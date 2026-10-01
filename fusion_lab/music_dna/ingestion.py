from __future__ import annotations

from collections import Counter
from pathlib import Path
import statistics
import xml.etree.ElementTree as ET

import mido

from .corpus import CorpusObservation


_STEP_TO_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def _aggregate_pitches(pitches: list[int], durations: list[float], tempo_bpm: float) -> dict[str, float]:
    if not pitches:
        return {'tempo_bpm': float(tempo_bpm), 'pitch_range': 0.0, 'chromatic_step_ratio': 0.0, 'mean_duration_units': 0.0}
    intervals = [abs(b - a) for a, b in zip(pitches, pitches[1:])]
    chromatic = sum(1 for interval in intervals if interval in (1, 2)) / max(1, len(intervals))
    return {
        'tempo_bpm': float(tempo_bpm),
        'pitch_range': float(max(pitches) - min(pitches)),
        'chromatic_step_ratio': chromatic,
        'mean_duration_units': float(statistics.fmean(durations)) if durations else 0.0,
    }


def ingest_midi(path: Path, *, genre: str, artist: str, track: str) -> CorpusObservation:
    midi = mido.MidiFile(path)
    tempo_bpm = 120.0
    pitches: list[int] = []
    durations: list[float] = []
    active: dict[tuple[int, int], int] = {}
    absolute = 0
    for midi_track in midi.tracks:
        absolute = 0
        for message in midi_track:
            absolute += message.time
            if message.type == 'set_tempo':
                tempo_bpm = float(mido.tempo2bpm(message.tempo))
            elif message.type == 'note_on' and message.velocity > 0:
                active[(message.channel, message.note)] = absolute
                pitches.append(message.note)
            elif message.type in {'note_off', 'note_on'}:
                key = (getattr(message, 'channel', 0), getattr(message, 'note', -1))
                start = active.pop(key, None)
                if start is not None:
                    durations.append(max(0.0, float(absolute - start) / max(1, midi.ticks_per_beat)))
    features = _aggregate_pitches(pitches, durations, tempo_bpm)
    features['event_count_normalized'] = min(1.0, len(pitches) / 512.0)
    return CorpusObservation(genre, artist, track, features, (f'midi:{Path(path).name}',))


def _xml_pitch(note: ET.Element) -> int | None:
    pitch = note.find('pitch')
    if pitch is None:
        return None
    step = pitch.findtext('step')
    octave = pitch.findtext('octave')
    if step not in _STEP_TO_PC or octave is None:
        return None
    alter = int(pitch.findtext('alter', '0'))
    return (int(octave) + 1) * 12 + _STEP_TO_PC[step] + alter


def ingest_musicxml(path: Path, *, genre: str, artist: str, track: str) -> CorpusObservation:
    root = ET.parse(path).getroot()
    tempo_bpm = 120.0
    pitches: list[int] = []
    durations: list[float] = []
    for sound in root.iter('sound'):
        tempo = sound.attrib.get('tempo')
        if tempo:
            tempo_bpm = float(tempo)
            break
    for note in root.iter('note'):
        midi_note = _xml_pitch(note)
        if midi_note is not None:
            pitches.append(midi_note)
        duration = note.findtext('duration')
        if duration is not None:
            durations.append(float(duration))
    features = _aggregate_pitches(pitches, durations, tempo_bpm)
    features['event_count_normalized'] = min(1.0, len(pitches) / 512.0)
    return CorpusObservation(genre, artist, track, features, (f'musicxml:{Path(path).name}',))
