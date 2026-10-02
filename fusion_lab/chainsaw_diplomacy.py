from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .model import HostComposition, NoteEvent, RoleTrack, Section
from .music_dna.riff_morphology import Gesture

TPQ = 480
FORM_BARS = (4, 8, 4, 8, 8, 8, 8, 4, 8, 4)
SECTION_IDS = ('intro', 'verse1', 'pre', 'chorus1', 'verse2', 'chorus2', 'solo', 'bridge', 'final_chorus', 'outro')
BAR_TICKS = 4 * TPQ


@dataclass(frozen=True, slots=True)
class ArticulationEvent:
    role_layer: str
    start_tick: int
    end_tick: int
    articulation: str


@dataclass(frozen=True, slots=True)
class VocalWindow:
    id: str
    section_id: str
    start_tick: int
    end_tick: int
    kind: str


@dataclass(frozen=True, slots=True)
class RiffBarPlan:
    bar_index: int
    section_id: str
    family_id: str
    gesture: Gesture


def _sections() -> tuple[Section, ...]:
    out = []
    bar = 0
    for sid, bars in zip(SECTION_IDS, FORM_BARS):
        out.append(Section(sid, bar, bars))
        bar += bars
    return tuple(out)


_SECTION_FAMILIES = {
    'intro': ('A_HOOK', 'A_HOOK', 'A_HOOK', 'E_TRANSITION'),
    'verse1': ('A_HOOK', 'A_HOOK', 'B_SPRINT', 'B_SPRINT', 'A_HOOK', 'A_HOOK', 'B_SPRINT', 'B_SPRINT'),
    'pre': ('D_PANIC',) * 2 + ('B_SPRINT',) * 2,
    'chorus1': ('A_HOOK',) * 4 + ('C_STOMP',) * 4,
    'verse2': ('B_SPRINT',) * 4 + ('D_PANIC',) * 4,
    'chorus2': ('A_HOOK',) * 4 + ('C_STOMP',) * 4,
    'solo': ('B_SPRINT',) * 2 + ('D_PANIC',) * 2 + ('B_SPRINT',) * 2 + ('D_PANIC',) * 2,
    'bridge': ('C_STOMP',) * 2 + ('E_TRANSITION',) * 2,
    'final_chorus': ('A_HOOK',) * 2 + ('B_SPRINT',) * 3 + ('C_STOMP',) * 3,
    'outro': ('D_PANIC',) * 2 + ('E_TRANSITION',) * 2,
}

_FAMILY_GESTURES = {
    'A_HOOK': Gesture.HOOK,
    'B_SPRINT': Gesture.SPRINT,
    'C_STOMP': Gesture.STOMP,
    'D_PANIC': Gesture.PANIC,
    'E_TRANSITION': Gesture.TRANSITION,
}


def chainsaw_riff_schedule() -> tuple[RiffBarPlan, ...]:
    rows = []
    for section in _sections():
        families = _SECTION_FAMILIES[section.id]
        if len(families) != section.bars:
            raise RuntimeError(f'CHAINSAW_RIFF_SCHEDULE_LENGTH: {section.id}')
        for offset, family_id in enumerate(families):
            rows.append(RiffBarPlan(section.start_bar + offset, section.id, family_id, _FAMILY_GESTURES[family_id]))
    return tuple(rows)


def _root5(root: int, start: int, dur: int, velocity: int, articulation: str, gesture: Gesture):
    function = f'RIFF_{gesture.value}'
    return (
        NoteEvent(start, dur, root, velocity, 2, articulation, function),
        NoteEvent(start, dur, root + 7, velocity, 2, articulation, function),
    )


def _riff_a_hook(base: int, *, prime: bool = False):
    g = Gesture.HOOK
    upper = 42 if prime else 41
    rows = []
    for tick, root, dur, vel, art in (
        (0, 40, 170, 108, 'PALM_MUTE_DOWNPICK'),
        (240, 40, 170, 103, 'PALM_MUTE_DOWNPICK'),
        (480, 46, 220, 116, 'CHROMATIC_POWER'),
        (720, 40, 170, 106, 'PALM_MUTE_DOWNPICK'),
        (960, upper, 220, 114, 'CHROMATIC_POWER'),
        (1200, 40, 170, 106, 'PALM_MUTE_DOWNPICK'),
        (1440, 46, 180, 118, 'CHROMATIC_POWER'),
        (1680, 47, 220, 122, 'OPEN_RELEASE'),
    ):
        rows.extend(_root5(root, base + tick, dur, vel, art, g))
    return rows


