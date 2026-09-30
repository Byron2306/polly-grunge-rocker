from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, Mapping
from .model import HostComposition, RoleTrack, NoteEvent
from .expression_model import StyleTrait, Technique, Function, Performer, Opportunity, ExpressionRequest, ResolvedExpression

Handler = Callable[[HostComposition, ExpressionRequest, Performer, Opportunity], tuple[NoteEvent,...]]

@dataclass(frozen=True, slots=True)
class ExpressionRegistries:
    traits:Mapping[str,StyleTrait]
    techniques:Mapping[str,Technique]
    functions:Mapping[str,Function]
    performers:Mapping[str,Performer]
    handlers:Mapping[str,Handler]
    def __post_init__(self):
        for name in ('traits','techniques','functions','performers','handlers'):
            object.__setattr__(self,name,MappingProxyType(dict(getattr(self,name))))

def _event_density(events:tuple[NoteEvent,...], opportunity:Opportunity)->float:
    span=opportunity.end_tick-opportunity.start_tick
    return sum(e.duration_ticks for e in events)/span if span else 0.0

def expression_density(expressions:tuple[ResolvedExpression,...], opportunity:Opportunity)->float:
    events=tuple(e for x in expressions if x.opportunity_id==opportunity.id for e in x.events)
    return _event_density(events,opportunity)

def resolve_expression(host:HostComposition, request:ExpressionRequest, registries:ExpressionRegistries, opportunity:Opportunity)->ResolvedExpression:
    if request.performer_id not in registries.performers: raise ValueError('unknown performer')
    if request.trait_id not in registries.traits: raise ValueError('unknown trait')
    if request.technique_id not in registries.techniques: raise ValueError('unknown technique')
    if request.function_id not in registries.functions: raise ValueError('unknown function')
    if request.opportunity_id != opportunity.id: raise ValueError('opportunity mismatch')
    performer=registries.performers[request.performer_id]
    if request.trait_id not in performer.trait_ids: raise ValueError('performer lacks trait')
    if request.technique_id not in performer.technique_ids: raise ValueError('performer lacks technique')
    if request.function_id not in opportunity.eligible_functions: raise ValueError('function not allowed by opportunity')
    if request.role_family not in opportunity.eligible_role_families: raise ValueError('role family not allowed by opportunity')
    handler=registries.handlers.get(request.technique_id)
    if handler is None: raise ValueError('missing technique handler')
    events=tuple(sorted(handler(host,request,performer,opportunity), key=lambda e:(e.start_tick,e.channel,e.note,e.duration_ticks)))
    for event in events:
        if event.start_tick < opportunity.start_tick or event.start_tick >= opportunity.end_tick:
            if request.density_policy != 'SATURATION_CONTROL':
                raise ValueError('event outside opportunity')
    density=_event_density(events,opportunity)
    if density > opportunity.density_budget and request.density_policy != 'SATURATION_CONTROL':
        raise ValueError('density budget exceeded')
    return ResolvedExpression(request.performer_id,request.trait_id,request.technique_id,request.function_id,request.opportunity_id,request.role_family,request.rhythmic_policy,request.harmonic_policy,request.timbral_policy,request.density_policy,opportunity.start_tick,opportunity.end_tick,events)

def apply_expressions(host:HostComposition, expressions:tuple[ResolvedExpression,...])->HostComposition:
    tracks=dict(host.tracks)
    grouped:dict[str,list[ResolvedExpression]]={}
    for expression in expressions:
        grouped.setdefault(expression.role_family,[]).append(expression)
    for role, exprs in grouped.items():
        if role not in tracks: raise ValueError(f'unknown role family {role}')
        base=tracks[role]
        events=list(base.events)
        for expression in exprs:
            if expression.rhythmic_policy == 'REPLACE_ROLE_WINDOW':
                events=[e for e in events if not (expression.opportunity_start_tick <= e.start_tick < expression.opportunity_end_tick)]
            events.extend(expression.events)
        events.sort(key=lambda e:(e.start_tick,e.channel,e.note,e.duration_ticks))
        tracks[role]=RoleTrack(base.role,tuple(events),base.program,base.percussion)
    return HostComposition(host.id,host.bpm,host.numerator,host.denominator,host.ticks_per_beat,host.tonal_center,host.sections,tracks)

def _riff_signature(host:HostComposition):
    return tuple((e.start_tick,e.duration_ticks,e.note,e.velocity,e.channel,e.articulation,e.function) for e in host.tracks['RHYTHM_GUITAR'].events)

def compare_host_dimensions(host:HostComposition, variant:HostComposition)->dict[str,bool]:
    return {
        'tempo':host.bpm==variant.bpm,
        'meter':(host.numerator,host.denominator)==(variant.numerator,variant.denominator),
        'sections':host.sections==variant.sections,
        'host_riff':_riff_signature(host)==_riff_signature(variant),
        'tonal_center':host.tonal_center==variant.tonal_center,
    }

def assert_frozen_dimensions(host:HostComposition, variant:HostComposition, frozen:tuple[str,...], mutated:tuple[str,...])->None:
    dimensions=compare_host_dimensions(host,variant)
    for dim in frozen:
        if dim in mutated: raise ValueError(f'dimension both frozen and mutated: {dim}')
        if dim in dimensions and not dimensions[dim]: raise ValueError(f'frozen dimension changed: {dim}')

