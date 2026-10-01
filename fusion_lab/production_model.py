from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Literal, Mapping

@dataclass(frozen=True, slots=True)
class ArticulationMap:
    name:str
    keyswitch:int|None=None
    midi_channel:int|None=None
    velocity_min:int=1
    velocity_max:int=127
    def __post_init__(self):
        if not self.name: raise ValueError('articulation name required')
        if self.keyswitch is not None and not 0 <= self.keyswitch <= 127: raise ValueError('keyswitch must be 0..127')
        if self.midi_channel is not None and not 0 <= self.midi_channel <= 15: raise ValueError('midi_channel must be 0..15')
        if not (1 <= self.velocity_min <= self.velocity_max <= 127): raise ValueError('invalid velocity range')

@dataclass(frozen=True, slots=True)
class InstrumentProfile:
    id:str
    role:str
    sfz_path:Path
    articulations:Mapping[str,ArticulationMap]
    source_id:str
    source_version:str|None=None
    def __post_init__(self):
        if not self.id or not self.role or not self.source_id: raise ValueError('instrument id, role and source_id required')
        if not self.articulations: raise ValueError('instrument articulation mapping required')
        object.__setattr__(self,'articulations',MappingProxyType(dict(self.articulations)))

@dataclass(frozen=True, slots=True)
class HumanizationProfile:
    seed:int
    timing_ms:int=0
    velocity_delta:int=0
    double_track_timing_ms:int=0
    double_track_velocity_delta:int=0
    def __post_init__(self):
        for name in ('timing_ms','velocity_delta','double_track_timing_ms','double_track_velocity_delta'):
            value=getattr(self,name)
            if value < 0: raise ValueError(f'{name} must be >= 0')
        if self.timing_ms > 30 or self.double_track_timing_ms > 40: raise ValueError('timing humanization exceeds production bound')
        if self.velocity_delta > 32 or self.double_track_velocity_delta > 40: raise ValueError('velocity humanization exceeds production bound')

@dataclass(frozen=True, slots=True)
class ToneControls:
    tuning_profile:str='E_STANDARD'
    pitch_shift_semitones:int=0
    boost_drive:float=0.0
    boost_level:float=0.0
    amp_gain:float=5.0
    distortion:float=0.0
    bass:float=5.0
    mid:float=5.0
    treble:float=5.0
    presence:float=5.0
    master:float=5.0
    reverb_mix:float=0.0
    reverb_decay_s:float=0.0
    reverb_predelay_ms:int=0
    cabinet_ir:Path|None=None
    def __post_init__(self):
        if not self.tuning_profile: raise ValueError('tuning_profile required')
        if not -24 <= self.pitch_shift_semitones <= 24: raise ValueError('pitch_shift_semitones must be -24..24')
        for name in ('boost_drive','boost_level','amp_gain','distortion','bass','mid','treble','presence','master'):
            value=float(getattr(self,name))
            if not 0.0 <= value <= 10.0: raise ValueError(f'{name} must be 0..10')
        if not 0.0 <= self.reverb_mix <= 1.0: raise ValueError('reverb_mix must be 0..1')
        if not 0.0 <= self.reverb_decay_s <= 20.0: raise ValueError('reverb_decay_s must be 0..20')
        if not 0 <= self.reverb_predelay_ms <= 500: raise ValueError('reverb_predelay_ms must be 0..500')

@dataclass(frozen=True, slots=True)
class ToneStage:
    kind:str
    executable:str|None=None
    args:tuple[str,...]=()
    asset_path:Path|None=None
    def __post_init__(self):
        if not self.kind: raise ValueError('tone stage kind required')
        if self.kind.lower() in {'function','role_function','musical_function'}: raise ValueError('tone stage may not encode musical function')

@dataclass(frozen=True, slots=True)
class ToneProfile:
    id:str
    stages:tuple[ToneStage,...]
    pan:float=0.0
    width:float=1.0
    controls:ToneControls|None=None
    def __post_init__(self):
        if not self.id: raise ValueError('tone profile id required')
        if not -1.0 <= self.pan <= 1.0: raise ValueError('pan must be -1..1')
        if self.width <= 0: raise ValueError('width must be positive')

@dataclass(frozen=True, slots=True)
class ProductionRoleProfile:
    role_layer:str
    instrument_id:str
    tone_profile_id:str
    humanization_id:str

@dataclass(frozen=True, slots=True)
class AuthenticityReview:
    state:Literal['PASS','ADJUST','REFUSE']
    notes:tuple[str,...]
    rubric:Mapping[str,str]
    def __post_init__(self):
        if self.state not in {'PASS','ADJUST','REFUSE'}: raise ValueError('invalid authenticity review state')
        object.__setattr__(self,'rubric',MappingProxyType(dict(self.rubric)))

@dataclass(frozen=True, slots=True)
class ProductionConfig:
    sample_rate:int
    sfizz_executable:str='sfizz_render'
    mixer_executable:str|None=None
    def __post_init__(self):
        if self.sample_rate <= 0: raise ValueError('sample_rate must be positive')

@dataclass(frozen=True, slots=True)
class ProductionStem:
    role_layer:str
    clean_path:Path
    processed_path:Path
    instrument_id:str
    tone_profile_id:str
