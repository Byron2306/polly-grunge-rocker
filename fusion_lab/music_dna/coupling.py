from __future__ import annotations

from typing import Iterable, Mapping

from fusion_lab.model import HostComposition, NoteEvent


def _onsets(events: Iterable[NoteEvent], *, note: int | None = None) -> tuple[int, ...]:
    ticks = {
        event.start_tick
        for event in events
        if note is None or event.note == note
    }
    return tuple(sorted(ticks))


def _coincidence_ratio(source: tuple[int, ...], target: tuple[int, ...], tolerance: int) -> float:
    if not source:
        return 0.0
    if not target:
        return 0.0
    hits = 0
    for tick in source:
        if any(abs(tick - other) <= tolerance for other in target):
            hits += 1
    return hits / len(source)


def extract_coupling_features(
    host: HostComposition,
    tolerance_ticks: int = 24,
) -> Mapping[str, float]:
    if tolerance_ticks < 0:
        raise ValueError('tolerance_ticks must be >= 0')

    guitar = _onsets(host.tracks['RHYTHM_GUITAR'].events)
    bass = _onsets(host.tracks['BASS'].events)
    kick = _onsets(host.tracks['DRUMS'].events, note=36)
    snare = _onsets(host.tracks['DRUMS'].events, note=38)

    return {
        'guitar_kick_coupling': _coincidence_ratio(guitar, kick, tolerance_ticks),
        'bass_guitar_lock_rate': _coincidence_ratio(bass, guitar, tolerance_ticks),
        'bass_kick_lock_rate': _coincidence_ratio(bass, kick, tolerance_ticks),
        'snare_guitar_accent_alignment': _coincidence_ratio(snare, guitar, tolerance_ticks),
    }
