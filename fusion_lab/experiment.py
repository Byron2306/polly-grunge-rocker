from __future__ import annotations
from dataclasses import replace
from .model import ExperimentDefinition, HostComposition, NoteEvent, Role, RoleTrack

EXPERIMENT_001=ExperimentDefinition(
    id='exp-001-style-not-function',host_id='host-001-glamasaurus-rex',role='RHYTHM_GUITAR',
    frozen_dimensions=('global_clock','sections','other_roles','function','harmonic_roots','phrase_bounds','chord_change_grid'),
    mutated_dimensions=('articulation','performance_density','voicing','register'),
    hypothesis='A stylistic trademark can change while convergent musical function remains constant.',
    variants=('A','B1','B2','C'),
)

def _bar_ticks(host:HostComposition)->int: return host.numerator*host.ticks_per_beat

def _section_ranges(host:HostComposition, pred):
    bt=_bar_ticks(host)
    return [(s.start_bar*bt,s.end_bar*bt) for s in host.sections if pred(s.id)]

def _in_ranges(tick:int,ranges): return any(a<=tick<b for a,b in ranges)

def _repeat_event(e:NoteEvent, division:int, articulation:str, octave:int=0):
    count=max(1,e.duration_ticks//division)
    out=[]
    for i in range(count):
        out.append(replace(e,start_tick=e.start_tick+i*division,duration_ticks=division,note=max(0,min(127,e.note+octave)),articulation=articulation))
    return out

def _variant(host:HostComposition, events:tuple[NoteEvent,...])->HostComposition:
    tracks=dict(host.tracks); old=tracks['RHYTHM_GUITAR']
    tracks['RHYTHM_GUITAR']=RoleTrack('RHYTHM_GUITAR',tuple(sorted(events,key=lambda e:(e.start_tick,e.note,e.duration_ticks))),old.program,old.percussion)
    return replace(host,tracks=tracks)

def _build_b1(host):
    chorus=_section_ranges(host,lambda s:'chorus' in s)
    division=host.ticks_per_beat//4
    out=[]
    for e in host.tracks['RHYTHM_GUITAR'].events:
        if _in_ranges(e.start_tick,chorus): out.extend(_repeat_event(e,division,'TREMOLO_TEXTURE'))
        else: out.append(e)
    return _variant(host,tuple(out))

def _build_b2(host):
    chorus=_section_ranges(host,lambda s:'chorus' in s)
    division=host.ticks_per_beat//4; out=[]; bt=_bar_ticks(host)
    for e in host.tracks['RHYTHM_GUITAR'].events:
        if _in_ranges(e.start_tick,chorus): out.extend(_repeat_event(e,division,'TREMOLO_TEXTURE',12))
        else: out.append(e)
    for s in host.sections:
        if 'chorus' not in s.id: continue
        for bar in range(s.start_bar,s.end_bar):
            original=[e for e in host.tracks['RHYTHM_GUITAR'].events if bar*bt<=e.start_tick<(bar+1)*bt]
            if original:
                root=min(e.note for e in original)
                out.append(NoteEvent(bar*bt,bt,root,72,2,'PEDAL_DRONE','HARMONIC_SUPPORT'))
    return _variant(host,tuple(out))

def _build_c(host):
    division=host.ticks_per_beat//4; out=[]
    for e in host.tracks['RHYTHM_GUITAR'].events: out.extend(_repeat_event(e,division,'TREMOLO_TEXTURE'))
    return _variant(host,tuple(out))

def build_experiment_001(host:HostComposition)->dict[str,HostComposition]:
    return {'A':host,'B1':_build_b1(host),'B2':_build_b2(host),'C':_build_c(host)}

def _role_events(host,role): return host.tracks[role].events

def _bar_presence(host,role):
    bt=_bar_ticks(host); return tuple(sorted({e.start_tick//bt for e in _role_events(host,role)}))

def _harmonic_roots_preserved(host,variant,role):
    bt=_bar_ticks(host); he=_role_events(host,role); ve=_role_events(variant,role)
    for bar in _bar_presence(host,role):
        hbar=[e for e in he if bar*bt<=e.start_tick<(bar+1)*bt]
        vbar=[e for e in ve if bar*bt<=e.start_tick<(bar+1)*bt]
        if not hbar or not vbar: return False
        root=min(e.note for e in hbar)%12
        if not any(e.note%12==root for e in vbar): return False
    return True

def _phrase_bounds(events):
    if not events: return None
    return (min(e.start_tick for e in events),max(e.start_tick+e.duration_ticks for e in events))

def compare_dimensions(host:HostComposition,variant:HostComposition,role:Role)->dict[str,bool]:
    he=_role_events(host,role); ve=_role_events(variant,role)
    other_roles=all(host.tracks[r]==variant.tracks[r] for r in host.tracks if r!=role)
    return {
      'global_clock':(host.bpm,host.numerator,host.denominator,host.ticks_per_beat,host.tonal_center)==(variant.bpm,variant.numerator,variant.denominator,variant.ticks_per_beat,variant.tonal_center),
      'sections':host.sections==variant.sections,
      'other_roles':other_roles,
      'function':{e.function for e in he}=={e.function for e in ve},
      'harmonic_roots':_harmonic_roots_preserved(host,variant,role),
      'phrase_bounds':_phrase_bounds(he)==_phrase_bounds(ve),
      'chord_change_grid':_bar_presence(host,role)==_bar_presence(variant,role),
      'articulation':tuple(e.articulation for e in he)==tuple(e.articulation for e in ve),
      'performance_density':len(he)==len(ve),
      'voicing':tuple(sorted({e.note for e in he}))==tuple(sorted({e.note for e in ve})),
      'register':(min(e.note for e in he),max(e.note for e in he))==(min(e.note for e in ve),max(e.note for e in ve)),
    }

def assert_experiment_contract(definition:ExperimentDefinition,host:HostComposition,variant:HostComposition)->None:
    if definition.host_id!=host.id or definition.role not in host.tracks: raise ValueError('FUSION_EXPERIMENT_HOST_MISMATCH')
    dims=compare_dimensions(host,variant,definition.role)
    failed=[d for d in definition.frozen_dimensions if not dims.get(d,False)]
    if failed: raise ValueError('FUSION_EXPERIMENT_FROZEN_DIMENSION: '+','.join(failed))
