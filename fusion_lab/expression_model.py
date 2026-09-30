from __future__ import annotations
from dataclasses import dataclass
from .model import NoteEvent

@dataclass(frozen=True, slots=True)
class StyleTrait:
    id:str
    description:str

@dataclass(frozen=True, slots=True)
class Technique:
    id:str
    description:str

@dataclass(frozen=True, slots=True)
class Function:
    id:str
    description:str

@dataclass(frozen=True, slots=True)
class Performer:
    id:str
    name:str
    role_affinities:tuple[str,...]
    trait_ids:tuple[str,...]
    technique_ids:tuple[str,...]
    timbral_preferences:tuple[str,...]=()
    local_cycle:tuple[int,...]|None=None
    def __post_init__(self):
        if self.local_cycle is not None:
            if not self.local_cycle or any((not isinstance(x,int) or x <= 0) for x in self.local_cycle):
                raise ValueError('local_cycle values must be positive integers')

@dataclass(frozen=True, slots=True)
class Opportunity:
    id:str
    section_id:str
    start_tick:int
    end_tick:int
    eligible_functions:tuple[str,...]
    eligible_role_families:tuple[str,...]
    density_budget:float
    convergence_tick:int|None=None
    def __post_init__(self):
        if self.start_tick < 0 or self.end_tick <= self.start_tick:
            raise ValueError('opportunity requires start_tick < end_tick')
        if not 0 <= self.density_budget <= 1:
            raise ValueError('density_budget must be 0..1')
        if self.convergence_tick is not None and not self.start_tick <= self.convergence_tick <= self.end_tick:
            raise ValueError('convergence_tick must be inside opportunity')

@dataclass(frozen=True, slots=True)
class LocalContext:
    section_id:str
    harmony:str
    bpm:int
    meter:str
    phrase_position:str
    active_performers:tuple[str,...]
    density:float
    register_occupancy:tuple[int,int]|None=None

@dataclass(frozen=True, slots=True)
class ExpressionRequest:
    performer_id:str
    trait_id:str
    technique_id:str
    function_id:str
    opportunity_id:str
    role_family:str
    rhythmic_policy:str
    harmonic_policy:str
    timbral_policy:str
    density_policy:str

@dataclass(frozen=True, slots=True)
class ResolvedExpression:
    performer_id:str
    trait_id:str
    technique_id:str
    function_id:str
    opportunity_id:str
    role_family:str
    rhythmic_policy:str
    harmonic_policy:str
    timbral_policy:str
    density_policy:str
    opportunity_start_tick:int
    opportunity_end_tick:int
    events:tuple[NoteEvent,...]
