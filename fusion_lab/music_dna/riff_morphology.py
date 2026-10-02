from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from fusion_lab.model import HostComposition, NoteEvent


class Gesture(str, Enum):
    UNKNOWN = 'UNKNOWN'
    STOMP = 'STOMP'
    SPRINT = 'SPRINT'
    PANIC = 'PANIC'
    HOOK = 'HOOK'
    TRANSITION = 'TRANSITION'
    TRANCE = 'TRANCE'


@dataclass(frozen=True, slots=True)
class RiffSignature:
    pedal_anchor: int | None
    pitch_contour: tuple[int, ...]
    onset_pattern: tuple[int, ...]
    rest_pattern: tuple[int, ...]
    accent_pattern: tuple[str, ...]
    articulation_pattern: tuple[str, ...]
    density: float
    cadence_shape: str


@dataclass(frozen=True, slots=True)
class RiffFamily:
    id: str
    signature: RiffSignature
    bar_indices: tuple[int, ...]
    gesture: Gesture = Gesture.UNKNOWN


@dataclass(frozen=True, slots=True)
class RiffMorphologyReport:
    families: tuple[RiffFamily, ...]
    family_by_bar: tuple[str | None, ...]
    gesture_by_bar: tuple[Gesture, ...]
    riff_family_count: int
    riff_family_recurrence: float
    longest_same_family_run_bars: int
    section_riff_contrast: float
    transition_density: float
    gesture_diversity: int
    gesture_metadata_present: bool

    def metrics(self) -> dict[str, float]:
        return {
            'riff_family_count': float(self.riff_family_count),
            'riff_family_recurrence': self.riff_family_recurrence,
            'longest_same_family_run_bars': float(self.longest_same_family_run_bars),
            'section_riff_contrast': self.section_riff_contrast,
            'transition_density': self.transition_density,
            'gesture_diversity': float(self.gesture_diversity),
        }

    def to_dict(self) -> dict[str, object]:
        return {
            **self.metrics(),
            'gesture_metadata_present': self.gesture_metadata_present,
            'family_by_bar': list(self.family_by_bar),
            'gesture_by_bar': [gesture.value for gesture in self.gesture_by_bar],
            'families': [
                {'id': family.id, 'bar_indices': list(family.bar_indices), 'gesture': family.gesture.value}
                for family in self.families
            ],
        }


def _onset_groups(events: Sequence[NoteEvent], bar_start: int, bar_ticks: int) -> list[tuple[int, tuple[NoteEvent, ...]]]:
    by_tick: dict[int, list[NoteEvent]] = {}
    end = bar_start + bar_ticks
    for event in events:
        if bar_start <= event.start_tick < end:
            by_tick.setdefault(event.start_tick, []).append(event)
    return [(tick, tuple(sorted(rows, key=lambda event: (event.note, event.duration_ticks)))) for tick, rows in sorted(by_tick.items())]


def _semantic_articulation(raw: str | None) -> str:
    value = (raw or 'SUSTAIN').upper()
    if 'GALLOP' in value:
        return 'GALLOP'
    if 'CHROMATIC' in value:
        return 'CHROMATIC'
    if 'DOWNPICK' in value:
        return 'DOWNPICK'
    if 'OPEN' in value or 'RELEASE' in value:
        return 'RELEASE'
    if 'TREMOLO' in value:
        return 'TREMOLO'
    return value


def _accent_bucket(velocity: int) -> str:
    if velocity >= 114:
        return 'HIGH'
    if velocity >= 100:
        return 'MEDIUM'
    return 'LOW'


def _scaled(value: int, bar_ticks: int) -> int:
    return round((value / max(1, bar_ticks)) * 1000)


