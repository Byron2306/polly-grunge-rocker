from __future__ import annotations

from pathlib import Path
import statistics
import xml.etree.ElementTree as ET

import mido

from .corpus import CorpusObservation


_STEP_TO_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def _aggregate_pitches(
    pitches: list[int],
    durations: list[float],
    tempo_bpm: float,
    meter_numerator: int,
    meter_denominator: int,
    onset_deltas: list[float],
    rest_count: int = 0,
    event_count: int | None = None,
) -> dict[str, float]:
    intervals = [abs(b - a) for a, b in zip(pitches, pitches[1:])]
    chromatic = sum(1 for interval in intervals if interval in (1, 2)) / max(1, len(intervals))
    total_events = max(1, event_count if event_count is not None else len(pitches))
    return {
        'tempo_bpm': float(tempo_bpm),
        'meter_numerator': float(meter_numerator),
        'meter_denominator': float(meter_denominator),
        'pitch_range': float(max(pitches) - min(pitches)) if pitches else 0.0,
        'chromatic_step_ratio': chromatic,
        'mean_duration_units': float(statistics.fmean(durations)) if durations else 0.0,
        'mean_onset_delta_beats': float(statistics.fmean(onset_deltas)) if onset_deltas else 0.0,
        'rest_ratio': rest_count / total_events,
    }


def ingest_midi(path: Path, *, genre: str, artist: str, track: str) -> CorpusObservation:
    midi = mido.MidiFile(path)
    tempo_bpm = 120.0
    meter_numerator, meter_denominator = 4, 4
    pitches: list[int] = []
    durations: list[float] = []
    onset_ticks: list[int] = []
    active: dict[tuple[int, int], int] = {}

    for midi_track in midi.tracks:
        absolute = 0
        for message in midi_track:
            absolute += message.time
            if message.type == 'set_tempo':
                tempo_bpm = float(mido.tempo2bpm(message.tempo))
            elif message.type == 'time_signature':
                meter_numerator = int(message.numerator)
                meter_denominator = int(message.denominator)
            elif message.type == 'note_on' and message.velocity > 0:
                key = (message.channel, message.note)
                if key in active:
                    raise ValueError(f'MIDI_OVERLAPPING_NOTE_UNSUPPORTED: channel={message.channel} note={message.note}')
                active[key] = absolute
                pitches.append(message.note)
                onset_ticks.append(absolute)
            elif message.type in {'note_off', 'note_on'}:
                key = (getattr(message, 'channel', 0), getattr(message, 'note', -1))
                start = active.pop(key, None)
                if start is not None:
                    durations.append(max(0.0, float(absolute - start) / max(1, midi.ticks_per_beat)))
    if active:
        raise ValueError('MIDI_UNCLOSED_NOTE_UNSUPPORTED')

    unique_onsets = sorted(set(onset_ticks))
    onset_deltas = [
        (b - a) / max(1, midi.ticks_per_beat)
        for a, b in zip(unique_onsets, unique_onsets[1:])
        if b > a
    ]
    features = _aggregate_pitches(
        pitches,
        durations,
        tempo_bpm,
        meter_numerator,
        meter_denominator,
        onset_deltas,
        event_count=len(pitches),
    )
    features['event_count_normalized'] = min(1.0, len(pitches) / 512.0)
    return CorpusObservation(genre, artist, track, features, (f'midi:{Path(path).name}',))


def _xml_pitch(note: ET.Element) -> int | None:
    pitch = note.find('pitch')
    if pitch is None:
        return None
    step = pitch.findtext('step')
    octave = pitch.findtext('octave')
    if step not in _STEP_TO_PC or octave is None:
        raise ValueError('MUSICXML_UNSUPPORTED_PITCH')
    alter = int(pitch.findtext('alter', '0'))
    return (int(octave) + 1) * 12 + _STEP_TO_PC[step] + alter


def ingest_musicxml(path: Path, *, genre: str, artist: str, track: str) -> CorpusObservation:
    root = ET.parse(path).getroot()
    for tag in ('backup', 'forward', 'time-modification'):
        if any(True for _ in root.iter(tag)):
            raise ValueError(f'MUSICXML_UNSUPPORTED_CONSTRUCT: {tag}')

    tempo_bpm = 120.0
    meter_numerator, meter_denominator = 4, 4
    divisions = 1.0
    pitches: list[int] = []
    durations: list[float] = []
    onset_beats: list[float] = []
    cursor = 0.0
    rest_count = 0
    total_events = 0

    for sound in root.iter('sound'):
        tempo = sound.attrib.get('tempo')
        if tempo:
            tempo_bpm = float(tempo)
            break

    for attributes in root.iter('attributes'):
        raw_divisions = attributes.findtext('divisions')
        if raw_divisions is not None:
            divisions = float(raw_divisions)
            if divisions <= 0:
                raise ValueError('MUSICXML_INVALID_DIVISIONS')
        time = attributes.find('time')
        if time is not None:
            beats = time.findtext('beats')
            beat_type = time.findtext('beat-type')
            if beats is None or beat_type is None:
                raise ValueError('MUSICXML_INCOMPLETE_TIME_SIGNATURE')
            meter_numerator = int(beats)
            meter_denominator = int(beat_type)

    for note in root.iter('note'):
        if note.find('chord') is not None:
            raise ValueError('MUSICXML_UNSUPPORTED_CONSTRUCT: chord')
        duration_text = note.findtext('duration')
        if duration_text is None:
            raise ValueError('MUSICXML_NOTE_DURATION_REQUIRED')
        duration_beats = float(duration_text) / divisions
        if duration_beats <= 0:
            raise ValueError('MUSICXML_NOTE_DURATION_INVALID')
        total_events += 1
        onset_beats.append(cursor)
        if note.find('rest') is not None:
            rest_count += 1
        else:
            midi_note = _xml_pitch(note)
            if midi_note is None:
                raise ValueError('MUSICXML_NOTE_PITCH_REQUIRED')
            pitches.append(midi_note)
        durations.append(duration_beats)
        cursor += duration_beats

    unique_onsets = sorted(set(onset_beats))
    onset_deltas = [b - a for a, b in zip(unique_onsets, unique_onsets[1:]) if b > a]
    features = _aggregate_pitches(
        pitches,
        durations,
        tempo_bpm,
        meter_numerator,
        meter_denominator,
        onset_deltas,
        rest_count=rest_count,
        event_count=total_events,
    )
    features['event_count_normalized'] = min(1.0, total_events / 512.0)
    return CorpusObservation(genre, artist, track, features, (f'musicxml:{Path(path).name}',))