def standard_technique_handlers()->dict[str,Handler]:
    def sustain(host,request,performer,opp):
        dur=max(host.ticks_per_beat*2, min(opp.end_tick-opp.start_tick, host.ticks_per_beat*4))
        return (NoteEvent(opp.start_tick,dur,64,84,3,'SUSTAINED_MELODIC_LINE',request.function_id),)
    def drone(host,request,performer,opp):
        return (NoteEvent(opp.start_tick,opp.end_tick-opp.start_tick,52,72,3,'DRONE_ANCHOR',request.function_id),)
    def thumb(host,request,performer,opp):
        step=max(30,host.ticks_per_beat//4)
        return tuple(NoteEvent(t,step//2,40,100,1,'THUMB_ATTACK',request.function_id) for t in range(opp.start_tick,opp.end_tick,step*2))
    def slap(host,request,performer,opp):
        step=max(30,host.ticks_per_beat//2)
        return tuple(NoteEvent(t,step//2,52,110,1,'SLAP_POP',request.function_id) for t in range(opp.start_tick+step,opp.end_tick,step*2))
    def ghost(host,request,performer,opp):
        step=max(30,host.ticks_per_beat//4)
        return tuple(NoteEvent(t,step//4,36,45,1,'GHOST_NOTE',request.function_id) for t in range(opp.start_tick+step//2,opp.end_tick,step))
    def local_cycle(host,request,performer,opp):
        cycle=performer.local_cycle or (3,3,2,3,5)
        unit=max(30,host.ticks_per_beat//4)
        t=opp.start_tick; out=[]; i=0
        while t < opp.end_tick:
            out.append(NoteEvent(t,max(15,unit//2),40+(i%2)*7,96,1,'ROLE_LOCAL_CYCLE',request.function_id))
            t += cycle[i%len(cycle)]*unit
            i += 1
        return tuple(out)
    def synth_swell(host,request,performer,opp):
        dur=min(opp.end_tick-opp.start_tick,host.ticks_per_beat*4)
        return (NoteEvent(opp.start_tick,dur,76,68,3,'SYNTH_SWELL',request.function_id),)
    def choir(host,request,performer,opp):
        dur=min(opp.end_tick-opp.start_tick,host.ticks_per_beat*4)
        return tuple(NoteEvent(opp.start_tick,dur,n,58,3,'CHOIR_PAD',request.function_id) for n in (64,67,71))
    def filter_move(host,request,performer,opp):
        step=host.ticks_per_beat
        return tuple(NoteEvent(t,max(30,step//2),72+(i%3)*2,min(120,55+i*5),3,'FILTER_MOVEMENT',request.function_id) for i,t in enumerate(range(opp.start_tick,opp.end_tick,step)))
    def noise_bed(host,request,performer,opp):
        return (NoteEvent(opp.start_tick,opp.end_tick-opp.start_tick,84,35,3,'NOISE_BED',request.function_id),)
    def double_kick(host,request,performer,opp):
        step=max(30,host.ticks_per_beat//4)
        return tuple(NoteEvent(t,step//3,36,112,9,'DOUBLE_KICK_LOCK',request.function_id) for t in range(opp.start_tick,opp.end_tick,step))
    def blast(host,request,performer,opp):
        step=max(30,host.ticks_per_beat//4)
        out=[]
        for i,t in enumerate(range(opp.start_tick,opp.end_tick,step)):
            out.append(NoteEvent(t,step//3,38 if i%2 else 36,116,9,'BLAST_BEAT',request.function_id))
            out.append(NoteEvent(t,step//3,42,88,9,'BLAST_BEAT',request.function_id))
        return tuple(out)
    def death_half(host,request,performer,opp):
        beat=host.ticks_per_beat
        out=[]
        for t in range(opp.start_tick,opp.end_tick,beat*2):
            out.append(NoteEvent(t,beat//3,36,118,9,'DEATH_HALF_TIME',request.function_id))
            if t+beat < opp.end_tick: out.append(NoteEvent(t+beat,beat//3,38,120,9,'DEATH_HALF_TIME',request.function_id))
        return tuple(out)
    def tom_fill(host,request,performer,opp):
        step=max(30,host.ticks_per_beat//4)
        notes=(45,47,48,50)
        return tuple(NoteEvent(t,step//2,notes[i%4],108,9,'TOM_FILL',request.function_id) for i,t in enumerate(range(opp.start_tick,opp.end_tick,step)))
    def metric_disp(host,request,performer,opp):
        return local_cycle(host,request,performer,opp)
    return {
        'SUSTAINED_MELODIC_LINE':sustain,'DRONE_ANCHOR':drone,'THUMB_ATTACK':thumb,'SLAP_POP':slap,
        'GHOST_NOTE':ghost,'METRIC_DISPLACEMENT':metric_disp,'ROLE_LOCAL_CYCLE':local_cycle,
        'SYNTH_SWELL':synth_swell,'CHOIR_PAD':choir,'FILTER_MOVEMENT':filter_move,'NOISE_BED':noise_bed,
        'DOUBLE_KICK_LOCK':double_kick,'BLAST_BEAT':blast,'DEATH_HALF_TIME':death_half,'TOM_FILL':tom_fill,
    }
