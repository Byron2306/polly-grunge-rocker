from __future__ import annotations
from .model import HostComposition, NoteEvent, RoleTrack, Section

TPQ=480
FORM_BARS=(4,8,4,8,4,8,4,8,8,4,8,4)
SECTION_IDS=('intro','verse1','pre1','chorus1','turnaround','verse2','pre2','chorus2','solo','build','final_chorus','outro')
VERSE_HARMONY=('E5','D5','A5','E5','E5','D5','A5','B5')
PRECHORUS_HARMONY=('A','B','C#m','B')
CHORUS_HARMONY=('E','B','C#m','A','E','B','A','B')

ROOTS={'E':40,'D':38,'A':45,'B':47,'C#':49}

def _root(symbol:str)->int:
    name='C#' if symbol.startswith('C#') else symbol[0]
    return ROOTS[name]

def _sections():
    out=[]; bar=0
    for sid,bars in zip(SECTION_IDS,FORM_BARS):
        out.append(Section(sid,bar,bars)); bar+=bars
    return tuple(out)

def _harmony_for(section:str,bars:int):
    if section.startswith('verse'): base=VERSE_HARMONY
    elif section.startswith('pre'): base=PRECHORUS_HARMONY
    elif 'chorus' in section: base=CHORUS_HARMONY
    elif section in {'solo','build'}: base=CHORUS_HARMONY
    else: base=VERSE_HARMONY
    return tuple(base[i%len(base)] for i in range(bars))

def _drums(sections):
    ev=[]
    for s in sections:
        for b in range(s.bars):
            bar=s.start_bar+b; base=bar*4*TPQ
            chorus='chorus' in s.id
            for eighth in range(8):
                ev.append(NoteEvent(base+eighth*(TPQ//2),TPQ//8,42,72,9,'STRAIGHT_HAT'))
            for beat in (1,3): ev.append(NoteEvent(base+beat*TPQ,TPQ//8,38,105,9,'BACKBEAT'))
            for beat in (0,2): ev.append(NoteEvent(base+beat*TPQ,TPQ//8,36,100,9,'ROCK_KICK'))
            if chorus: ev.append(NoteEvent(base,TPQ//4,49,110,9,'CHORUS_CRASH'))
            if b==s.bars-1:
                for i,n in enumerate((45,47,50)): ev.append(NoteEvent(base+3*TPQ+i*(TPQ//3),TPQ//8,n,92,9,'TRANSITION_FILL'))
    return tuple(sorted(ev,key=lambda e:(e.start_tick,e.note,e.velocity)))

def _rhythm(sections):
    ev=[]
    for s in sections:
        harmony=_harmony_for(s.id,s.bars)
        for i,chord in enumerate(harmony):
            base=(s.start_bar+i)*4*TPQ; root=_root(chord); fifth=root+7
            if 'chorus' in s.id:
                dur=4*TPQ
                for n in (root,fifth): ev.append(NoteEvent(base,dur,n,104,2,'OPEN_POWER_CHORD','HARMONIC_SUPPORT'))
            else:
                for beat in (0,1,2):
                    start=base+beat*TPQ
                    for n in (root,fifth): ev.append(NoteEvent(start,TPQ//2,n,90,2,'GLAM_CHUG','HARMONIC_SUPPORT'))
                for n in (root,fifth): ev.append(NoteEvent(base+3*TPQ,TPQ,n,102,2,'OPEN_POWER_CHORD','HARMONIC_SUPPORT'))
    return tuple(sorted(ev,key=lambda e:(e.start_tick,e.note)))

def _bass(sections):
    ev=[]
    for s in sections:
        for i,chord in enumerate(_harmony_for(s.id,s.bars)):
            base=(s.start_bar+i)*4*TPQ; root=_root(chord)-12
            for eighth in range(8):
                note=root if eighth<7 else root+7
                ev.append(NoteEvent(base+eighth*(TPQ//2),TPQ//2,note,82,1,'EIGHTH_PUMP','GROOVE_ANCHOR'))
    return tuple(ev)

def _lead(sections):
    ev=[]
    hook=(64,68,71,68,66,64)
    for s in sections:
        if 'chorus' in s.id or s.id=='solo':
            start=s.start_bar*4*TPQ
            repeats=max(1,(s.bars*4)//len(hook))
            idx=0
            for r in range(repeats):
                for n in hook:
                    art='BEND_VIBRATO' if idx%6==1 else ('TAPPING_FLOURISH' if s.id=='solo' and idx%9==0 else 'GLAM_HOOK')
                    ev.append(NoteEvent(start+idx*TPQ,TPQ,n,96,3,art,'MELODIC_LEAD'))
                    idx+=1
                    if start+idx*TPQ >= (s.start_bar+s.bars)*4*TPQ: break
                if start+idx*TPQ >= (s.start_bar+s.bars)*4*TPQ: break
        elif s.id.startswith('pre'):
            start=s.start_bar*4*TPQ
            for i,n in enumerate((64,66,68,71)): ev.append(NoteEvent(start+i*TPQ*4,TPQ*2,n,80,3,'PRECHORUS_LIFT','MELODIC_LEAD'))
    return tuple(ev)

def _vocals(sections):
    ev=[]
    phrase=(64,66,68,66)
    for s in sections:
        if s.id.startswith('verse') or 'chorus' in s.id:
            start=s.start_bar*4*TPQ
            for bar in range(s.bars):
                n=phrase[bar%len(phrase)] + (4 if 'chorus' in s.id else 0)
                ev.append(NoteEvent(start+bar*4*TPQ,TPQ*3,n,76,4,'MELODY_GUIDE','VOCAL_PHRASE'))
    return tuple(ev)

def build_glamasaurus_rex()->HostComposition:
    sections=_sections()
    tracks={
        'DRUMS':RoleTrack('DRUMS',_drums(sections),None,True),
        'BASS':RoleTrack('BASS',_bass(sections),33,False),
        'RHYTHM_GUITAR':RoleTrack('RHYTHM_GUITAR',_rhythm(sections),30,False),
        'LEAD_KEYS':RoleTrack('LEAD_KEYS',_lead(sections),29,False),
        'VOCALS':RoleTrack('VOCALS',_vocals(sections),54,False),
    }
    return HostComposition('host-001-glamasaurus-rex',138,4,4,TPQ,'E',sections,tracks)
