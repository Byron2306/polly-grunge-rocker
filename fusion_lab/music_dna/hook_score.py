from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterator, Mapping, Sequence

from fusion_lab.model import NoteEvent


@dataclass(frozen=True, slots=True)
class HookScore(Mapping[str, float]):
    recurrence: float
    rhythmic_identity: float
    contour_recurrence: float
    rest_recurrence: float
    phrase_end_mutation: float
    loop_penalty: float
    total: float

    def to_dict(self) -> dict[str, float]:
        return {
            'recurrence': self.recurrence,
            'rhythmic_identity': self.rhythmic_identity,
            'contour_recurrence': self.contour_recurrence,
            'rest_recurrence': self.rest_recurrence,
            'phrase_end_mutation': self.phrase_end_mutation,
            'loop_penalty': self.loop_penalty,
            'total': self.total,
        }

    def __getitem__(self, key: str) -> float:
        return self.to_dict()[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.to_dict())

    def __len__(self) -> int:
        return 7


def _bar_signature(events: Sequence[NoteEvent], bar_start: int, bar_ticks: int) -> tuple[tuple[int, int, int], ...]:
    rows = []
    for event in events:
        if bar_start <= event.start_tick < bar_start + bar_ticks:
            rows.append((event.start_tick - bar_start, event.note, event.duration_ticks))
    return tuple(sorted(rows))


def _mode_recurrence(values: Sequence[tuple]) -> float:
    if not values:
        return 0.0
    return max(Counter(values).values()) / len(values)


def _contour(signature: tuple[tuple[int, int, int], ...]) -> tuple[int, ...]:
    notes = [row[1] for row in signature]
    return tuple(0 if b == a else (1 if b > a else -1) for a, b in zip(notes, notes[1:]))


def _rest_pattern(signature: tuple[tuple[int, int, int], ...], bar_ticks: int) -> tuple[int, ...]:
    if not signature:
        return (bar_ticks,)
    intervals = []
    cursor = 0
    for onset, _, duration in signature:
        if onset > cursor:
            intervals.append(onset - cursor)
        cursor = max(cursor, onset + duration)
    if cursor < bar_ticks:
        intervals.append(bar_ticks - cursor)
    return tuple(intervals)


def _phrase_end_mutation(signatures: Sequence[tuple]) -> float:
    """Measure diversity among four-bar phrase endings.

    The old implementation compared only the first and last bars of the
    entire song.  That made a deliberately evolved outro look maximally
    mutated even when the internal phrase endings had a healthy recurring
    vocabulary.  Thrash hooks typically keep a recognisable body while
    changing turnarounds, so score the ending bar of each four-bar phrase.
    """
    nonempty = tuple(sig for sig in signatures if sig)
    if len(nonempty) < 4:
        return 0.0

    phrase_ends = tuple(nonempty[i] for i in range(3, len(nonempty), 4))
    if len(phrase_ends) >= 2:
        most_common = max(Counter(phrase_ends).values())
        return 1.0 - most_common / len(phrase_ends)

    # Short fixture/song fallback: compare the final turnaround against the
    # dominant body bar.  A changed ending represents moderate, not maximal,
    # phrase mutation.
    body = nonempty[:-1]
    if not body:
        return 0.0
    reference = Counter(body).most_common(1)[0][0]
    return 0.5 if nonempty[-1] != reference else 0.0


def score_hook(
    events: Sequence[NoteEvent],
    ticks_per_beat: int,
    beats_per_bar: int = 4,
) -> HookScore:
    if ticks_per_beat <= 0:
        raise ValueError('ticks_per_beat must be > 0')
    if beats_per_bar <= 0:
        raise ValueError('beats_per_bar must be > 0')
    if not events:
        return HookScore(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    ordered = tuple(sorted(events, key=lambda e: (e.start_tick, e.note, e.duration_ticks)))
    bar_ticks = ticks_per_beat * beats_per_bar
    last_tick = max(e.start_tick for e in ordered)
    bars = max(1, last_tick // bar_ticks + 1)
    signatures = tuple(_bar_signature(ordered, i * bar_ticks, bar_ticks) for i in range(bars))
    nonempty = tuple(sig for sig in signatures if sig)
    counts = Counter(nonempty)
    max_repeat = max(counts.values()) if counts else 0
    recurrence = 0.0 if not nonempty else min(1.0, max_repeat / max(2, len(nonempty) / 2))

    onset_patterns = tuple(tuple(row[0] for row in sig) for sig in nonempty)
    rhythmic_identity = _mode_recurrence(onset_patterns)
    contour_recurrence = _mode_recurrence(tuple(_contour(sig) for sig in nonempty))
    rest_recurrence = _mode_recurrence(tuple(_rest_pattern(sig, bar_ticks) for sig in nonempty))
    phrase_end_mutation = _phrase_end_mutation(signatures)

    loop_penalty = 0.0
    if len(nonempty) >= 8 and len(counts) <= 2:
        loop_penalty = min(0.75, (len(nonempty) - len(counts)) / len(nonempty))

    total = max(
        0.0,
        min(
            1.0,
            0.30 * recurrence
            + 0.18 * rhythmic_identity
            + 0.12 * contour_recurrence
            + 0.10 * rest_recurrence
            + 0.30 * phrase_end_mutation
            - 0.60 * loop_penalty,
        ),
    )
    return HookScore(
        recurrence,
        rhythmic_identity,
        contour_recurrence,
        rest_recurrence,
        phrase_end_mutation,
        loop_penalty,
        total,
    )
