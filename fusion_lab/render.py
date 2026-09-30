from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import shutil, subprocess
from .model import CANONICAL_ROLES, Role

WAV_FILENAMES={'DRUMS':'drums.wav','BASS':'bass.wav','RHYTHM_GUITAR':'rhythm_guitar.wav','LEAD_KEYS':'lead_keys.wav','VOCALS':'vocals.wav'}

@dataclass(frozen=True, slots=True)
class RenderConfig:
    soundfont:Path
    sample_rate:int=44100
    gain:float=0.8
    def __post_init__(self):
        if self.sample_rate <= 0: raise ValueError('sample_rate must be > 0')
        if self.gain <= 0: raise ValueError('gain must be > 0')

def check_render_dependencies(config:RenderConfig)->None:
    if shutil.which('fluidsynth') is None:
        raise RuntimeError('FUSION_RENDER_MISSING_FLUIDSYNTH: install fluidsynth')
    if not Path(config.soundfont).is_file():
        raise RuntimeError(f'FUSION_RENDER_MISSING_SOUNDFONT: {config.soundfont}')

def render_midi(midi:Path,wav:Path,config:RenderConfig)->None:
    check_render_dependencies(config)
    exe=shutil.which('fluidsynth')
    Path(wav).parent.mkdir(parents=True,exist_ok=True)
    cmd=[exe,'-ni','-g',str(config.gain),'-r',str(config.sample_rate),'-F',str(wav),str(config.soundfont),str(midi)]
    subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

def render_stems(midi_paths:dict[Role,Path],out_dir:Path,config:RenderConfig)->dict[Role,Path]:
    out_dir=Path(out_dir); out_dir.mkdir(parents=True,exist_ok=True)
    result={}
    for role in CANONICAL_ROLES:
        if role not in midi_paths: raise RuntimeError(f'FUSION_RENDER_MISSING_MIDI: {role}')
        wav=out_dir/WAV_FILENAMES[role]
        render_midi(Path(midi_paths[role]),wav,config)
        result[role]=wav
    return result

def mix_stems(stems:dict[Role,Path],mix_path:Path)->None:
    for role in CANONICAL_ROLES:
        if role not in stems or not Path(stems[role]).is_file():
            raise RuntimeError(f'FUSION_RENDER_MISSING_STEM: {role}')
    mix_path=Path(mix_path); mix_path.parent.mkdir(parents=True,exist_ok=True)
    ffmpeg=shutil.which('ffmpeg')
    if ffmpeg:
        cmd=[ffmpeg,'-y']
        for role in CANONICAL_ROLES: cmd += ['-i',str(stems[role])]
        cmd += ['-filter_complex',f'amix=inputs={len(CANONICAL_ROLES)}:normalize=0','-c:a','pcm_s16le',str(mix_path)]
        subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        return
    sox=shutil.which('sox')
    if sox:
        cmd=[sox,'-m',*(str(stems[r]) for r in CANONICAL_ROLES),str(mix_path)]
        subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        return
    raise RuntimeError('FUSION_RENDER_MISSING_MIXER: install ffmpeg or sox')
