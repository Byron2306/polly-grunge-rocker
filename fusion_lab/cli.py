from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .experiment import EXPERIMENT_001, build_experiment_001, assert_experiment_contract
from .glamasaurus_rex import build_glamasaurus_rex
from .midi_io import FILENAMES, host_manifest, write_role_midis
from .model import CANONICAL_ROLES
from .render import RenderConfig, mix_stems, render_stems

def _write_json(path:Path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')

def _midi_paths(directory:Path): return {r:directory/FILENAMES[r] for r in CANONICAL_ROLES}

def compose(out:Path)->int:
    host=build_glamasaurus_rex(); paths=write_role_midis(host,out); _write_json(out/'manifest.json',host_manifest(host,paths))
    print(f'composed {host.id} -> {out}')
    return 0

def verify_host(directory:Path)->int:
    host=build_glamasaurus_rex(); paths=_midi_paths(directory)
    if not all(p.is_file() for p in paths.values()): raise RuntimeError('FUSION_VERIFY_MISSING_MIDI')
    manifest_path=directory/'manifest.json'
    if not manifest_path.is_file(): raise RuntimeError('FUSION_VERIFY_MISSING_MANIFEST')
    actual=json.loads(manifest_path.read_text()); expected=host_manifest(host,paths)
    if actual != expected: raise RuntimeError('FUSION_VERIFY_HOST_MISMATCH')
    print('HOST VERIFY PASS')
    return 0

def _experiment_metadata():
    return {
      'schema':'polly.fusion-lab.experiment.v1','id':EXPERIMENT_001.id,'host_id':EXPERIMENT_001.host_id,
      'role':EXPERIMENT_001.role,'frozen_dimensions':list(EXPERIMENT_001.frozen_dimensions),
      'mutated_dimensions':list(EXPERIMENT_001.mutated_dimensions),'hypothesis':EXPERIMENT_001.hypothesis,
      'variants':list(EXPERIMENT_001.variants),'conclusion_status':'UNRESOLVED','human_listening_notes':[],
    }

def experiment_001(out:Path)->int:
    host=build_glamasaurus_rex(); variants=build_experiment_001(host)
    for name in EXPERIMENT_001.variants:
        variant=variants[name]; assert_experiment_contract(EXPERIMENT_001,host,variant)
        paths=write_role_midis(variant,out/name)
        _write_json(out/name/'manifest.json',host_manifest(variant,paths))
    _write_json(out/'experiment.json',_experiment_metadata())
    print(f'experiment {EXPERIMENT_001.id} -> {out}')
    return 0

def render_dir(midi_dir:Path,out:Path,soundfont:Path)->int:
    stems=render_stems(_midi_paths(midi_dir),out,RenderConfig(soundfont))
    mix_stems(stems,out/'mix.wav'); print(f'rendered -> {out}'); return 0

def render_exp001(root:Path,soundfont:Path)->int:
    for name in EXPERIMENT_001.variants: render_dir(root/name,root/name,soundfont)
    return 0

def build_parser():
    p=argparse.ArgumentParser(prog='python -m fusion_lab',description='Headless deterministic Polly Fusion Lab')
    sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('compose'); q.add_argument('--out',type=Path,required=True)
    q=sub.add_parser('verify-host'); q.add_argument('--dir',type=Path,required=True)
    q=sub.add_parser('experiment-001'); q.add_argument('--out',type=Path,required=True)
    q=sub.add_parser('render'); q.add_argument('--midi-dir',type=Path,required=True); q.add_argument('--out',type=Path,required=True); q.add_argument('--soundfont',type=Path,required=True)
    q=sub.add_parser('render-exp001'); q.add_argument('--root',type=Path,required=True); q.add_argument('--soundfont',type=Path,required=True)
    return p

def main(argv=None)->int:
    args=build_parser().parse_args(argv)
    try:
        if args.command=='compose': return compose(args.out)
        if args.command=='verify-host': return verify_host(args.dir)
        if args.command=='experiment-001': return experiment_001(args.out)
        if args.command=='render': return render_dir(args.midi_dir,args.out,args.soundfont)
        if args.command=='render-exp001': return render_exp001(args.root,args.soundfont)
    except (RuntimeError,ValueError) as exc:
        print(str(exc),file=sys.stderr); return 2
    return 2
