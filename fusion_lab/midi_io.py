from __future__ import annotations
import hashlib, json
from pathlib import Path
from collections import Counter
import mido
from .model import CANONICAL_ROLES, HostComposition, Role, RoleTrack
from .expression_model import ResolvedExpression

FILENAMES={
 'DRUMS':'drums.mid','BASS':'bass.mid','RHYTHM_GUITAR':'rhythm_guitar.mid','LEAD_KEYS':'lead_keys.mid','VOCALS':'vocals.mid'
}

def _messages_for_track(host:HostComposition, role:Role):
    track=host.tracks[role]
    events=[]
    events.append((0,0,mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(host.bpm),time=0)))
    events.append((0,1,mido.MetaMessage('time_signature',numerator=host.numerator,denominator=host.denominator,time=0)))
    if track.program is not None and not track.percussion:
        events.append((0,2,mido.Message('program_change',program=track.program,channel=track.events[0].channel if track.events else 0,time=0)))
    for e in track.events:
        events.append((e.start_tick,10,mido.Message('note_on',note=e.note,velocity=e.velocity,channel=e.channel,time=0)))
        events.append((e.start_tick+e.duration_ticks,5,mido.Message('note_off',note=e.note,velocity=0,channel=e.channel,time=0)))
    events.sort(key=lambda item:(item[0],item[1],getattr(item[2],'channel',-1),getattr(item[2],'note',-1),getattr(item[2],'velocity',-1)))
    last=0; out=[]
    for tick,_,msg in events:
        out.append(msg.copy(time=tick-last)); last=tick
    out.append(mido.MetaMessage('end_of_track',time=0))
    return out

def write_role_midis(host:HostComposition,out_dir:Path)->dict[Role,Path]:
    out_dir=Path(out_dir); out_dir.mkdir(parents=True,exist_ok=True)
    result={}
    for role in CANONICAL_ROLES:
        mf=mido.MidiFile(type=0,ticks_per_beat=host.ticks_per_beat)
        tr=mido.MidiTrack(); mf.tracks.append(tr); tr.extend(_messages_for_track(host,role))
        path=out_dir/FILENAMES[role]; mf.save(path); result[role]=path
    return result

def normalized_event_signature(path:Path)->str:
    mf=mido.MidiFile(path)
    absolute=0; rows=[]
    for msg in mido.merge_tracks(mf.tracks):
        absolute += msg.time
        data=msg.dict().copy(); data.pop('time',None)
        rows.append((absolute,tuple(sorted(data.items()))))
    payload=json.dumps(rows,separators=(',',':'),default=list)
    return hashlib.sha256(payload.encode()).hexdigest()

def _host_structural_payload(host:HostComposition):
    return {
      'id':host.id,'bpm':host.bpm,'meter':[host.numerator,host.denominator],
      'ticks_per_beat':host.ticks_per_beat,'tonal_center':host.tonal_center,
      'sections':[(s.id,s.start_bar,s.bars) for s in host.sections],
      'tracks':{role:[(e.start_tick,e.duration_ticks,e.note,e.velocity,e.channel,e.articulation,e.function) for e in host.tracks[role].events] for role in CANONICAL_ROLES},
    }

def host_structural_signature(host:HostComposition)->str:
    payload=json.dumps(_host_structural_payload(host),sort_keys=True,separators=(',',':'))
    return hashlib.sha256(payload.encode()).hexdigest()

def host_manifest(host:HostComposition,midi_paths:dict[Role,Path])->dict:
    return {
      'schema':'polly.fusion-lab.host-manifest.v1','host_id':host.id,'bpm':host.bpm,
      'meter':[host.numerator,host.denominator],'tonal_center':host.tonal_center,
      'role_signatures':{role:normalized_event_signature(midi_paths[role]) for role in CANONICAL_ROLES},
      'host_structural_signature':host_structural_signature(host),
      'midi_files':{role:Path(midi_paths[role]).name for role in CANONICAL_ROLES},
    }

def _messages_for_roletrack(host:HostComposition, track:RoleTrack):
    events=[]
    events.append((0,0,mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(host.bpm),time=0)))
    events.append((0,1,mido.MetaMessage('time_signature',numerator=host.numerator,denominator=host.denominator,time=0)))
    if track.program is not None and not track.percussion:
        channel=track.events[0].channel if track.events else 0
        events.append((0,2,mido.Message('program_change',program=track.program,channel=channel,time=0)))
    for e in track.events:
        events.append((e.start_tick,10,mido.Message('note_on',note=e.note,velocity=e.velocity,channel=e.channel,time=0)))
        events.append((e.start_tick+e.duration_ticks,5,mido.Message('note_off',note=e.note,velocity=0,channel=e.channel,time=0)))
    events.sort(key=lambda item:(item[0],item[1],getattr(item[2],'channel',-1),getattr(item[2],'note',-1),getattr(item[2],'velocity',-1)))
    last=0; out=[]
    for tick,_,msg in events:
        out.append(msg.copy(time=tick-last)); last=tick
    out.append(mido.MetaMessage('end_of_track',time=0))
    return out

def _write_named_track(host:HostComposition, track:RoleTrack, path:Path):
    mf=mido.MidiFile(type=0,ticks_per_beat=host.ticks_per_beat)
    tr=mido.MidiTrack(); mf.tracks.append(tr); tr.extend(_messages_for_roletrack(host,track))
    path.parent.mkdir(parents=True,exist_ok=True); mf.save(path)

def write_layered_variant_midis(
    host:HostComposition,
    variant:HostComposition,
    expressions:tuple[ResolvedExpression,...],
    out_dir:Path,
    performer_programs:dict[str,int|None],
)->dict[str,Path]:
    out_dir=Path(out_dir); out_dir.mkdir(parents=True,exist_ok=True)
    result:dict[str,Path]={}
    expression_by_role:dict[str,list]= {}
    expression_by_performer:dict[str,list]= {}
    for x in expressions:
        expression_by_role.setdefault(x.role_family,[]).extend(x.events)
        expression_by_performer.setdefault(x.performer_id,[]).extend(x.events)
    for role in CANONICAL_ROLES:
        counter=Counter(expression_by_role.get(role,[]))
        base=[]
        for event in variant.tracks[role].events:
            if counter[event] > 0:
                counter[event]-=1
            else:
                base.append(event)
        src=variant.tracks[role]
        track=RoleTrack(role,tuple(base),src.program,src.percussion)
        path=out_dir/f"host_{FILENAMES[role]}"
        _write_named_track(host,track,path); result[f'host_{role}']=path
    for performer_id in sorted(expression_by_performer):
        events=tuple(sorted(expression_by_performer[performer_id],key=lambda e:(e.start_tick,e.channel,e.note,e.duration_ticks)))
        percussion=all(e.channel==9 for e in events)
        program=performer_programs.get(performer_id)
        role=next(x.role_family for x in expressions if x.performer_id==performer_id)
        track=RoleTrack(role,events,program,percussion)
        path=out_dir/f'performer_{performer_id}.mid'
        _write_named_track(host,track,path); result[f'performer_{performer_id}']=path
    return result
