from __future__ import annotations
import hashlib, json, os, shutil, subprocess
from pathlib import Path
from typing import Mapping
from .production_model import ProductionConfig, ToneProfile, InstrumentProfile, ArticulationMap, ToneStage

def _sha256(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def _expand_path(value:str)->Path:
    return Path(os.path.expandvars(os.path.expanduser(value)))

def load_instrument_profiles(path:Path)->dict[str,InstrumentProfile]:
    raw=json.loads(Path(path).read_text())
    out={}
    for layer,row in raw['layers'].items():
        arts={name:ArticulationMap(name=name,keyswitch=cfg.get('keyswitch'),midi_channel=cfg.get('midi_channel'),velocity_min=cfg.get('velocity_min',1),velocity_max=cfg.get('velocity_max',127)) for name,cfg in row['articulations'].items()}
        out[layer]=InstrumentProfile(row['id'],row['role'],_expand_path(row['sfz_path']),arts,row['source_id'],row.get('source_version'))
    return out

def load_tone_profiles(path:Path)->dict[str,ToneProfile]:
    raw=json.loads(Path(path).read_text()); out={}
    for layer,row in raw['layers'].items():
        stages=tuple(ToneStage(s['kind'],s.get('executable'),tuple(s.get('args',())),_expand_path(s['asset_path']) if s.get('asset_path') else None) for s in row.get('stages',()))
        out[layer]=ToneProfile(row['id'],stages,float(row.get('pan',0.0)),float(row.get('width',1.0)))
    return out

def check_production_dependencies(config:ProductionConfig, instruments:Mapping[str,InstrumentProfile]|None=None, tone_profiles:Mapping[str,ToneProfile]|None=None)->None:
    if shutil.which(config.sfizz_executable) is None:
        raise RuntimeError('PRODUCTION_MISSING_SFIZZ_RENDER')
    for instrument in (instruments or {}).values():
        if not instrument.sfz_path.is_file(): raise RuntimeError(f'PRODUCTION_MISSING_SFZ: {instrument.sfz_path}')
    for profile in (tone_profiles or {}).values():
        for stage in profile.stages:
            if stage.executable and shutil.which(stage.executable) is None: raise RuntimeError(f'PRODUCTION_MISSING_TONE_EXECUTABLE: {stage.executable}')
            if stage.asset_path and not stage.asset_path.is_file(): raise RuntimeError(f'PRODUCTION_MISSING_TONE_ASSET: {stage.asset_path}')

def render_sfz(midi:Path,sfz:Path,wav:Path,*,sample_rate:int,executable:str='sfizz_render')->None:
    exe=shutil.which(executable)
    if exe is None: raise RuntimeError('PRODUCTION_MISSING_SFIZZ_RENDER')
    if not Path(sfz).is_file(): raise RuntimeError(f'PRODUCTION_MISSING_SFZ: {sfz}')
    if not Path(midi).is_file(): raise RuntimeError(f'PRODUCTION_MISSING_MIDI: {midi}')
    Path(wav).parent.mkdir(parents=True,exist_ok=True)
    cmd=[exe,'--sfz',str(sfz),'--midi',str(midi),'--wav',str(wav),'--samplerate',str(sample_rate),'--use-eot']
    subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

def apply_tone_chain(source:Path,destination:Path,profile:ToneProfile)->None:
    source=Path(source); destination=Path(destination)
    if not source.is_file(): raise RuntimeError(f'PRODUCTION_MISSING_SOURCE_WAV: {source}')
    destination.parent.mkdir(parents=True,exist_ok=True)
    if not profile.stages:
        shutil.copyfile(source,destination); return
    current=source; temps=[]
    for i,stage in enumerate(profile.stages):
        if not stage.executable: raise RuntimeError(f'PRODUCTION_UNSUPPORTED_TONE_STAGE: {stage.kind}')
        exe=shutil.which(stage.executable)
        if exe is None: raise RuntimeError(f'PRODUCTION_MISSING_TONE_EXECUTABLE: {stage.executable}')
        if stage.asset_path and not stage.asset_path.is_file(): raise RuntimeError(f'PRODUCTION_MISSING_TONE_ASSET: {stage.asset_path}')
        out=destination if i==len(profile.stages)-1 else destination.with_suffix(f'.stage{i}.wav')
        args=[a.replace('{in}',str(current)).replace('{out}',str(out)).replace('{asset}',str(stage.asset_path or '')) for a in stage.args]
        subprocess.run([exe,*args],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if current != source: temps.append(current)
        current=out
    for p in temps:
        try: Path(p).unlink()
        except FileNotFoundError: pass

def mix_production_stems(stems:Mapping[str,Path],mix_path:Path)->None:
    if not stems: raise RuntimeError('PRODUCTION_NO_STEMS')
    for name,path in stems.items():
        if not Path(path).is_file(): raise RuntimeError(f'PRODUCTION_MISSING_STEM: {name}')
    ffmpeg=shutil.which('ffmpeg')
    if ffmpeg is None: raise RuntimeError('PRODUCTION_MISSING_MIXER: ffmpeg')
    cmd=[ffmpeg,'-y']
    for path in stems.values(): cmd += ['-i',str(path)]
    cmd += ['-filter_complex',f'amix=inputs={len(stems)}:normalize=0','-c:a','pcm_s16le',str(mix_path)]
    subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

def production_manifest(*,host_id:str,renderer_version:str,instruments:Mapping[str,InstrumentProfile],tone_profiles:Mapping[str,ToneProfile],humanization_seed:int,structural_signature:str,stems:Mapping[str,Path],mix_path:Path|None=None)->dict:
    data={
      'schema':'polly.fusion-lab.production-manifest.v1','host_id':host_id,'renderer_version':renderer_version,
      'humanization_seed':humanization_seed,'structural_signature':structural_signature,
      'instruments':{k:{'id':v.id,'source_id':v.source_id,'source_version':v.source_version,'sfz_path':str(v.sfz_path)} for k,v in sorted(instruments.items())},
      'tone_profiles':{k:{'id':v.id,'pan':v.pan,'width':v.width,'stages':[s.kind for s in v.stages]} for k,v in sorted(tone_profiles.items())},
      'stems':{k:{'path':str(v),'sha256':_sha256(Path(v)) if Path(v).is_file() else None} for k,v in sorted(stems.items())},
    }
    if mix_path is not None: data['mix']={'path':str(mix_path),'sha256':_sha256(Path(mix_path)) if Path(mix_path).is_file() else None}
    payload=json.dumps(data,sort_keys=True,separators=(',',':'))
    data['manifest_sha256']=hashlib.sha256(payload.encode()).hexdigest()
    return data
