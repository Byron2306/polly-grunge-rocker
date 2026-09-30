from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal

Role = Literal['DRUMS','BASS','RHYTHM_GUITAR','LEAD_KEYS','VOCALS']
CANONICAL_ROLES: tuple[Role,...] = ('DRUMS','BASS','RHYTHM_GUITAR','LEAD_KEYS','VOCALS')

@dataclass(frozen=True, slots=True)
class NoteEvent:
    start_tick:int
    duration_ticks:int
    note:int
    velocity:int
    channel:int
    articulation:str|None=None
    function:str|None=None
    def __post_init__(self):
        if self.start_tick < 0: raise ValueError('start_tick must be >= 0')
        if self.duration_ticks <= 0: raise ValueError('duration_ticks must be > 0')
        if not 0 <= self.note <= 127: raise ValueError('note must be 0..127')
        if not 1 <= self.velocity <= 127: raise ValueError('velocity must be 1..127')
        if not 0 <= self.channel <= 15: raise ValueError('channel must be 0..15')

@dataclass(frozen=True, slots=True)
class Section:
    id:str
    start_bar:int
    bars:int
    def __post_init__(self):
        if self.start_bar < 0: raise ValueError('start_bar must be >= 0')
        if self.bars <= 0: raise ValueError('bars must be > 0')
    @property
    def end_bar(self)->int: return self.start_bar+self.bars

@dataclass(frozen=True, slots=True)
class RoleTrack:
    role:Role
    events:tuple[NoteEvent,...]
    program:int|None
    percussion:bool=False
    def __post_init__(self):
        if self.role not in CANONICAL_ROLES: raise ValueError('unknown role')
        if self.program is not None and not 0 <= self.program <= 127: raise ValueError('program must be 0..127')

@dataclass(frozen=True, slots=True)
class HostComposition:
    id:str
    bpm:int
    numerator:int
    denominator:int
    ticks_per_beat:int
    tonal_center:str
    sections:tuple[Section,...]
    tracks:dict[Role,RoleTrack]
    def __post_init__(self):
        if self.bpm <= 0: raise ValueError('bpm must be > 0')
        if self.numerator <= 0 or self.denominator <= 0: raise ValueError('meter must be positive')
        if self.ticks_per_beat <= 0: raise ValueError('ticks_per_beat must be > 0')
        previous_end=-1
        for section in self.sections:
            if section.start_bar < previous_end: raise ValueError('sections overlap or move backwards')
            previous_end=section.end_bar
        if set(self.tracks) != set(CANONICAL_ROLES): raise ValueError('host must contain exactly five canonical roles')
        object.__setattr__(self, 'tracks', MappingProxyType(dict(self.tracks)))
        for role,track in self.tracks.items():
            if track.role != role: raise ValueError('track role mismatch')

@dataclass(frozen=True, slots=True)
class ExperimentDefinition:
    id:str
    host_id:str
    role:Role
    frozen_dimensions:tuple[str,...]
    mutated_dimensions:tuple[str,...]
    hypothesis:str
    variants:tuple[str,...]
