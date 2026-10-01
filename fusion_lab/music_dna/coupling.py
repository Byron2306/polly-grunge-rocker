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
    if not source or not target:
        return 0.0
    hits = sum(1 for tick in source if any(abs(tick - other) <= tolerance for other in target))
    return hits / len(source)


def _section_density_contrast(host: HostComposition) -> float:
    if not host.sections:
        return 0.0
    bar_ticks = host.numerator * host.ticks_per_beat
    role_events = tuple(
        event
        for role in ('RHYTHM_GUITAR', 'BASS', 'DRUMS', 'LEAD_KEYS', 'VOCALS')
        for event in host.tracks[role].events
    )
    densities: list[float] = []
    for section in host.sections:
        start = section.start_bar * bar_ticks
        end = section.end_bar * bar_ticks
        onsets = {event.start_tick for event in role_events if start <= event.start_tick < end}
        beats = max(1, section.bars * host.numerator)
        densities.append(len(onsets) / beats)
    if not densities:
        return 0.0
    high = max(densities)
    low = min(densities)
    return 0.0 if high == 0 else min(1.0, (high - low) / high)


def extract_coupling_features(
    host: HostComposition,
    tolerance_ticks: int = 30,
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
        'section_density_contrast': _section_density_contrast(host),
    }