def signature_for_bar(events: Sequence[NoteEvent], bar_start: int, bar_ticks: int) -> RiffSignature:
    groups = _onset_groups(events, bar_start, bar_ticks)
    if not groups:
        return RiffSignature(None, (), (), (1000,), (), (), 0.0, 'empty')

    roots = [min(event.note for event in rows) for _, rows in groups]
    anchor = roots[0]
    pitch_contour = tuple(root - anchor for root in roots)
    onset_pattern = tuple(_scaled(tick - bar_start, bar_ticks) for tick, _ in groups)

    rests: list[int] = []
    cursor = bar_start
    for tick, rows in groups:
        if tick > cursor:
            rests.append(_scaled(tick - cursor, bar_ticks))
        sounding_end = max(event.start_tick + event.duration_ticks for event in rows)
        cursor = max(cursor, sounding_end)
    if cursor < bar_start + bar_ticks:
        rests.append(_scaled(bar_start + bar_ticks - cursor, bar_ticks))

    accents = tuple(_accent_bucket(max(event.velocity for event in rows)) for _, rows in groups)
    articulations = tuple(_semantic_articulation(rows[0].articulation) for _, rows in groups)
    density = min(1.0, len(groups) / 16.0)

    final_quarter = bar_start + (bar_ticks * 3 // 4)
    final_groups = [(tick, rows) for tick, rows in groups if tick >= final_quarter]
    if final_groups:
        final_art = _semantic_articulation(final_groups[-1][1][0].articulation)
        if final_art == 'RELEASE':
            cadence = 'release'
        elif final_art == 'CHROMATIC' or len({min(e.note for e in rows) for _, rows in final_groups}) > 1:
            cadence = 'chromatic'
        else:
            cadence = 'held'
    elif any(event.start_tick < final_quarter < event.start_tick + event.duration_ticks for event in events):
        cadence = 'held'
    else:
        cadence = 'empty'

    counts = Counter(root % 12 for root in roots)
    pedal_anchor = counts.most_common(1)[0][0]
    return RiffSignature(pedal_anchor, pitch_contour, onset_pattern, tuple(rests), accents, articulations, density, cadence)


def _sequence_similarity(a: tuple, b: tuple) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    shared = sum(1 for left, right in zip(a, b) if left == right)
    return shared / max(len(a), len(b))


def _signature_similarity(a: RiffSignature, b: RiffSignature) -> float:
    onset = _sequence_similarity(a.onset_pattern, b.onset_pattern)
    rests = _sequence_similarity(a.rest_pattern, b.rest_pattern)
    articulation = _sequence_similarity(a.articulation_pattern, b.articulation_pattern)
    contour = _sequence_similarity(a.pitch_contour, b.pitch_contour)
    cadence = 1.0 if a.cadence_shape == b.cadence_shape else 0.0
    density = max(0.0, 1.0 - abs(a.density - b.density) * 2.0)
    return 0.30 * onset + 0.14 * rests + 0.14 * articulation + 0.12 * contour + 0.20 * cadence + 0.10 * density


def _coerce_gesture(value: Gesture | str | None) -> Gesture:
    if value is None:
        return Gesture.UNKNOWN
    if isinstance(value, Gesture):
        return value
    return Gesture(str(value).upper())


def _embedded_gestures(rhythm: Sequence[NoteEvent], bar_ticks: int, end_bar: int) -> dict[int, Gesture]:
    result: dict[int, Gesture] = {}
    for bar in range(end_bar):
        start = bar * bar_ticks
        end = start + bar_ticks
        labels = []
        for event in rhythm:
            if start <= event.start_tick < end and event.function and event.function.startswith('RIFF_'):
                labels.append(event.function.removeprefix('RIFF_'))
        if labels:
            label = Counter(labels).most_common(1)[0][0]
            try:
                result[bar] = Gesture(label)
            except ValueError:
                result[bar] = Gesture.UNKNOWN
    return result


def _section_contrast(host: HostComposition, family_by_bar: Sequence[str | None]) -> float:
    if len(host.sections) < 2:
        return 0.0
    contrasts: list[float] = []
    for left, right in zip(host.sections, host.sections[1:]):
        left_set = {family for family in family_by_bar[left.start_bar:left.end_bar] if family is not None}
        right_set = {family for family in family_by_bar[right.start_bar:right.end_bar] if family is not None}
        union = left_set | right_set
        contrasts.append(0.0 if not union else 1.0 - len(left_set & right_set) / len(union))
    return sum(contrasts) / len(contrasts)


def analyze_riff_morphology(host: HostComposition, explicit_gestures: Mapping[int, Gesture | str] | None = None) -> RiffMorphologyReport:
    rhythm = tuple(host.tracks['RHYTHM_GUITAR'].events)
    end_bar = max((section.end_bar for section in host.sections), default=0)
    bar_ticks = host.ticks_per_beat * host.numerator
    signatures = [signature_for_bar(rhythm, bar * bar_ticks, bar_ticks) for bar in range(end_bar)]

    representatives: list[RiffSignature] = []
    bars_by_family: list[list[int]] = []
    family_by_bar: list[str | None] = []
    threshold = 0.74
    for bar, signature in enumerate(signatures):
        if not signature.onset_pattern:
            family_by_bar.append(None)
            continue
        match = None
        best_score = threshold
        for index, representative in enumerate(representatives):
            score = _signature_similarity(signature, representative)
            if score >= best_score:
                best_score = score
                match = index
        if match is None:
            match = len(representatives)
            representatives.append(signature)
            bars_by_family.append([])
        bars_by_family[match].append(bar)
        family_by_bar.append(f'RF{match + 1}')

    embedded = _embedded_gestures(rhythm, bar_ticks, end_bar)
    gesture_source: Mapping[int, Gesture | str] = explicit_gestures if explicit_gestures is not None else embedded
    gesture_by_bar = tuple(
        _coerce_gesture(gesture_source.get(bar)) if family_by_bar[bar] is not None else Gesture.UNKNOWN
        for bar in range(end_bar)
    )

    families: list[RiffFamily] = []
    for index, representative in enumerate(representatives):
        bar_indices = tuple(bars_by_family[index])
        gestures = [gesture_by_bar[bar] for bar in bar_indices if gesture_by_bar[bar] != Gesture.UNKNOWN]
        family_gesture = Counter(gestures).most_common(1)[0][0] if gestures else Gesture.UNKNOWN
        families.append(RiffFamily(f'RF{index + 1}', representative, bar_indices, family_gesture))

    populated = [family for family in family_by_bar if family is not None]
    recurrence = max(Counter(populated).values()) / len(populated) if populated else 0.0
    longest = 0
    current = 0
    previous: str | None = None
    for family in family_by_bar:
        if family is not None and family == previous:
            current += 1
        elif family is not None:
            current = 1
        else:
            current = 0
        previous = family
        longest = max(longest, current)

    transition_bars = sum(1 for gesture in gesture_by_bar if gesture == Gesture.TRANSITION)
    populated_bar_count = max(1, len(populated))
    non_unknown = {gesture for gesture in gesture_by_bar if gesture != Gesture.UNKNOWN}
    return RiffMorphologyReport(
        tuple(families),
        tuple(family_by_bar),
        gesture_by_bar,
        len(families),
        recurrence,
        longest,
        _section_contrast(host, family_by_bar),
        transition_bars / populated_bar_count,
        len(non_unknown),
        bool(non_unknown),
    )
