from __future__ import annotations

from dataclasses import dataclass

from fusion_lab.model import NoteEvent


def _probability(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f'{name} must be within 0..1')


@dataclass(frozen=True, slots=True)
class GuitarPerformanceEvent:
    start_tick: int
    duration_ticks: int
    midi_note: int
    velocity: int
    string: int | None
    fret: int | None
    pick_direction: str | None
    palm_mute: float
    accent: float
    technique: str
    chord_shape: str | None
    phrase_role: str

    def __post_init__(self) -> None:
        _probability('palm_mute', self.palm_mute)
        _probability('accent', self.accent)
        if self.string is not None and not 1 <= self.string <= 8:
            raise ValueError('string must be 1..8')
        if self.fret is not None and not 0 <= self.fret <= 36:
            raise ValueError('fret must be 0..36')


@dataclass(frozen=True, slots=True)
class BassPerformanceEvent:
    start_tick: int
    duration_ticks: int
    midi_note: int
    velocity: int
    technique: str
    lock_target: str | None
    phrase_role: str


@dataclass(frozen=True, slots=True)
class DrumPerformanceEvent:
    start_tick: int
    duration_ticks: int
    midi_note: int
    velocity: int
    limb: str | None
    technique: str
    groove_role: str
    accent: float

    def __post_init__(self) -> None:
        _probability('accent', self.accent)


@dataclass(frozen=True, slots=True)
class VocalPerformanceEvent:
    start_tick: int
    duration_ticks: int
    pitch: int | None
    syllabic_density: float
    delivery: str
    phrase_role: str

    def __post_init__(self) -> None:
        _probability('syllabic_density', self.syllabic_density)


@dataclass(frozen=True, slots=True)
class KeyPerformanceEvent:
    start_tick: int
    duration_ticks: int
    midi_note: int
    velocity: int
    voicing_role: str
    articulation: str


def to_note_event(event, channel: int, fallback_note: int = 60) -> NoteEvent:
    if isinstance(event, GuitarPerformanceEvent):
        return NoteEvent(event.start_tick, event.duration_ticks, event.midi_note, event.velocity, channel, event.technique, event.phrase_role)
    if isinstance(event, BassPerformanceEvent):
        return NoteEvent(event.start_tick, event.duration_ticks, event.midi_note, event.velocity, channel, event.technique, event.phrase_role)
    if isinstance(event, DrumPerformanceEvent):
        return NoteEvent(event.start_tick, event.duration_ticks, event.midi_note, event.velocity, channel, event.technique, event.groove_role)
    if isinstance(event, KeyPerformanceEvent):
        return NoteEvent(event.start_tick, event.duration_ticks, event.midi_note, event.velocity, channel, event.articulation, event.voicing_role)
    if isinstance(event, VocalPerformanceEvent):
        note = fallback_note if event.pitch is None else event.pitch
        return NoteEvent(event.start_tick, event.duration_ticks, note, max(1, min(127, int(64 + 63 * event.syllabic_density))), channel, event.delivery, event.phrase_role)
    raise TypeError(f'unsupported performance event: {type(event).__name__}')
