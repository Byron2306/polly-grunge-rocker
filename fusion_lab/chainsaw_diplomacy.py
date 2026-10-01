from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping
from .model import HostComposition, NoteEvent, RoleTrack, Section

TPQ=480
FORM_BARS=(4,8,4,8,8,8,8,4,8,4)
SECTION_IDS=('intro','verse1','pre','chorus1','verse2','chorus2','solo','bridge','final_chorus','outro')
BAR_TICKS=4*TPQ

@dataclass(frozen=True, slots=True)
class ArticulationEvent:
    role_layer:str
    start_tick:int
    end_tick:int
    articulation:str

@dataclass(frozen=True, slots=True)
class VocalWindow:
    id:str
    section_id:str
    start_tick:int
    end_tick:int
    kind:str

def _sections():
    out=[]; bar=0
    for sid,bars in zip(SECTION_IDS,FORM_BARS): out.append(Section(sid,bar,bars)); bar+=bars
    return tuple(out)

def _root5(root:int,start:int,dur:int,velocity:int=104,articulation:str='OPEN_RELEASE'):
    return (NoteEvent(start,dur,root,velocity,2,articulation,'RHYTHM_SUPPORT'),NoteEvent(start,dur,root+7,velocity,2,articulation,'RHYTHM_SUPPORT'))

