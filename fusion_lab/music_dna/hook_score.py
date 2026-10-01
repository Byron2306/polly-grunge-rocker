from __future__ import annotations

from collections import Counter
from typing import Mapping, Sequence

from fusion_lab.model import NoteEvent


def _bar_signature(events: Sequence[NoteEvent], bar_start: int, bar_ticks: int) -> tuple[tuple[int, int, int], ...]:
    rows = []
    for event in events:
        if bar_start <= event.start_tick < bar_start + bar_ticks:
            rows.append((event.start_tick - bar_start, event.note, event.duration_ticks))
    return tuple(sorted(rows))


def score_hook(events: Sequence[NoteEvent], ticks_per_beat: int) -> Mapping[str, float]:
    if ticks_per_beat <= 0:
        raise ValueError('ticks_per_beat must be > 0')
    if not events:
        return {
            'recurrence': 0.0,
            'rhythmic_identity': 0.0,
            'phrase_end_mutation': 0.0,
            'loop_penalty': 0.0,
            'total': 0.0,
        }

    ordered = tuple(sorted(events, key=lambda e: (e.start_tick, e.note, e.duration_ticks)))
    bar_ticks = ticks_per_beat * 4
    last_tick = max(e.start_tick for e in ordered)
    bars = max(1, last_tick // bar_ticks + 1)
    signatures = tuple(_bar_signature(ordered, i * bar_ticks, bar_ticks) for i in range(bars))
    nonempty = tuple(sig for sig in signatures if sig)
    counts = Counter(nonempty)
    max_repeat = max(counts.values()) if counts else 0
    recurrence = 0.0 if not nonempty else min(1.0, max_repeat / max(2, len(nonempty) / 2))

    onset_patterns = []
    for sig in nonempty:
        onset_patterns.append(tuple(row[0] for row in sig))
    rhythmic_identity = 0.0
    if onset_patterns:
        rhythmic_identity = max(Counter(onset_patterns).values()) / len(onset_patterns)

    phrase_end_mutation = 0.0
    if len(nonempty) >= 4:
        base = nonempty[0]
        end = nonempty[-1]
        if base != end:
            shared_onsets = {x[0] for x in base} & {x[0] for x in end}
            if shared_onsets:
                phrase_end_mutation = min(1.0, len(shared_onsets) / max(1, len({x[0] for x in base})))

    loop_penalty = 0.0
    if len(nonempty) >= 8 and len(counts) <= 2:
        loop_penalty = min(0.75, (len(nonempty) - len(counts)) / len(nonempty))

    total = max(
        0.0,
        min(
            1.0,
            0.45 * recurrence
            + 0.25 * rhythmic_identity
            + 0.30 * phrase_end_mutation
            - 0.60 * loop_penalty,
        ),
    )
    return {
        'recurrence': recurrence,
        'rhythmic_identity': rhythmic_identity,
        'phrase_end_mutation': phrase_end_mutation,
        'loop_penalty': loop_penalty,
        'total': total,
    }
