from __future__ import annotations
from dataclasses import replace
from .model import HostComposition, Section, RoleTrack, NoteEvent, CANONICAL_ROLES
from .expression_model import StyleTrait, Technique, Function, Performer, Opportunity, ExpressionRequest, ResolvedExpression
from .expression_engine import ExpressionRegistries, standard_technique_handlers, resolve_expression, apply_expressions, assert_frozen_dimensions

TPB=480
BAR=TPB*4
FORM=(
    ('INTRO',4),('VERSE_1',8),('PRE_CHORUS',4),('CHORUS_1',8),('VERSE_2',8),
    ('CHORUS_2',8),('SOLO',8),('BREAK',4),('FINAL_CHORUS',8),('OUTRO',4),
)

SECTION_ROOTS={
    'INTRO':(40,40,46,45),
    'VERSE_1':(40,40,43,41,40,46,45,40),
    'PRE_CHORUS':(43,45,46,47),
    'CHORUS_1':(40,43,45,46,40,43,47,46),
    'VERSE_2':(40,40,43,41,40,46,45,40),
    'CHORUS_2':(40,43,45,46,40,43,47,46),
    'SOLO':(40,43,45,46,41,43,46,47),
    'BREAK':(40,41,40,46),
    'FINAL_CHORUS':(40,43,45,46,40,43,47,40),
    'OUTRO':(40,46,45,40),
}

def _sections()->tuple[Section,...]:
    out=[]; bar=0
    for sid,bars in FORM:
        out.append(Section(sid,bar,bars)); bar += bars
    return tuple(out)

def _section(host:HostComposition, sid:str)->Section:
    return next(s for s in host.sections if s.id==sid)

def _section_ticks(host:HostComposition, sid:str)->tuple[int,int]:
    s=_section(host,sid)
    return s.start_bar*BAR,s.end_bar*BAR

def _riff_events(sections:tuple[Section,...])->tuple[NoteEvent,...]:
    out=[]
    gallop=(0,120,240,480,600,720,960,1080,1200,1440,1560,1680)
    for sec in sections:
        roots=SECTION_ROOTS[sec.id]
        for local_bar in range(sec.bars):
            root=roots[local_bar%len(roots)]
            bar_start=(sec.start_bar+local_bar)*BAR
            for i,off in enumerate(gallop):
                dur=90 if i%3!=2 else 180
                vel=112 if off in (0,960) else 100
                out.append(NoteEvent(bar_start+off,dur,root,vel,2,'THRASH_GALLOP','HOST_RIFF'))
            out.append(NoteEvent(bar_start+1800,120,min(root+7,127),108,2,'THRASH_DOWNPICK','HOST_RIFF'))
    return tuple(sorted(out,key=lambda e:(e.start_tick,e.note)))

def _bass_events(riff:tuple[NoteEvent,...])->tuple[NoteEvent,...]:
    return tuple(NoteEvent(e.start_tick,max(90,e.duration_ticks),max(0,e.note-12),94,1,'THRASH_BASS_FOLLOW','PRIMARY_GROOVE') for e in riff)