def _riff_for_bar(base:int,variant:int):
    ev=[]
    if variant==0:
        for i in range(6): ev += list(_root5(40,base+i*TPQ//2,TPQ//3,102,'PALM_MUTE_DOWNPICK'))
        ev += list(_root5(46,base+3*TPQ,TPQ//2,112,'CHROMATIC_POWER'))
        ev += list(_root5(47,base+3*TPQ+TPQ//2,TPQ//2,114,'OPEN_RELEASE'))
    elif variant==1:
        t=base
        for _ in range(3):
            ev += list(_root5(40,t,TPQ//2,106,'PALM_MUTE_DOWNPICK')); t += TPQ//2
            ev += list(_root5(40,t,TPQ//4,98,'PALM_MUTE_GALLOP')); t += TPQ//4
            ev += list(_root5(40,t,TPQ//4,101,'PALM_MUTE_GALLOP')); t += TPQ//4
        ev += list(_root5(41,base+3*TPQ,TPQ//2,110,'CHROMATIC_POWER'))
        ev += list(_root5(42,base+3*TPQ+TPQ//2,TPQ//2,112,'CHROMATIC_POWER'))
    elif variant==2:
        for eighth in (0,1,2,3,4):
            ev += list(_root5(40,base+eighth*TPQ//2,TPQ//3,101+(eighth%2)*3,'PALM_MUTE_DOWNPICK'))
        ev += list(_root5(46,base+5*TPQ//2,TPQ//2,112,'CHROMATIC_POWER'))
        ev += list(_root5(40,base+3*TPQ,TPQ//3,106,'PALM_MUTE_DOWNPICK'))
        ev += list(_root5(46,base+7*TPQ//2,TPQ//2,116,'OPEN_RELEASE'))
    elif variant==3:
        for eighth in range(4):
            ev += list(_root5(40,base+eighth*TPQ//2,TPQ//3,104,'PALM_MUTE_DOWNPICK'))
        ev += list(_root5(43,base+2*TPQ,TPQ//2,110,'CHROMATIC_POWER'))
        ev += list(_root5(42,base+2*TPQ+TPQ//2,TPQ//2,112,'CHROMATIC_POWER'))
        ev += list(_root5(41,base+3*TPQ,TPQ//2,114,'CHROMATIC_POWER'))
        ev += list(_root5(40,base+3*TPQ+TPQ//2,TPQ//2,118,'OPEN_RELEASE'))
    else:
        for eighth in range(6):
            ev += list(_root5(40,base+eighth*TPQ//2,TPQ//3,103+(eighth%3)*2,'PALM_MUTE_DOWNPICK'))
        ev += list(_root5(46,base+3*TPQ,TPQ//4,116,'CHROMATIC_POWER'))
        ev += list(_root5(47,base+3*TPQ+TPQ//4,TPQ//4,112,'CHROMATIC_POWER'))
        ev += list(_root5(41,base+3*TPQ+TPQ//2,TPQ//4,114,'CHROMATIC_POWER'))
        ev += list(_root5(40,base+3*TPQ+3*TPQ//4,TPQ//4,120,'OPEN_RELEASE'))
    return ev

def _rhythm(sections):
    ev=[]
    for s in sections:
        for i in range(s.bars):
            phrase_pos=i%4; phrase_index=i//4
            if phrase_pos==0: variant=0
            elif phrase_pos==1: variant=1
            elif phrase_pos==2: variant=2 if phrase_index%2 else 0
            else: variant=3 if phrase_index%2==0 else 4
            ev.extend(_riff_for_bar((s.start_bar+i)*BAR_TICKS,variant))
    return tuple(sorted(ev,key=lambda e:(e.start_tick,e.note,e.duration_ticks)))

def _bass(sections,rhythm):
    ev=[]; by_tick={}
    fill_windows=[]
    for s in sections:
        end=s.end_bar*BAR_TICKS
        fill_windows.append((end-2*TPQ,end))
    for e in rhythm: by_tick.setdefault(e.start_tick,[]).append(e)
    for tick,items in sorted(by_tick.items()):
        if any(start <= tick < end for start,end in fill_windows):
            continue
        root=min(x.note for x in items)
        ev.append(NoteEvent(tick,items[0].duration_ticks,max(28,root-12),88,1,'PICKED_FOLLOW','GROOVE_ANCHOR'))
    fill_notes=(28,28,31,34,35,34,31,29,28,34,35,28)
    for start,_ in fill_windows:
        for i,note in enumerate(fill_notes):
            ev.append(NoteEvent(start+i*(TPQ//6),TPQ//8,note,86+(i%4)*3,1,'PHRASE_END_FILL','GROOVE_FILL'))
    return tuple(sorted(ev,key=lambda e:(e.start_tick,e.note)))

def _drums(sections,rhythm):
    ev=[]
    muted_by_bar={}
    for e in rhythm:
        if e.articulation in {'PALM_MUTE_DOWNPICK','PALM_MUTE_GALLOP'}:
            muted_by_bar.setdefault(e.start_tick//BAR_TICKS,set()).add(e.start_tick)
    for s in sections:
        for b in range(s.bars):
            bar_no=s.start_bar+b; base=bar_no*BAR_TICKS; bridge=s.id=='bridge'; chorus='chorus' in s.id
            if bridge:
                for beat in (0,2): ev.append(NoteEvent(base+beat*TPQ,TPQ//8,36,112,9,'THRASH_HALF_TIME','PROPULSION'))
                ev.append(NoteEvent(base+2*TPQ,TPQ//8,38,118,9,'THRASH_HALF_TIME','BACKBEAT'))
                for beat in range(4): ev.append(NoteEvent(base+beat*TPQ,TPQ//8,51,78,9,'RIDE','TIME'))
            else:
                for eighth in range(8): ev.append(NoteEvent(base+eighth*TPQ//2,TPQ//8,42 if not chorus else 51,74+(eighth%3)*3,9,'THRASH_SKANK','TIME'))
                for beat in (1,3): ev.append(NoteEvent(base+beat*TPQ,TPQ//8,38,116,9,'CHORUS_BACKBEAT' if chorus else 'THRASH_SKANK','BACKBEAT'))
                kick_step=TPQ//2 if s.id in {'pre','solo'} else TPQ
                kick_ticks=set(range(base,base+BAR_TICKS,kick_step))
                missed=[t for t in sorted(muted_by_bar.get(bar_no,())) if t not in kick_ticks]
                kick_ticks.update(t for i,t in enumerate(missed) if i%2==0)
                for t in sorted(kick_ticks):
                    is_double=kick_step<TPQ or t%TPQ!=0
                    articulation='DOUBLE_KICK_ESCALATION' if is_double else 'THRASH_KICK'
                    ev.append(NoteEvent(t,TPQ//8,36,108 if t%TPQ==0 else 102,9,articulation,'PROPULSION'))
            if b==s.bars-1:
                for i,n in enumerate((45,47,50,47)): ev.append(NoteEvent(base+3*TPQ+i*TPQ//4,TPQ//8,n,96+i*4,9,'TOM_FILL','TRANSITION'))
    return tuple(sorted(ev,key=lambda e:(e.start_tick,e.note,e.velocity)))

def _lead(sections):
    s=next(x for x in sections if x.id=='solo'); start=s.start_bar*BAR_TICKS; ev=[]
    ev.append(NoteEvent(start,TPQ*2,76,104,3,'LEAD_SUSTAIN','MELODIC_LEAD'))
    ev.append(NoteEvent(start+TPQ*3,TPQ,79,108,3,'LEAD_VIBRATO','MELODIC_LEAD'))
    run=(76,79,81,82,84,86,88,91); run_start=start+BAR_TICKS*2
    for i,n in enumerate(run): ev.append(NoteEvent(run_start+i*TPQ//4,TPQ//5,n,100+i%3*5,3,'LEAD_FAST_RUN','MELODIC_LEAD'))
    ev.append(NoteEvent(start+BAR_TICKS*5,TPQ*2,95,118,3,'LEAD_PEAK','CLIMAX'))
    ev.append(NoteEvent(start+BAR_TICKS*7,TPQ,88,100,3,'LEAD_VIBRATO','RESOLUTION'))
    return tuple(ev)

def build_chainsaw_diplomacy()->HostComposition:
    sections=_sections(); rhythm=_rhythm(sections)
    tracks={'DRUMS':RoleTrack('DRUMS',_drums(sections,rhythm),None,True),'BASS':RoleTrack('BASS',_bass(sections,rhythm),33,False),'RHYTHM_GUITAR':RoleTrack('RHYTHM_GUITAR',rhythm,30,False),'LEAD_KEYS':RoleTrack('LEAD_KEYS',_lead(sections),29,False),'VOCALS':RoleTrack('VOCALS',(),54,False)}
    return HostComposition('host-003-chainsaw-diplomacy',192,4,4,TPQ,'E',sections,tracks)

def chainsaw_articulation_map(host:HostComposition)->Mapping[str,tuple[ArticulationEvent,...]]:
    layers={'rhythm_guitar_L':[],'rhythm_guitar_R':[],'bass':[],'drums':[],'lead_guitar':[]}
    role_to_layers={'RHYTHM_GUITAR':('rhythm_guitar_L','rhythm_guitar_R'),'BASS':('bass',),'DRUMS':('drums',),'LEAD_KEYS':('lead_guitar',)}
    for role,names in role_to_layers.items():
        for e in host.tracks[role].events:
            for name in names: layers[name].append(ArticulationEvent(name,e.start_tick,e.start_tick+e.duration_ticks,e.articulation or 'SUSTAIN'))
    return MappingProxyType({k:tuple(v) for k,v in layers.items()})

def chainsaw_vocal_windows(host:HostComposition)->tuple[VocalWindow,...]:
    by={s.id:s for s in host.sections}
    def win(i,section,bar_offset,beats,kind):
        s=by[section]; start=(s.start_bar+bar_offset)*BAR_TICKS; return VocalWindow(i,section,start,start+int(beats*TPQ),kind)
    return (win('long-1','verse1',0,6,'LONG_SUSTAIN'),win('bark-1','pre',1,1,'SHORT_BARK'),win('sync-1','chorus1',1,3,'SYNCOPATED'),VocalWindow('cross-1','verse2',(by['verse2'].start_bar+2)*BAR_TICKS+3*TPQ,(by['verse2'].start_bar+3)*BAR_TICKS+2*TPQ,'CROSS_BAR'),win('call-1','chorus2',2,2,'CALL'),win('response-1','chorus2',3,2,'RESPONSE'),win('harmony-1','final_chorus',2,4,'HARMONIC_DOUBLE'),win('dissonance-1','final_chorus',5,4,'DISSONANT_DOUBLE'))

def chainsaw_review_rubric()->Mapping[str,str]:
    return MappingProxyType({'palm_mute_punch':'Must sound percussive and tight without modern djent gating.','pick_attack':'Repeated downpicks/gallops must read as played, not machine-gunned.','gain_character':'Aggressive late-80s Thrash saturation, not over-scooped fizzy mush.','double_track':'L/R must sound like two performances while preserving riff identity.','bass_body':'Picked bass audible in low mids without modern click-bass.','drum_naturalism':'Velocity/timing/round-robin behavior must avoid grid-machine feel.','lead_believability':'Solo must read as guitar phrasing, not MIDI keyboard notes.'})
