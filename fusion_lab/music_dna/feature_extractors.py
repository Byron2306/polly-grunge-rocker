from __future__ import annotations

from collections import Counter
from typing import Mapping

from fusion_lab.model import HostComposition, NoteEvent

from .model import FeatureVector


def _track(host: HostComposition, role: str) -> tuple[NoteEvent, ...]:
    return tuple(host.tracks[role].events)


def _song_ticks(host: HostComposition) -> int:
    if not host.sections:
        return host.ticks_per_beat * host.numerator
    end_bar = max(section.end_bar for section in host.sections)
    return max(1, end_bar * host.numerator * host.ticks_per_beat)


def _attack_density(events: tuple[NoteEvent, ...], song_ticks: int, tpq: int) -> float:
    if not events:
        return 0.0
    beats = max(1.0, song_ticks / tpq)
    return min(1.0, len({e.start_tick for e in events}) / beats)


def _ratio(events: tuple[NoteEvent, ...], predicate) -> float:
    if not events:
        return 0.0
    return sum(1 for e in events if predicate(e)) / len(events)


def _sustain_ratio(events: tuple[NoteEvent, ...], tpq: int) -> float:
    if not events:
        return 0.0
    long = sum(1 for e in events if e.duration_ticks >= tpq)
    return long / len(events)


def _pedal_note_ratio(events: tuple[NoteEvent, ...]) -> float:
    if not events:
        return 0.0
    counts = Counter(e.note for e in events)
    return max(counts.values()) / len(events)


def _chromaticity(events: tuple[NoteEvent, ...]) -> float:
    ordered = sorted(events, key=lambda e: (e.start_tick, e.note))
    if len(ordered) < 2:
        return 0.0
    intervals = [abs(b.note - a.note) for a, b in zip(ordered, ordered[1:])]
    return sum(1 for interval in intervals if interval in (1, 2, 6)) / len(intervals)


def extract_role_features(host: HostComposition, role: str) -> Mapping[str, float]:
    events = _track(host, role)
    song_ticks = _song_ticks(host)
    tpq = host.ticks_per_beat
    if role == 'RHYTHM_GUITAR':
        return {
            'attack_density': _attack_density(events, song_ticks, tpq),
            'palm_mute_ratio': _ratio(events, lambda e: bool(e.articulation and 'PALM_MUTE' in e.articulation)),
            'tremolo_ratio': _ratio(events, lambda e: bool(e.articulation and 'TREMOLO' in e.articulation)),
            'downpick_ratio': _ratio(events, lambda e: bool(e.articulation and 'DOWNPICK' in e.articulation)),
            'gallop_rate': _ratio(events, lambda e: bool(e.articulation and 'GALLOP' in e.articulation)),
            'sustain_ratio': _sustain_ratio(events, tpq),
        }
    if role == 'BASS':
        return {
            'attack_density': _attack_density(events, song_ticks, tpq),
            'sustain_ratio': _sustain_ratio(events, tpq),
            'fill_probability': _ratio(events, lambda e: bool(e.function and 'FILL' in e.function)),
        }
    if role == 'DRUMS':
        return {
            'attack_density': _attack_density(events, song_ticks, tpq),
            'blast_probability': _ratio(events, lambda e: bool(e.articulation and 'BLAST' in e.articulation)),
            'double_kick_density': _ratio(events, lambda e: bool(e.articulation and 'DOUBLE_KICK' in e.articulation)),
            'skank_probability': _ratio(events, lambda e: bool(e.articulation and 'SKANK' in e.articulation)),
        }
    return {
        'attack_density': _attack_density(events, song_ticks, tpq),
        'sustain_ratio': _sustain_ratio(events, tpq),
    }


def extract_harmony_features(host: HostComposition) -> Mapping[str, float]:
    guitar = _track(host, 'RHYTHM_GUITAR')
    ordered = sorted(guitar, key=lambda e: (e.start_tick, e.note))
    intervals = [abs(b.note - a.note) % 12 for a, b in zip(ordered, ordered[1:])]
    denominator = max(1, len(intervals))
    return {
        'pedal_note_ratio': _pedal_note_ratio(guitar),
        'chromaticity': _chromaticity(guitar),
        'minor_second_rate': sum(1 for interval in intervals if interval in (1, 11)) / denominator,
        'minor_third_rate': sum(1 for interval in intervals if interval in (3, 9)) / denominator,
        'tritone_rate': sum(1 for interval in intervals if interval == 6) / denominator,
        'perfect_fifth_rate': sum(1 for interval in intervals if interval in (5, 7)) / denominator,
    }


def extract_arrangement_features(host: HostComposition) -> Mapping[str, float]:
    bars = [section.bars for section in host.sections]
    section_count = len(host.sections)
    return {
        'section_count_normalized': min(1.0, section_count / 12.0),
        'mean_section_length_bars_normalized': min(1.0, (sum(bars) / max(1, len(bars))) / 16.0),
        'odd_meter_probability': 0.0 if host.numerator == 4 and host.denominator == 4 else 1.0,
    }


def extract_host_features(host: HostComposition) -> FeatureVector:
    values: dict[str, float] = {}
    for prefix, role in (
        ('guitar', 'RHYTHM_GUITAR'),
        ('bass', 'BASS'),
        ('drums', 'DRUMS'),
        ('lead', 'LEAD_KEYS'),
        ('vocals', 'VOCALS'),
    ):
        for name, value in extract_role_features(host, role).items():
            values[f'{prefix}.{name}'] = value
    for name, value in extract_harmony_features(host).items():
        values[f'harmony.{name}'] = value
    for name, value in extract_arrangement_features(host).items():
        values[f'arrangement.{name}'] = value
    values['tempo_bpm'] = float(host.bpm)
    return FeatureVector(values)
