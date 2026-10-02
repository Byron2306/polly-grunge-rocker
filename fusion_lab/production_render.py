from __future__ import annotations
import hashlib, json, math, os, shutil, subprocess
from pathlib import Path
from typing import Mapping
from .production_model import ProductionConfig, ToneProfile, InstrumentProfile, ArticulationMap, ToneStage, ToneControls

def _sha256(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def _expand_path(value:str)->Path:
    return Path(os.path.expandvars(os.path.expanduser(value)))

def load_instrument_profiles(path:Path)->dict[str,InstrumentProfile]:
    raw=json.loads(Path(path).read_text()); out={}
    for layer,row in raw['layers'].items():
        arts={name:ArticulationMap(name=name,keyswitch=cfg.get('keyswitch'),midi_channel=cfg.get('midi_channel'),velocity_min=cfg.get('velocity_min',1),velocity_max=cfg.get('velocity_max',127),sfz_path=_expand_path(cfg['sfz_path']) if cfg.get('sfz_path') else None) for name,cfg in row['articulations'].items()}
        out[layer]=InstrumentProfile(row['id'],row['role'],_expand_path(row['sfz_path']),arts,row['source_id'],row.get('source_version'))
    return out

def _load_controls(row:dict)->ToneControls|None:
    raw=row.get('controls')
    if raw is None: return None
    cab=raw.get('cabinet_ir')
    return ToneControls(
        tuning_profile=raw.get('tuning_profile','E_STANDARD'),
        pitch_shift_semitones=int(raw.get('pitch_shift_semitones',0)),
        boost_drive=float(raw.get('boost_drive',0.0)),
        boost_level=float(raw.get('boost_level',0.0)),
        amp_gain=float(raw.get('amp_gain',5.0)),
        distortion=float(raw.get('distortion',0.0)),
        bass=float(raw.get('bass',5.0)),
        mid=float(raw.get('mid',5.0)),
        treble=float(raw.get('treble',5.0)),
        presence=float(raw.get('presence',5.0)),
        master=float(raw.get('master',5.0)),
        reverb_mix=float(raw.get('reverb_mix',0.0)),
        reverb_decay_s=float(raw.get('reverb_decay_s',0.0)),
        reverb_predelay_ms=int(raw.get('reverb_predelay_ms',0)),
        cabinet_ir=_expand_path(cab) if cab else None,
    )

def load_tone_profiles(path:Path)->dict[str,ToneProfile]:
    raw=json.loads(Path(path).read_text()); out={}
    for layer,row in raw['layers'].items():
        stages=tuple(ToneStage(s['kind'],s.get('executable'),tuple(s.get('args',())),_expand_path(s['asset_path']) if s.get('asset_path') else None) for s in row.get('stages',()))
        out[layer]=ToneProfile(row['id'],stages,float(row.get('pan',0.0)),float(row.get('width',1.0)),_load_controls(row))
    return out

def check_production_dependencies(config:ProductionConfig, instruments:Mapping[str,InstrumentProfile]|None=None, tone_profiles:Mapping[str,ToneProfile]|None=None)->None:
    if shutil.which(config.sfizz_executable) is None: raise RuntimeError('PRODUCTION_MISSING_SFIZZ_RENDER')
    for instrument in (instruments or {}).values():
        if not instrument.sfz_path.is_file(): raise RuntimeError(f'PRODUCTION_MISSING_SFZ: {instrument.sfz_path}')
        for art in instrument.articulations.values():
            if art.sfz_path is not None and not art.sfz_path.is_file(): raise RuntimeError(f'PRODUCTION_MISSING_ARTICULATION_SFZ: {instrument.id}:{art.name}:{art.sfz_path}')
    for profile in (tone_profiles or {}).values():
        if profile.controls is not None:
            if shutil.which('ffmpeg') is None: raise RuntimeError('PRODUCTION_MISSING_TONE_EXECUTABLE: ffmpeg')
            if profile.controls.cabinet_ir and not profile.controls.cabinet_ir.is_file(): raise RuntimeError(f'PRODUCTION_MISSING_TONE_ASSET: {profile.controls.cabinet_ir}')
        for stage in profile.stages:
            if stage.executable and shutil.which(stage.executable) is None: raise RuntimeError(f'PRODUCTION_MISSING_TONE_EXECUTABLE: {stage.executable}')
            if stage.asset_path and not stage.asset_path.is_file(): raise RuntimeError(f'PRODUCTION_MISSING_TONE_ASSET: {stage.asset_path}')

def render_sfz(midi:Path,sfz:Path,wav:Path,*,sample_rate:int,executable:str='sfizz_render')->None:
    exe=shutil.which(executable)
    if exe is None: raise RuntimeError('PRODUCTION_MISSING_SFIZZ_RENDER')
    if not Path(sfz).is_file(): raise RuntimeError(f'PRODUCTION_MISSING_SFZ: {sfz}')
    if not Path(midi).is_file(): raise RuntimeError(f'PRODUCTION_MISSING_MIDI: {midi}')
    Path(wav).parent.mkdir(parents=True,exist_ok=True)
    subprocess.run([exe,'--sfz',str(sfz),'--midi',str(midi),'--wav',str(wav),'--samplerate',str(sample_rate),'--use-eot'],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

def tone_filter_string(c:ToneControls)->str:
    filters=[]
    if c.pitch_shift_semitones:
        scale=2.0**(c.pitch_shift_semitones/12.0)
        filters.append(f'rubberband=pitch={scale:.8f}:tempo=1.0')
    input_db=(c.boost_level*0.9)+(c.amp_gain*1.8)+(c.boost_drive*0.35)
    if input_db: filters.append(f'volume={input_db:.3f}dB')
    filters.extend([
        f'equalizer=f=120:t=q:w=1:g={(c.bass-5.0)*1.4:.3f}',
        f'equalizer=f=950:t=q:w=1:g={(c.mid-5.0)*1.4:.3f}',
        f'equalizer=f=4200:t=q:w=1:g={(c.treble-5.0)*1.3:.3f}',
        f'equalizer=f=6500:t=q:w=1:g={(c.presence-5.0)*1.2:.3f}',
    ])
    if c.distortion > 0:
        threshold=max(0.08,0.96-(c.distortion*0.086))
        filters.append(f'asoftclip=type=tanh:threshold={threshold:.4f}:output=0.82:oversample=4')
    master_db=(c.master-5.0)*1.4
    if master_db: filters.append(f'volume={master_db:.3f}dB')
    if c.reverb_mix > 0 and c.reverb_decay_s > 0:
        delay=max(1,c.reverb_predelay_ms)
        decay=min(0.95,max(0.05,c.reverb_decay_s/8.0))
        wet=min(0.95,max(0.01,c.reverb_mix))
        filters.append(f'aecho=1.0:{wet:.4f}:{delay}:{decay:.4f}')
    return ','.join(filters) if filters else 'anull'

def _apply_controls(source:Path,destination:Path,controls:ToneControls)->None:
    ffmpeg=shutil.which('ffmpeg')
    if ffmpeg is None: raise RuntimeError('PRODUCTION_MISSING_TONE_EXECUTABLE: ffmpeg')
    destination.parent.mkdir(parents=True,exist_ok=True)
    pre=destination.with_suffix('.controls-pre.wav') if controls.cabinet_ir else destination
    subprocess.run([ffmpeg,'-y','-i',str(source),'-af',tone_filter_string(controls),'-c:a','pcm_s16le',str(pre)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if controls.cabinet_ir:
        if not controls.cabinet_ir.is_file(): raise RuntimeError(f'PRODUCTION_MISSING_TONE_ASSET: {controls.cabinet_ir}')
        subprocess.run([ffmpeg,'-y','-i',str(pre),'-i',str(controls.cabinet_ir),'-filter_complex','[0:a][1:a]afir=dry=0:wet=1','-c:a','pcm_s16le',str(destination)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try: pre.unlink()
        except FileNotFoundError: pass

def apply_tone_chain(source:Path,destination:Path,profile:ToneProfile)->None:
    source=Path(source); destination=Path(destination)
    if not source.is_file(): raise RuntimeError(f'PRODUCTION_MISSING_SOURCE_WAV: {source}')
    destination.parent.mkdir(parents=True,exist_ok=True)
    current=source; temps=[]
    if profile.controls is not None:
        control_out=destination if not profile.stages else destination.with_suffix('.controls.wav')
        _apply_controls(current,control_out,profile.controls)
        current=control_out
    if profile.stages:
        for i,stage in enumerate(profile.stages):
            if not stage.executable: raise RuntimeError(f'PRODUCTION_UNSUPPORTED_TONE_STAGE: {stage.kind}')
            exe=shutil.which(stage.executable)
            if exe is None: raise RuntimeError(f'PRODUCTION_MISSING_TONE_EXECUTABLE: {stage.executable}')
            if stage.asset_path and not stage.asset_path.is_file(): raise RuntimeError(f'PRODUCTION_MISSING_TONE_ASSET: {stage.asset_path}')
            out=destination if i==len(profile.stages)-1 else destination.with_suffix(f'.stage{i}.wav')
            args=[a.replace('{in}',str(current)).replace('{out}',str(out)).replace('{asset}',str(stage.asset_path or '')) for a in stage.args]
            try:
                subprocess.run([exe,*args],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            except subprocess.CalledProcessError as exc:
                stdout=(exc.stdout or '').strip()
                stderr=(exc.stderr or '').strip()
                raise RuntimeError(
                    f'PRODUCTION_TONE_STAGE_FAILED: kind={stage.kind}; executable={exe}; '
                    f'returncode={exc.returncode}; stdout={stdout}; stderr={stderr}'
                ) from exc
            if current != source and current != destination: temps.append(current)
            current=out
    elif profile.controls is None:
        shutil.copyfile(source,destination)
    for p in temps:
        try: Path(p).unlink()
        except FileNotFoundError: pass
    if profile.pan != 0.0:
        ffmpeg=shutil.which('ffmpeg')
        if ffmpeg is None: raise RuntimeError('PRODUCTION_MISSING_TONE_EXECUTABLE: ffmpeg')
        pan=max(-1.0,min(1.0,profile.pan)); left=1.0 if pan <= 0 else 1.0-pan; right=1.0 if pan >= 0 else 1.0+pan
        panned=destination.with_suffix('.pan.wav'); filt=f'pan=stereo|c0={left:.4f}*c0|c1={right:.4f}*c1'
        subprocess.run([ffmpeg,'-y','-i',str(destination),'-af',filt,'-c:a','pcm_s16le',str(panned)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        panned.replace(destination)

def mix_production_stems(stems:Mapping[str,Path],mix_path:Path)->None:
    if not stems: raise RuntimeError('PRODUCTION_NO_STEMS')
    for name,path in stems.items():
        if not Path(path).is_file(): raise RuntimeError(f'PRODUCTION_MISSING_STEM: {name}')
    ffmpeg=shutil.which('ffmpeg')
    if ffmpeg is None: raise RuntimeError('PRODUCTION_MISSING_MIXER: ffmpeg')
    mix_path=Path(mix_path)
    mix_path.parent.mkdir(parents=True,exist_ok=True)
    cmd=[ffmpeg,'-y']
    for path in stems.values(): cmd += ['-i',str(path)]
    cmd += ['-filter_complex',f'amix=inputs={len(stems)}:normalize=0','-c:a','pcm_s16le',str(mix_path)]
    try:
        subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    except subprocess.CalledProcessError as exc:
        stem_desc=', '.join(f'{name}={Path(path)}' for name,path in stems.items())
        stderr=(exc.stderr or '').strip()
        raise RuntimeError(
            f'PRODUCTION_MIX_FAILED: returncode={exc.returncode}; stems=[{stem_desc}]; ffmpeg_stderr={stderr}'
        ) from exc

def _controls_manifest(c:ToneControls|None):
    if c is None: return None
    return {'tuning_profile':c.tuning_profile,'pitch_shift_semitones':c.pitch_shift_semitones,'boost_drive':c.boost_drive,'boost_level':c.boost_level,'amp_gain':c.amp_gain,'distortion':c.distortion,'bass':c.bass,'mid':c.mid,'treble':c.treble,'presence':c.presence,'master':c.master,'reverb_mix':c.reverb_mix,'reverb_decay_s':c.reverb_decay_s,'reverb_predelay_ms':c.reverb_predelay_ms,'cabinet_ir':str(c.cabinet_ir) if c.cabinet_ir else None}

def production_manifest(*,host_id:str,renderer_version:str,instruments:Mapping[str,InstrumentProfile],tone_profiles:Mapping[str,ToneProfile],humanization_seed:int,structural_signature:str,stems:Mapping[str,Path],mix_path:Path|None=None)->dict:
    data={'schema':'polly.fusion-lab.production-manifest.v3','host_id':host_id,'renderer_version':renderer_version,'humanization_seed':humanization_seed,'structural_signature':structural_signature,'instruments':{k:{'id':v.id,'source_id':v.source_id,'source_version':v.source_version,'sfz_path':str(v.sfz_path),'articulations':{name:{'sfz_path':str(a.sfz_path) if a.sfz_path else None,'keyswitch':a.keyswitch} for name,a in sorted(v.articulations.items())}} for k,v in sorted(instruments.items())},'tone_profiles':{k:{'id':v.id,'pan':v.pan,'width':v.width,'controls':_controls_manifest(v.controls),'stages':[s.kind for s in v.stages]} for k,v in sorted(tone_profiles.items())},'stems':{k:{'path':str(v),'sha256':_sha256(Path(v)) if Path(v).is_file() else None} for k,v in sorted(stems.items())}}
    if mix_path is not None: data['mix']={'path':str(mix_path),'sha256':_sha256(Path(mix_path)) if Path(mix_path).is_file() else None}
    payload=json.dumps(data,sort_keys=True,separators=(',',':')); data['manifest_sha256']=hashlib.sha256(payload.encode()).hexdigest(); return data