def _drum_events(sections:tuple[Section,...])->tuple[NoteEvent,...]:
    out=[]
    for sec in sections:
        for local_bar in range(sec.bars):
            start=(sec.start_bar+local_bar)*BAR
            for off in range(0,BAR,TPB//2):
                out.append(NoteEvent(start+off,90,42,82,9,'THRASH_HAT','PULSE'))
            for off in (TPB,TPB*3):
                out.append(NoteEvent(start+off,120,38,112,9,'THRASH_SNARE','BACKBEAT'))
            for off in (0,240,960,1200,1440):
                out.append(NoteEvent(start+off,90,36,108,9,'THRASH_KICK','PROPULSION'))
            if local_bar==sec.bars-1:
                for i,n in enumerate((45,47,48,50)):
                    out.append(NoteEvent(start+1440+i*120,90,n,98,9,'THRASH_FILL','TRANSITION_DRIVE'))
    return tuple(sorted(out,key=lambda e:(e.start_tick,e.note)))

def _lead_events(sections:tuple[Section,...])->tuple[NoteEvent,...]:
    out=[]
    for sec in sections:
        if sec.id in {'CHORUS_1','CHORUS_2','FINAL_CHORUS','SOLO'}:
            start=sec.start_bar*BAR
            notes=(64,67,69,70,67,64,62,64)
            for i,n in enumerate(notes):
                t=start+i*TPB
                if t < sec.end_bar*BAR:
                    out.append(NoteEvent(t,TPB//2,n,90,3,'THRASH_LEAD','MELODIC_LEAD'))
    return tuple(out)

def _vocal_guide(sections:tuple[Section,...])->tuple[NoteEvent,...]:
    out=[]
    for sec in sections:
        if sec.id.startswith('CHORUS') or sec.id=='FINAL_CHORUS':
            start=sec.start_bar*BAR
            for i,n in enumerate((64,64,67,69)):
                out.append(NoteEvent(start+i*TPB*2,TPB,n,72,4,'VOCAL_GUIDE','PHRASE_CALL'))
    return tuple(out)

def build_thrash_host()->HostComposition:
    sections=_sections()
    riff=_riff_events(sections)
    tracks={
        'DRUMS':RoleTrack('DRUMS',_drum_events(sections),None,True),
        'BASS':RoleTrack('BASS',_bass_events(riff),33,False),
        'RHYTHM_GUITAR':RoleTrack('RHYTHM_GUITAR',riff,30,False),
        'LEAD_KEYS':RoleTrack('LEAD_KEYS',_lead_events(sections),29,False),
        'VOCALS':RoleTrack('VOCALS',_vocal_guide(sections),53,False),
    }
    return HostComposition('host-002-thrash-control',190,4,4,TPB,'E',sections,tracks)

def build_thrash_chimera_registries()->ExpressionRegistries:
    traits={x.id:x for x in (
        StyleTrait('LONG_SUSTAIN','long sustain and harmonic gravity'),
        StyleTrait('PERCUSSIVE_THUMB','percussive thumb/slap and displaced groove'),
        StyleTrait('TIMBRAL_EXPERIMENTATION','spectral transformation and re-orchestration'),
        StyleTrait('EXTREME_DENSITY','high-density death-metal percussion vocabulary'),
    )}
    techniques={x.id:x for x in (
        Technique('SUSTAINED_MELODIC_LINE','slow sustained melodic line'),Technique('DRONE_ANCHOR','long pedal drone'),
        Technique('THUMB_ATTACK','percussive thumb attack'),Technique('SLAP_POP','slap/pop punctuation'),Technique('GHOST_NOTE','muted ghost note'),
        Technique('METRIC_DISPLACEMENT','displaced accent pattern'),Technique('ROLE_LOCAL_CYCLE','role-local accent cycle'),
        Technique('SYNTH_SWELL','synth swell'),Technique('CHOIR_PAD','choir-like pad'),Technique('FILTER_MOVEMENT','moving filter texture'),Technique('NOISE_BED','noise atmosphere'),
        Technique('DOUBLE_KICK_LOCK','dense double-kick propulsion'),Technique('BLAST_BEAT','blast-beat escalation'),Technique('DEATH_HALF_TIME','half-time death groove'),Technique('TOM_FILL','violent tom transition'),
    )}
    functions={x.id:x for x in (
        Function('COUNTER_MELODY','slow melodic counterline'),Function('EMOTIONAL_BED','emotional bed'),Function('RESOLUTION','resolution'),
        Function('COUNTER_RHYTHM','counter-rhythm'),Function('GROOVE_DESTABILIZATION','groove destabilization'),Function('CONVERGENCE_SETUP','convergence setup'),
        Function('TEXTURAL_ATMOSPHERE','textural atmosphere'),Function('SECTION_ILLUMINATION','section illumination'),Function('DRAMATIC_REVEAL','dramatic reveal'),
        Function('PROPULSION','forward propulsion'),Function('ESCALATION','escalation'),Function('DENSE_SUPPORT','dense support'),Function('SECTION_GRAVITY','section gravity'),Function('TRANSITION_DRIVE','transition drive'),
    )}
    performers={
        'doom_guitarist':Performer('doom_guitarist','Doom Melodic Guitarist',('LEAD_KEYS',),('LONG_SUSTAIN',),('SUSTAINED_MELODIC_LINE','DRONE_ANCHOR'),('HEAVY_VIBRATO','WARM_SATURATION')),
        'djent_bassist':Performer('djent_bassist','Djent Thumb Bassist',('BASS',),('PERCUSSIVE_THUMB',),('THUMB_ATTACK','SLAP_POP','GHOST_NOTE','METRIC_DISPLACEMENT','ROLE_LOCAL_CYCLE'),('PERCUSSIVE_EXTENDED_RANGE',),local_cycle=(3,3,2,3,5)),
        'prog_synth':Performer('prog_synth','Prog Synth Recruit',('LEAD_KEYS',),('TIMBRAL_EXPERIMENTATION',),('SYNTH_SWELL','CHOIR_PAD','FILTER_MOVEMENT','NOISE_BED'),('ANALOG_SWELL','CHOIR','FILTER_MOTION')),
        'death_drummer':Performer('death_drummer','Death Metal Drummer',('DRUMS',),('EXTREME_DENSITY',),('DOUBLE_KICK_LOCK','BLAST_BEAT','DEATH_HALF_TIME','TOM_FILL'),('EXTREME_METAL_KIT',)),
    }
    return ExpressionRegistries(traits,techniques,functions,performers,standard_technique_handlers())

def build_thrash_chimera_opportunities(host:HostComposition)->tuple[Opportunity,...]:
    out=[]
    def add(oid,sid,funcs,roles,budget=1.0,converge=True):
        a,b=_section_ticks(host,sid)
        out.append(Opportunity(oid,sid,a,b,tuple(funcs),tuple(roles),budget,b if converge else None))
    add('doom_chorus_1','CHORUS_1',('COUNTER_MELODY','EMOTIONAL_BED','RESOLUTION'),('LEAD_KEYS',),0.75)
    add('doom_chorus_2','CHORUS_2',('COUNTER_MELODY','EMOTIONAL_BED','RESOLUTION'),('LEAD_KEYS',),0.75)
    add('doom_final','FINAL_CHORUS',('COUNTER_MELODY','EMOTIONAL_BED','RESOLUTION'),('LEAD_KEYS',),1.0)
    add('bass_verse_1','VERSE_1',('COUNTER_RHYTHM','GROOVE_DESTABILIZATION','CONVERGENCE_SETUP'),('BASS',),1.0)
    add('bass_verse_2','VERSE_2',('COUNTER_RHYTHM','GROOVE_DESTABILIZATION','CONVERGENCE_SETUP'),('BASS',),1.0)
    add('bass_final','FINAL_CHORUS',('COUNTER_RHYTHM','CONVERGENCE_SETUP'),('BASS',),1.0)
    add('prog_pre','PRE_CHORUS',('TEXTURAL_ATMOSPHERE','SECTION_ILLUMINATION','DRAMATIC_REVEAL'),('LEAD_KEYS',),0.8)
    add('prog_chorus','CHORUS_1',('TEXTURAL_ATMOSPHERE','SECTION_ILLUMINATION'),('LEAD_KEYS',),0.8)
    add('prog_final','FINAL_CHORUS',('TEXTURAL_ATMOSPHERE','SECTION_ILLUMINATION','DRAMATIC_REVEAL'),('LEAD_KEYS',),0.8)
    add('death_verse','VERSE_1',('PROPULSION',),('DRUMS',),1.0)
    add('death_pre','PRE_CHORUS',('ESCALATION',),('DRUMS',),1.0)
    add('death_chorus','CHORUS_1',('DENSE_SUPPORT',),('DRUMS',),1.0)
    add('death_break','BREAK',('SECTION_GRAVITY',),('DRUMS',),1.0)
    add('death_outro','OUTRO',('TRANSITION_DRIVE',),('DRUMS',),1.0)
    total_end=host.sections[-1].end_bar*BAR
    out.append(Opportunity('sat_lead','INTRO',0,total_end,('COUNTER_MELODY','TEXTURAL_ATMOSPHERE','SECTION_ILLUMINATION'),('LEAD_KEYS',),1.0,total_end))
    out.append(Opportunity('sat_bass','INTRO',0,total_end,('COUNTER_RHYTHM','GROOVE_DESTABILIZATION'),('BASS',),1.0,total_end))
    out.append(Opportunity('sat_drums','INTRO',0,total_end,('ESCALATION','PROPULSION','SECTION_GRAVITY'),('DRUMS',),1.0,total_end))
    return tuple(out)

def _opp_map(host): return {o.id:o for o in build_thrash_chimera_opportunities(host)}

def _req(perf,trait,tech,func,opp,role,rhythm='HOST_CLOCK',harm='HOST_HARMONY',timbre='NATIVE',density='WITHIN_BUDGET'):
    return ExpressionRequest(perf,trait,tech,func,opp,role,rhythm,harm,timbre,density)

def build_thrash_chimera_expression_sets()->dict[str,tuple[ExpressionRequest,...]]:
    B=(
        _req('doom_guitarist','LONG_SUSTAIN','SUSTAINED_MELODIC_LINE','COUNTER_MELODY','doom_chorus_1','LEAD_KEYS',timbre='DOOM_GUITAR'),
        _req('doom_guitarist','LONG_SUSTAIN','SUSTAINED_MELODIC_LINE','RESOLUTION','doom_chorus_2','LEAD_KEYS',timbre='DOOM_GUITAR'),
        _req('doom_guitarist','LONG_SUSTAIN','DRONE_ANCHOR','EMOTIONAL_BED','doom_final','LEAD_KEYS',timbre='DOOM_GUITAR'),
    )
    C=(
        _req('djent_bassist','PERCUSSIVE_THUMB','ROLE_LOCAL_CYCLE','COUNTER_RHYTHM','bass_verse_1','BASS','REPLACE_ROLE_WINDOW',timbre='PERCUSSIVE_EXTENDED_RANGE'),
        _req('djent_bassist','PERCUSSIVE_THUMB','THUMB_ATTACK','GROOVE_DESTABILIZATION','bass_verse_1','BASS',timbre='PERCUSSIVE_EXTENDED_RANGE'),
        _req('djent_bassist','PERCUSSIVE_THUMB','ROLE_LOCAL_CYCLE','COUNTER_RHYTHM','bass_verse_2','BASS','REPLACE_ROLE_WINDOW',timbre='PERCUSSIVE_EXTENDED_RANGE'),
        _req('djent_bassist','PERCUSSIVE_THUMB','SLAP_POP','CONVERGENCE_SETUP','bass_final','BASS',timbre='PERCUSSIVE_EXTENDED_RANGE'),
    )
    D=(
        _req('prog_synth','TIMBRAL_EXPERIMENTATION','SYNTH_SWELL','DRAMATIC_REVEAL','prog_pre','LEAD_KEYS',timbre='ANALOG_SWELL'),
        _req('prog_synth','TIMBRAL_EXPERIMENTATION','CHOIR_PAD','TEXTURAL_ATMOSPHERE','prog_chorus','LEAD_KEYS',timbre='CHOIR_PAD'),
        _req('prog_synth','TIMBRAL_EXPERIMENTATION','FILTER_MOVEMENT','SECTION_ILLUMINATION','prog_final','LEAD_KEYS',timbre='FILTER_MOTION'),
    )
    E=(
        _req('death_drummer','EXTREME_DENSITY','DOUBLE_KICK_LOCK','PROPULSION','death_verse','DRUMS','REPLACE_ROLE_WINDOW',harm='N/A',timbre='EXTREME_METAL_KIT'),
        _req('death_drummer','EXTREME_DENSITY','BLAST_BEAT','ESCALATION','death_pre','DRUMS','REPLACE_ROLE_WINDOW',harm='N/A',timbre='EXTREME_METAL_KIT'),
        _req('death_drummer','EXTREME_DENSITY','DOUBLE_KICK_LOCK','DENSE_SUPPORT','death_chorus','DRUMS','REPLACE_ROLE_WINDOW',harm='N/A',timbre='EXTREME_METAL_KIT'),
        _req('death_drummer','EXTREME_DENSITY','DEATH_HALF_TIME','SECTION_GRAVITY','death_break','DRUMS','REPLACE_ROLE_WINDOW',harm='N/A',timbre='EXTREME_METAL_KIT'),
        _req('death_drummer','EXTREME_DENSITY','TOM_FILL','TRANSITION_DRIVE','death_outro','DRUMS','REPLACE_ROLE_WINDOW',harm='N/A',timbre='EXTREME_METAL_KIT'),
    )
    F=B+C+D+E
    G=(
        _req('doom_guitarist','LONG_SUSTAIN','DRONE_ANCHOR','COUNTER_MELODY','sat_lead','LEAD_KEYS',timbre='DOOM_GUITAR',density='SATURATION_CONTROL'),
        _req('doom_guitarist','LONG_SUSTAIN','SUSTAINED_MELODIC_LINE','COUNTER_MELODY','sat_lead','LEAD_KEYS',timbre='DOOM_GUITAR',density='SATURATION_CONTROL'),
        _req('prog_synth','TIMBRAL_EXPERIMENTATION','CHOIR_PAD','TEXTURAL_ATMOSPHERE','sat_lead','LEAD_KEYS',timbre='CHOIR_PAD',density='SATURATION_CONTROL'),
        _req('prog_synth','TIMBRAL_EXPERIMENTATION','NOISE_BED','SECTION_ILLUMINATION','sat_lead','LEAD_KEYS',timbre='NOISE_BED',density='SATURATION_CONTROL'),
        _req('djent_bassist','PERCUSSIVE_THUMB','ROLE_LOCAL_CYCLE','COUNTER_RHYTHM','sat_bass','BASS','REPLACE_ROLE_WINDOW',timbre='PERCUSSIVE_EXTENDED_RANGE',density='SATURATION_CONTROL'),
        _req('djent_bassist','PERCUSSIVE_THUMB','THUMB_ATTACK','GROOVE_DESTABILIZATION','sat_bass','BASS',timbre='PERCUSSIVE_EXTENDED_RANGE',density='SATURATION_CONTROL'),
        _req('djent_bassist','PERCUSSIVE_THUMB','GHOST_NOTE','COUNTER_RHYTHM','sat_bass','BASS',timbre='PERCUSSIVE_EXTENDED_RANGE',density='SATURATION_CONTROL'),
        _req('death_drummer','EXTREME_DENSITY','BLAST_BEAT','ESCALATION','sat_drums','DRUMS','REPLACE_ROLE_WINDOW',harm='N/A',timbre='EXTREME_METAL_KIT',density='SATURATION_CONTROL'),
        _req('death_drummer','EXTREME_DENSITY','DOUBLE_KICK_LOCK','PROPULSION','sat_drums','DRUMS',harm='N/A',timbre='EXTREME_METAL_KIT',density='SATURATION_CONTROL'),
    )
    return {'A':(), 'B':B, 'C':C, 'D':D, 'E':E, 'F':F, 'G':G}

def _resolve_set(host:HostComposition, requests:tuple[ExpressionRequest,...])->tuple[ResolvedExpression,...]:
    regs=build_thrash_chimera_registries(); opps=_opp_map(host)
    resolved=[]
    for req in requests:
        resolved.append(resolve_expression(host,req,regs,opps[req.opportunity_id]))
    return tuple(resolved)

def build_thrash_chimera_variants()->dict[str,HostComposition]:
    host=build_thrash_host(); sets=build_thrash_chimera_expression_sets(); out={'A':host}
    frozen=('tempo','meter','sections','host_riff','tonal_center')
    for key in 'BCDEFG':
        exprs=_resolve_set(host,sets[key])
        variant=apply_expressions(host,exprs)
        assert_frozen_dimensions(host,variant,frozen,())
        out[key]=variant
    return out

def chimera_variant_metrics(key:str)->dict[str,float|int]:
    host=build_thrash_host(); sets=build_thrash_chimera_expression_sets()
    if key=='A': return {'density':0.0,'saturation_controls':0}
    resolved=_resolve_set(host,sets[key])
    total_span=max(1,host.sections[-1].end_bar*BAR)
    occupied=sum(e.duration_ticks for r in resolved for e in r.events)
    return {
        'density':occupied/total_span,
        'saturation_controls':sum(1 for r in sets[key] if r.density_policy=='SATURATION_CONTROL'),
    }

CHIMERA_PERFORMER_PROGRAMS={
    'doom_guitarist':29,
    'djent_bassist':36,
    'prog_synth':88,
    'death_drummer':None,
}

def resolve_thrash_chimera_variant(key:str):
    if key not in 'ABCDEFG': raise ValueError('unknown THRASH CHIMERA variant')
    host=build_thrash_host()
    requests=build_thrash_chimera_expression_sets()[key]
    expressions=_resolve_set(host,requests) if requests else ()
    variant=apply_expressions(host,expressions) if expressions else host
    assert_frozen_dimensions(host,variant,('tempo','meter','sections','host_riff','tonal_center'),())
    return host,variant,expressions
