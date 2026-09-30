from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .experiment import EXPERIMENT_001, build_experiment_001, assert_experiment_contract
from .glamasaurus_rex import build_glamasaurus_rex
from .midi_io import FILENAMES, host_manifest, write_role_midis, write_layered_variant_midis, normalized_event_signature
from .model import CANONICAL_ROLES
from .render import RenderConfig, mix_stems, render_stems, render_named_stems, mix_named_stems
from .thrash_chimera import CHIMERA_PERFORMER_PROGRAMS, build_thrash_chimera_expression_sets, chimera_variant_metrics, resolve_thrash_chimera_variant
from .chainsaw_diplomacy import build_chainsaw_diplomacy, chainsaw_vocal_windows, chainsaw_review_rubric
from .production_model import ProductionConfig
from .production_render import load_instrument_profiles, load_tone_profiles, check_production_dependencies
from .production_pipeline import render_chainsaw_production

def _write_json(path:Path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')

def _midi_paths(directory:Path): return {r:directory/FILENAMES[r] for r in CANONICAL_ROLES}

def compose(out:Path)->int:
    host=build_glamasaurus_rex(); paths=write_role_midis(host,out); _write_json(out/'manifest.json',host_manifest(host,paths)); print(f'composed {host.id} -> {out}'); return 0

def verify_host(directory:Path)->int:
    host=build_glamasaurus_rex(); paths=_midi_paths(directory)
    if not all(p.is_file() for p in paths.values()): raise RuntimeError('FUSION_VERIFY_MISSING_MIDI')
    manifest_path=directory/'manifest.json'
    if not manifest_path.is_file(): raise RuntimeError('FUSION_VERIFY_MISSING_MANIFEST')
    actual=json.loads(manifest_path.read_text()); expected=host_manifest(host,paths)
    if actual != expected: raise RuntimeError('FUSION_VERIFY_HOST_MISMATCH')
    print('HOST VERIFY PASS'); return 0

def _experiment_metadata():
    return {'schema':'polly.fusion-lab.experiment.v1','id':EXPERIMENT_001.id,'host_id':EXPERIMENT_001.host_id,'role':EXPERIMENT_001.role,'frozen_dimensions':list(EXPERIMENT_001.frozen_dimensions),'mutated_dimensions':list(EXPERIMENT_001.mutated_dimensions),'hypothesis':EXPERIMENT_001.hypothesis,'variants':list(EXPERIMENT_001.variants),'conclusion_status':'UNRESOLVED','human_listening_notes':[]}

def experiment_001(out:Path)->int:
    host=build_glamasaurus_rex(); variants=build_experiment_001(host)
    for name in EXPERIMENT_001.variants:
        variant=variants[name]; assert_experiment_contract(EXPERIMENT_001,host,variant); paths=write_role_midis(variant,out/name); _write_json(out/name/'manifest.json',host_manifest(variant,paths))
    _write_json(out/'experiment.json',_experiment_metadata()); print(f'experiment {EXPERIMENT_001.id} -> {out}'); return 0

def _chimera_request_row(request):
    return {'performer_id':request.performer_id,'trait_id':request.trait_id,'technique_id':request.technique_id,'function_id':request.function_id,'opportunity_id':request.opportunity_id,'role_family':request.role_family,'rhythmic_policy':request.rhythmic_policy,'harmonic_policy':request.harmonic_policy,'timbral_policy':request.timbral_policy,'density_policy':request.density_policy}

def _chimera_metadata():
    sets=build_thrash_chimera_expression_sets()
    return {'schema':'polly.fusion-lab.experiment.v2','id':'exp-002-thrash-chimera','host_id':'host-002-thrash-control','laws':['STYLE != FUNCTION','TRAIT != TECHNIQUE != FUNCTION != ROLE','SHARED CLOCK != SHARED RHYTHMIC IDENTITY'],'hypothesis':'Specific trait x technique x function x context relationships can coexist coherently inside a frozen Thrash host.','variants':list('ABCDEFG'),'variant_graph':{'A':'pure thrash control','B':'doom melodic guitarist only','C':'djent thumb/slap bassist only','D':'prog synth only','E':'death drummer only','F':'all four recruits, authored placement','G':'same vocabulary, saturation/bad-placement control'},'requests':{k:[_chimera_request_row(r) for r in v] for k,v in sets.items()},'conclusion_status':'UNRESOLVED','human_listening_notes':[]}

def experiment_002(out:Path)->int:
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    for name in 'ABCDEFG':
        host,variant,expressions=resolve_thrash_chimera_variant(name); paths=write_layered_variant_midis(host,variant,expressions,out/name,CHIMERA_PERFORMER_PROGRAMS)
        _write_json(out/name/'manifest.json',{'schema':'polly.fusion-lab.layered-variant.v1','experiment_id':'exp-002-thrash-chimera','variant':name,'host_id':host.id,'bpm':host.bpm,'meter':[host.numerator,host.denominator],'layers':{k:Path(v).name for k,v in paths.items()},'layer_signatures':{k:normalized_event_signature(v) for k,v in paths.items()},'metrics':chimera_variant_metrics(name)})
    _write_json(out/'experiment.json',_chimera_metadata()); print(f'experiment exp-002-thrash-chimera -> {out}'); return 0

def compose_host003(out:Path)->int:
    host=build_chainsaw_diplomacy(); paths=write_role_midis(host,out)
    manifest=host_manifest(host,paths); manifest['bars']=sum(s.bars for s in host.sections); manifest['vocal_windows']=[{'id':w.id,'section_id':w.section_id,'start_tick':w.start_tick,'end_tick':w.end_tick,'kind':w.kind} for w in chainsaw_vocal_windows(host)]; manifest['authenticity_rubric']=dict(chainsaw_review_rubric())
    _write_json(out/'manifest.json',manifest); print(f'composed {host.id} -> {out}'); return 0

def production_check(instrument_config:Path,tone_config:Path,sfizz_render:str,sample_rate:int)->int:
    instruments=load_instrument_profiles(instrument_config); tones=load_tone_profiles(tone_config); check_production_dependencies(ProductionConfig(sample_rate,sfizz_render),instruments,tones)
    print('PRODUCTION CHECK PASS'); return 0

def render_host003_production(out:Path,instrument_config:Path,tone_config:Path,seed:int,sample_rate:int,sfizz_render:str)->int:
    manifest=render_chainsaw_production(out_dir=out,instrument_config=instrument_config,tone_config=tone_config,seed=seed,sample_rate=sample_rate,sfizz_executable=sfizz_render)
    print(f"rendered {manifest['host_id']} -> {out}"); return 0

def record_host003_review(manifest_path:Path,state:str,notes:list[str])->int:
    data=json.loads(manifest_path.read_text()); review=data.setdefault('authenticity_review',{}); review['state']=state; review['notes']=list(notes); review.setdefault('rubric',dict(chainsaw_review_rubric())); _write_json(manifest_path,data); print(f'AUTHENTICITY REVIEW {state}'); return 0

def render_dir(midi_dir:Path,out:Path,soundfont:Path)->int:
    stems=render_stems(_midi_paths(midi_dir),out,RenderConfig(soundfont)); mix_stems(stems,out/'mix.wav'); print(f'rendered -> {out}'); return 0

def render_exp001(root:Path,soundfont:Path)->int:
    for name in EXPERIMENT_001.variants: render_dir(root/name,root/name,soundfont)
    return 0

def render_exp002(root:Path,soundfont:Path)->int:
    root=Path(root); config=RenderConfig(soundfont)
    for name in 'ABCDEFG':
        directory=root/name; midi_paths={p.stem:p for p in sorted(directory.glob('*.mid'))}
        if not midi_paths: raise RuntimeError(f'FUSION_CHIMERA_MISSING_MIDI: {name}')
        stems=render_named_stems(midi_paths,directory,config); mix_named_stems(stems,directory/'mix.wav'); print(f'rendered chimera {name} -> {directory}')
    return 0

def build_parser():
    p=argparse.ArgumentParser(prog='python -m fusion_lab',description='Headless deterministic Polly Fusion Lab'); sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('compose'); q.add_argument('--out',type=Path,required=True)
    q=sub.add_parser('verify-host'); q.add_argument('--dir',type=Path,required=True)
    q=sub.add_parser('experiment-001'); q.add_argument('--out',type=Path,required=True)
    q=sub.add_parser('experiment-002'); q.add_argument('--out',type=Path,required=True)
    q=sub.add_parser('compose-host003'); q.add_argument('--out',type=Path,required=True)
    q=sub.add_parser('production-check'); q.add_argument('--instrument-config',type=Path,required=True); q.add_argument('--tone-config',type=Path,default=Path('fusion_lab/data/production/tone-profiles.json')); q.add_argument('--sfizz-render',default='sfizz_render'); q.add_argument('--sample-rate',type=int,default=48000)
    q=sub.add_parser('render-host003-production'); q.add_argument('--out',type=Path,required=True); q.add_argument('--instrument-config',type=Path,required=True); q.add_argument('--tone-config',type=Path,default=Path('fusion_lab/data/production/tone-profiles.json')); q.add_argument('--seed',type=int,default=1988); q.add_argument('--sample-rate',type=int,default=48000); q.add_argument('--sfizz-render',default='sfizz_render')
    q=sub.add_parser('review-host003'); q.add_argument('--manifest',type=Path,required=True); q.add_argument('--state',choices=('PASS','ADJUST','REFUSE'),required=True); q.add_argument('--note',action='append',default=[])
    q=sub.add_parser('render'); q.add_argument('--midi-dir',type=Path,required=True); q.add_argument('--out',type=Path,required=True); q.add_argument('--soundfont',type=Path,required=True)
    q=sub.add_parser('render-exp001'); q.add_argument('--root',type=Path,required=True); q.add_argument('--soundfont',type=Path,required=True)
    q=sub.add_parser('render-exp002'); q.add_argument('--root',type=Path,required=True); q.add_argument('--soundfont',type=Path,required=True)
    return p

def main(argv=None)->int:
    args=build_parser().parse_args(argv)
    try:
        if args.command=='compose': return compose(args.out)
        if args.command=='verify-host': return verify_host(args.dir)
        if args.command=='experiment-001': return experiment_001(args.out)
        if args.command=='experiment-002': return experiment_002(args.out)
        if args.command=='compose-host003': return compose_host003(args.out)
        if args.command=='production-check': return production_check(args.instrument_config,args.tone_config,args.sfizz_render,args.sample_rate)
        if args.command=='render-host003-production': return render_host003_production(args.out,args.instrument_config,args.tone_config,args.seed,args.sample_rate,args.sfizz_render)
        if args.command=='review-host003': return record_host003_review(args.manifest,args.state,args.note)
        if args.command=='render': return render_dir(args.midi_dir,args.out,args.soundfont)
        if args.command=='render-exp001': return render_exp001(args.root,args.soundfont)
        if args.command=='render-exp002': return render_exp002(args.root,args.soundfont)
    except (RuntimeError,ValueError,FileNotFoundError) as exc:
        print(str(exc),file=sys.stderr); return 2
    return 2
