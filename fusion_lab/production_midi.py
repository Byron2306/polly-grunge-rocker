from __future__ import annotations
import hashlib, random
from pathlib import Path
from typing import Mapping
import mido
from .model import HostComposition, NoteEvent, RoleTrack
from .production_model import HumanizationProfile, InstrumentProfile

LAYER_ROLE={'rhythm_guitar_L':'RHYTHM_GUITAR','rhythm_guitar_R':'RHYTHM_GUITAR','bass':'BASS','drums':'DRUMS','lead_guitar':'LEAD_KEYS'}

def _seed_for(profile:HumanizationProfile,layer:str)->int:
    return profile.seed ^ int(hashlib.sha256(layer.encode()).hexdigest()[:8],16)

def humanize_events(host:HostComposition,events:tuple[NoteEvent,...],profile:HumanizationProfile,layer:str)->tuple[NoteEvent,...]:
    rng=random.Random(_seed_for(profile,layer))
    ms_per_tick=60000.0/(host.bpm*host.ticks_per_beat)
    timing_ms=profile.double_track_timing_ms if layer.startswith('rhythm_guitar_') else profile.timing_ms
    velocity_delta=profile.double_track_velocity_delta if layer.startswith('rhythm_guitar_') else profile.velocity_delta
    max_tick=max(0,round(timing_ms/ms_per_tick))
    onset_jitter={}
    out=[]
    for e in events:
        if e.start_tick not in onset_jitter:
            onset_jitter[e.start_tick]=rng.randint(-max_tick,max_tick) if max_tick else 0
        jitter=onset_jitter[e.start_tick]
        velocity=max(1,min(127,e.velocity+(rng.randint(-velocity_delta,velocity_delta) if velocity_delta else 0)))
        out.append(NoteEvent(max(0,e.start_tick+jitter),e.duration_ticks,e.note,velocity,e.channel,e.articulation,e.function))
    return tuple(sorted(out,key=lambda e:(e.start_tick,e.note,e.duration_ticks,e.velocity)))

def _messages(host:HostComposition,track:RoleTrack,instrument:InstrumentProfile):
    events=[(0,0,mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(host.bpm),time=0)),(0,1,mido.MetaMessage('time_signature',numerator=host.numerator,denominator=host.denominator,time=0))]
    last_art=None
    for e in track.events:
        art_name=e.articulation or 'SUSTAIN'
        if art_name not in instrument.articulations:
            raise ValueError(f'PRODUCTION_UNSUPPORTED_ARTICULATION: {instrument.id}:{art_name}')
        art=instrument.articulations[art_name]
        channel=art.midi_channel if art.midi_channel is not None else e.channel
        if art.keyswitch is not None and art_name!=last_art:
            ks_tick=max(0,e.start_tick-host.ticks_per_beat//16)
            events.append((ks_tick,2,mido.Message('note_on',note=art.keyswitch,velocity=100,channel=channel,time=0)))
            events.append((ks_tick+max(1,host.ticks_per_beat//32),3,mido.Message('note_off',note=art.keyswitch,velocity=0,channel=channel,time=0)))
            last_art=art_name
        velocity=max(art.velocity_min,min(art.velocity_max,e.velocity))
        events.append((e.start_tick,10,mido.Message('note_on',note=e.note,velocity=velocity,channel=channel,time=0)))
        events.append((e.start_tick+e.duration_ticks,5,mido.Message('note_off',note=e.note,velocity=0,channel=channel,time=0)))
    events.sort(key=lambda x:(x[0],x[1],getattr(x[2],'channel',-1),getattr(x[2],'note',-1)))
    last=0; out=[]
    for tick,_,msg in events: out.append(msg.copy(time=tick-last)); last=tick
    out.append(mido.MetaMessage('end_of_track',time=0)); return out

def _save_track(host:HostComposition,track:RoleTrack,instrument:InstrumentProfile,path:Path)->Path:
    mf=mido.MidiFile(type=0,ticks_per_beat=host.ticks_per_beat)
    tr=mido.MidiTrack(); mf.tracks.append(tr); tr.extend(_messages(host,track,instrument))
    path.parent.mkdir(parents=True,exist_ok=True); mf.save(path); return path

def write_articulation_midis(host:HostComposition,out_dir:Path,layer:str,profile:HumanizationProfile,instrument:InstrumentProfile)->dict[str,Path]:
    if layer not in LAYER_ROLE: raise ValueError(f'PRODUCTION_UNKNOWN_LAYER: {layer}')
    source=host.tracks[LAYER_ROLE[layer]]
    humanized=humanize_events(host,source.events,profile,layer)
    grouped={}
    for e in humanized:
        art=e.articulation or 'SUSTAIN'
        if art not in instrument.articulations:
            raise ValueError(f'PRODUCTION_UNSUPPORTED_ARTICULATION: {instrument.id}:{art}')
        grouped.setdefault(art,[]).append(e)
    result={}
    for art,events in sorted(grouped.items()):
        track=RoleTrack(source.role,tuple(events),source.program,source.percussion)
        safe=''.join(ch.lower() if ch.isalnum() else '_' for ch in art).strip('_')
        result[art]=_save_track(host,track,instrument,Path(out_dir)/f'{layer}__{safe}.mid')
    return result

def write_production_midis(host:HostComposition,out_dir:Path,humanization_profiles:Mapping[str,HumanizationProfile],instrument_profiles:Mapping[str,InstrumentProfile])->dict[str,Path]:
    out_dir=Path(out_dir); out_dir.mkdir(parents=True,exist_ok=True); result={}
    for layer,role in LAYER_ROLE.items():
        if layer not in humanization_profiles: raise ValueError(f'PRODUCTION_MISSING_HUMANIZATION_PROFILE: {layer}')
        if layer not in instrument_profiles: raise ValueError(f'PRODUCTION_MISSING_INSTRUMENT_PROFILE: {layer}')
        source=host.tracks[role]
        track=RoleTrack(source.role,humanize_events(host,source.events,humanization_profiles[layer],layer),source.program,source.percussion)
        result[layer]=_save_track(host,track,instrument_profiles[layer],out_dir/f'{layer}.mid')
    return result
