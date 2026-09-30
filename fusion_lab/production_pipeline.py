from __future__ import annotations
import json
from pathlib import Path
from .chainsaw_diplomacy import build_chainsaw_diplomacy, chainsaw_vocal_windows, chainsaw_review_rubric
from .midi_io import host_structural_signature
from .production_model import HumanizationProfile, ProductionConfig
from .production_midi import write_production_midis
from .production_render import load_instrument_profiles, load_tone_profiles, check_production_dependencies, render_sfz, apply_tone_chain, mix_production_stems, production_manifest

def default_humanization(seed:int)->dict[str,HumanizationProfile]:
    return {'rhythm_guitar_L':HumanizationProfile(seed,2,4,7,8),'rhythm_guitar_R':HumanizationProfile(seed,2,4,9,9),'bass':HumanizationProfile(seed+11,4,6,0,0),'drums':HumanizationProfile(seed+23,6,8,0,0),'lead_guitar':HumanizationProfile(seed+37,7,7,0,0)}

def render_chainsaw_production(*,out_dir:Path,instrument_config:Path,tone_config:Path,seed:int=1988,sample_rate:int=48000,sfizz_executable:str='sfizz_render')->dict:
    out_dir=Path(out_dir); out_dir.mkdir(parents=True,exist_ok=True)
    host=build_chainsaw_diplomacy(); instruments=load_instrument_profiles(instrument_config); tones=load_tone_profiles(tone_config)
    expected={'rhythm_guitar_L','rhythm_guitar_R','bass','drums','lead_guitar'}
    if set(instruments)!=expected: raise RuntimeError('PRODUCTION_INSTRUMENT_LAYER_MISMATCH')
    if set(tones)!=expected: raise RuntimeError('PRODUCTION_TONE_LAYER_MISMATCH')
    config=ProductionConfig(sample_rate,sfizz_executable); check_production_dependencies(config,instruments,tones)
    midi_dir=out_dir/'midi'; clean_dir=out_dir/'clean'; stem_dir=out_dir/'stems'
    midis=write_production_midis(host,midi_dir,default_humanization(seed),instruments)
    processed={}
    for layer in sorted(expected):
        clean=clean_dir/f'{layer}.wav'; final=stem_dir/f'{layer}.wav'
        render_sfz(midis[layer],instruments[layer].sfz_path,clean,sample_rate=sample_rate,executable=sfizz_executable)
        apply_tone_chain(clean,final,tones[layer]); processed[layer]=final
    mix_path=out_dir/'CHAINSAW_DIPLOMACY_INSTRUMENTAL.wav'; mix_production_stems(processed,mix_path)
    manifest=production_manifest(host_id=host.id,renderer_version='sfizz-1.2.3-compatible',instruments=instruments,tone_profiles=tones,humanization_seed=seed,structural_signature=host_structural_signature(host),stems=processed,mix_path=mix_path)
    manifest['bpm']=host.bpm; manifest['meter']=[host.numerator,host.denominator]; manifest['bars']=sum(s.bars for s in host.sections)
    manifest['vocal_windows']=[{'id':w.id,'section_id':w.section_id,'start_tick':w.start_tick,'end_tick':w.end_tick,'kind':w.kind} for w in chainsaw_vocal_windows(host)]
    manifest['authenticity_review']={'state':'PENDING','rubric':dict(chainsaw_review_rubric()),'notes':[]}
    (out_dir/'production-manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return manifest