def _riff_b_sprint(base: int):
    g = Gesture.SPRINT
    rows = []
    for beat in range(4):
        tick = base + beat * TPQ
        root = 40 if beat < 3 else 42
        rows.extend(_root5(root, tick, 100, 112, 'PALM_MUTE_DOWNPICK', g))
        rows.extend(_root5(root, tick + TPQ // 4, 90, 108, 'PALM_MUTE_GALLOP_DOWNPICK', g))
        rows.extend(_root5(root, tick + TPQ // 2, 90, 105, 'PALM_MUTE_GALLOP', g))
        rows.extend(_root5(root, tick + 3 * TPQ // 4, 90, 109, 'PALM_MUTE_DOWNPICK', g))
    return rows


def _riff_c_stomp(base: int, *, prime: bool = False):
    g = Gesture.STOMP
    landing = 43 if prime else 41
    rows = []
    for tick, root, dur, vel, art in (
        (0, 40, 360, 120, 'OPEN_RELEASE'),
        (720, 43, 260, 124, 'CHROMATIC_POWER'),
        (1200, landing, 300, 122, 'CHROMATIC_POWER'),
        (1680, 46, 220, 127, 'OPEN_RELEASE'),
    ):
        rows.extend(_root5(root, base + tick, dur, vel, art, g))
    return rows


def _riff_d_panic(base: int):
    g = Gesture.PANIC
    rows = []
    roots = (40, 41, 46, 42, 47, 41, 43, 40)
    for index, root in enumerate(roots):
        art = 'PALM_MUTE_DOWNPICK' if index in (0, 3, 7) else 'CHROMATIC_POWER_DOWNPICK'
        rows.extend(_root5(root, base + index * TPQ // 2, TPQ // 3, 110 + (index % 3) * 4, art, g))
    return rows


def _riff_e_transition(base: int):
    g = Gesture.TRANSITION
    rows = []
    for tick, root, vel, art in (
        (0, 40, 112, 'PALM_MUTE_DOWNPICK'),
        (480, 46, 120, 'CHROMATIC_POWER'),
        (960, 47, 122, 'CHROMATIC_POWER'),
        (1320, 43, 118, 'CHROMATIC_POWER'),
        (1560, 41, 120, 'CHROMATIC_POWER'),
        (1800, 40, 127, 'OPEN_RELEASE'),
    ):
        rows.extend(_root5(root, base + tick, TPQ // 3, vel, art, g))
    return rows


def _compose_riff(plan: RiffBarPlan):
    base = plan.bar_index * BAR_TICKS
    if plan.family_id == 'A_HOOK':
        return _riff_a_hook(base, prime='chorus' in plan.section_id or plan.section_id == 'final_chorus')
    if plan.family_id == 'B_SPRINT':
        return _riff_b_sprint(base)
    if plan.family_id == 'C_STOMP':
        return _riff_c_stomp(base, prime=plan.section_id in {'chorus2', 'final_chorus'})
    if plan.family_id == 'D_PANIC':
        return _riff_d_panic(base)
    if plan.family_id == 'E_TRANSITION':
        return _riff_e_transition(base)
    raise RuntimeError(f'CHAINSAW_UNKNOWN_RIFF_FAMILY: {plan.family_id}')


def _rhythm(schedule: tuple[RiffBarPlan, ...]):
    events = []
    for plan in schedule:
        events.extend(_compose_riff(plan))
    return tuple(sorted(events, key=lambda e: (e.start_tick, e.note, e.duration_ticks)))


def _family_boundaries(schedule: tuple[RiffBarPlan, ...]) -> set[int]:
    return {
        current.bar_index
        for previous, current in zip(schedule, schedule[1:])
        if previous.family_id != current.family_id
    }


def _bass(schedule: tuple[RiffBarPlan, ...], rhythm):
    events = []
    by_tick = {}
    for event in rhythm:
        by_tick.setdefault(event.start_tick, []).append(event)
    for tick, items in sorted(by_tick.items()):
        root = min(item.note for item in items)
        vel = 104 if any(item.articulation and 'DOWNPICK' in item.articulation for item in items) else 100
        events.append(NoteEvent(tick, items[0].duration_ticks, max(28, root - 12), vel, 1, 'PICKED_FOLLOW', 'GROOVE_ANCHOR'))

    fill_notes = (28, 31, 34, 35, 34, 28)
    boundaries = _family_boundaries(schedule)
    for boundary_bar in sorted(boundaries | {64}):
        start = boundary_bar * BAR_TICKS - TPQ
        if start < 0:
            continue
        for i, note in enumerate(fill_notes):
            events.append(NoteEvent(start + i * TPQ // 6, TPQ // 10, note, 106 + i * 3, 1, 'PHRASE_END_FILL', 'GROOVE_FILL'))
    return tuple(sorted(events, key=lambda e: (e.start_tick, e.note, e.velocity)))


def _drums(schedule: tuple[RiffBarPlan, ...]):
    events = []
    boundaries = _family_boundaries(schedule)
    section_starts = {section.start_bar for section in _sections()}

    for plan in schedule:
        base = plan.bar_index * BAR_TICKS
        gesture = plan.gesture
        if plan.bar_index in boundaries or plan.bar_index in section_starts:
            events.append(NoteEvent(base, TPQ // 6, 49, 127, 9, 'CRASH', 'ACCENT'))

        if gesture == Gesture.STOMP:
            for beat in range(4):
                events.append(NoteEvent(base + beat * TPQ, TPQ // 8, 51, 98 + (beat % 2) * 4, 9, 'RIDE', 'TIME'))
            for beat in (0, 2):
                events.append(NoteEvent(base + beat * TPQ, TPQ // 8, 36, 124, 9, 'THRASH_HALF_TIME', 'PROPULSION'))
            events.append(NoteEvent(base + 2 * TPQ, TPQ // 8, 38, 127, 9, 'THRASH_HALF_TIME', 'BACKBEAT'))
        elif gesture == Gesture.SPRINT:
            for eighth in range(8):
                events.append(NoteEvent(base + eighth * TPQ // 2, TPQ // 8, 51, 96 + (eighth % 3) * 3, 9, 'THRASH_SKANK', 'TIME'))
                articulation = 'THRASH_KICK' if eighth % 2 == 0 else 'DOUBLE_KICK_ESCALATION'
                events.append(NoteEvent(base + eighth * TPQ // 2, TPQ // 10, 36, 121 if eighth % 2 == 0 else 117, 9, articulation, 'PROPULSION'))
            for beat in (1, 3):
                events.append(NoteEvent(base + beat * TPQ, TPQ // 8, 38, 126, 9, 'THRASH_SKANK', 'BACKBEAT'))
        elif gesture == Gesture.PANIC:
            for eighth in range(8):
                events.append(NoteEvent(base + eighth * TPQ // 2, TPQ // 8, 42, 94 + (eighth % 4) * 4, 9, 'THRASH_SKANK', 'TIME'))
            for beat in (1, 3):
                events.append(NoteEvent(base + beat * TPQ, TPQ // 8, 38, 125, 9, 'THRASH_SKANK', 'BACKBEAT'))
            for step in (0, 1, 3, 4, 6, 7, 10, 13):
                tick = base + step * TPQ // 4
                art = 'THRASH_KICK' if step % 4 == 0 else 'DOUBLE_KICK_ESCALATION'
                events.append(NoteEvent(tick, TPQ // 10, 36, 119 if art == 'THRASH_KICK' else 116, 9, art, 'PROPULSION'))
        elif gesture == Gesture.TRANSITION:
            events.append(NoteEvent(base, TPQ // 8, 36, 124, 9, 'THRASH_KICK', 'PROPULSION'))
            events.append(NoteEvent(base + 2 * TPQ, TPQ // 8, 38, 127, 9, 'CHORUS_BACKBEAT', 'BACKBEAT'))
            for i, note in enumerate((45, 47, 50, 47, 45, 50)):
                events.append(NoteEvent(base + TPQ + i * TPQ // 2, TPQ // 8, note, 108 + i * 3, 9, 'TOM_FILL', 'TRANSITION'))
        else:
            for eighth in range(8):
                events.append(NoteEvent(base + eighth * TPQ // 2, TPQ // 8, 42, 92 + (eighth % 3) * 4, 9, 'THRASH_SKANK', 'TIME'))
            for beat in (1, 3):
                events.append(NoteEvent(base + beat * TPQ, TPQ // 8, 38, 124, 9, 'CHORUS_BACKBEAT', 'BACKBEAT'))
            for tick in (0, TPQ, 2 * TPQ, 3 * TPQ, 3 * TPQ + TPQ // 2):
                art = 'THRASH_KICK' if tick % TPQ == 0 else 'DOUBLE_KICK_ESCALATION'
                events.append(NoteEvent(base + tick, TPQ // 10, 36, 120 if art == 'THRASH_KICK' else 116, 9, art, 'PROPULSION'))

    return tuple(sorted(events, key=lambda e: (e.start_tick, e.note, e.velocity)))


def _lead(sections):
    solo = next(section for section in sections if section.id == 'solo')
    start = solo.start_bar * BAR_TICKS
    events = [
        NoteEvent(start, TPQ * 2, 64, 108, 3, 'LEAD_SUSTAIN', 'MELODIC_LEAD'),
        NoteEvent(start + TPQ * 3, TPQ, 67, 112, 3, 'LEAD_VIBRATO', 'MELODIC_LEAD'),
    ]
    run1 = (64, 67, 69, 70, 72, 70, 69, 67)
    run_start = start + BAR_TICKS * 2
    for i, note in enumerate(run1):
        events.append(NoteEvent(run_start + i * TPQ // 4, TPQ // 4, note, 104 + (i % 3) * 4, 3, 'LEAD_FAST_RUN', 'MELODIC_LEAD'))
    run2 = (70, 71, 70, 67, 64, 70, 73, 72)
    answer_start = start + BAR_TICKS * 4
    for i, note in enumerate(run2):
        events.append(NoteEvent(answer_start + i * TPQ // 4, TPQ // 4, note, 106 + (i % 2) * 5, 3, 'LEAD_FAST_RUN', 'MELODIC_LEAD'))
    events.append(NoteEvent(start + BAR_TICKS * 5 + 2 * TPQ, TPQ * 2, 79, 120, 3, 'LEAD_PEAK', 'CLIMAX'))
    events.append(NoteEvent(start + BAR_TICKS * 7, TPQ * 2, 72, 108, 3, 'LEAD_VIBRATO', 'RESOLUTION'))
    return tuple(events)


def build_chainsaw_diplomacy() -> HostComposition:
    sections = _sections()
    schedule = chainsaw_riff_schedule()
    rhythm = _rhythm(schedule)
    tracks = {
        'DRUMS': RoleTrack('DRUMS', _drums(schedule), None, True),
        'BASS': RoleTrack('BASS', _bass(schedule, rhythm), 33, False),
        'RHYTHM_GUITAR': RoleTrack('RHYTHM_GUITAR', rhythm, 30, False),
        'LEAD_KEYS': RoleTrack('LEAD_KEYS', _lead(sections), 29, False),
        'VOCALS': RoleTrack('VOCALS', (), 54, False),
    }
    return HostComposition('host-003-chainsaw-diplomacy', 192, 4, 4, TPQ, 'E', sections, tracks)


def chainsaw_articulation_map(host: HostComposition) -> Mapping[str, tuple[ArticulationEvent, ...]]:
    layers = {'rhythm_guitar_L': [], 'rhythm_guitar_R': [], 'bass': [], 'drums': [], 'lead_guitar': []}
    role_to_layers = {'RHYTHM_GUITAR': ('rhythm_guitar_L', 'rhythm_guitar_R'), 'BASS': ('bass',), 'DRUMS': ('drums',), 'LEAD_KEYS': ('lead_guitar',)}
    for role, names in role_to_layers.items():
        for event in host.tracks[role].events:
            for name in names:
                layers[name].append(ArticulationEvent(name, event.start_tick, event.start_tick + event.duration_ticks, event.articulation or 'SUSTAIN'))
    return MappingProxyType({key: tuple(value) for key, value in layers.items()})


def chainsaw_vocal_windows(host: HostComposition) -> tuple[VocalWindow, ...]:
    by = {section.id: section for section in host.sections}

    def win(identifier, section, bar_offset, beats, kind):
        row = by[section]
        start = (row.start_bar + bar_offset) * BAR_TICKS
        return VocalWindow(identifier, section, start, start + int(beats * TPQ), kind)

    return (
        win('long-1', 'verse1', 0, 6, 'LONG_SUSTAIN'),
        win('bark-1', 'pre', 1, 1, 'SHORT_BARK'),
        win('sync-1', 'chorus1', 1, 3, 'SYNCOPATED'),
        VocalWindow('cross-1', 'verse2', (by['verse2'].start_bar + 2) * BAR_TICKS + 3 * TPQ, (by['verse2'].start_bar + 3) * BAR_TICKS + 2 * TPQ, 'CROSS_BAR'),
        win('call-1', 'chorus2', 2, 2, 'CALL'),
        win('response-1', 'chorus2', 3, 2, 'RESPONSE'),
        win('harmony-1', 'final_chorus', 2, 4, 'HARMONIC_DOUBLE'),
        win('dissonance-1', 'final_chorus', 5, 4, 'DISSONANT_DOUBLE'),
    )


def chainsaw_review_rubric() -> Mapping[str, str]:
    return MappingProxyType({
        'palm_mute_punch': 'Must sound percussive and tight without modern djent gating.',
        'pick_attack': 'Repeated downpicks/gallops must read as played, not machine-gunned.',
        'gain_character': 'Aggressive late-80s Thrash saturation, not over-scooped fizzy mush.',
        'double_track': 'L/R must sound like two performances while preserving riff identity.',
        'bass_body': 'Picked bass audible in low mids without modern click-bass.',
        'drum_naturalism': 'Velocity/timing/round-robin behavior must avoid grid-machine feel.',
        'lead_believability': 'Solo must read as guitar phrasing, not MIDI keyboard notes.',
    })