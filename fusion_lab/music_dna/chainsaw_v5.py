from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

from fusion_lab.chainsaw_diplomacy import build_chainsaw_diplomacy, chainsaw_review_rubric
from fusion_lab.mix_truth import THRASH_1988_MIX_LEVELS
from fusion_lab.production_midi import write_articulation_midis
from fusion_lab.production_model import ProductionConfig
from fusion_lab.production_pipeline import default_humanization, render_chainsaw_production
from fusion_lab.production_render import (
    apply_tone_chain,
    check_production_dependencies,
    load_instrument_profiles,
    load_tone_profiles,
    mix_production_stems,
    render_sfz,
)

from .analysis import analyze_host
from .audio_truth import validate_articulation_audio
from .chainsaw_gate import GateState, evaluate_isolated_guitar_gate
from .genre_profiles import load_seed_genre_profiles
from .model import MusicDNAReport
from .production_topology import evidence_from_profiles
from .production_truth import validate_production_truth


EXPECTED_LAYERS = {'rhythm_guitar_L', 'rhythm_guitar_R', 'bass', 'drums', 'lead_guitar'}


def _write_json(path: Path, payload: Mapping | dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')


def _load_thr_profile(profile_root: Path):
    return load_seed_genre_profiles(profile_root)['THRASH_CLASSIC']


def _report_with_production(report: MusicDNAReport, production_payload: Mapping[str, object]) -> MusicDNAReport:
    return MusicDNAReport(
        genre_profile=report.genre_profile,
        feature_vector=report.feature_vector,
        coupling=report.coupling,
        hook_score=report.hook_score,
        production_truth=production_payload,
        decision=report.decision,
    )


def _validate_layer_sets(instruments, tones) -> None:
    if set(instruments) != EXPECTED_LAYERS:
        raise RuntimeError('V5_INSTRUMENT_LAYER_MISMATCH')
    if set(tones) != EXPECTED_LAYERS:
        raise RuntimeError('V5_TONE_LAYER_MISMATCH')


def build_machine_gate(
    *,
    instrument_config: Path,
    tone_config: Path,
    profile_root: Path,
    seed: int = 1988,
):
    host = build_chainsaw_diplomacy()
    profile = _load_thr_profile(profile_root)
    report = analyze_host(host, profile)
    instruments = load_instrument_profiles(instrument_config)
    tones = load_tone_profiles(tone_config)
    _validate_layer_sets(instruments, tones)
    evidence = evidence_from_profiles(
        tones['rhythm_guitar_L'],
        tones['rhythm_guitar_R'],
        instruments['rhythm_guitar_L'],
        instruments['rhythm_guitar_R'],
        seed=seed,
    )
    production = validate_production_truth(profile.production, evidence)
    gate = evaluate_isolated_guitar_gate(report.decision, production, human_review=None)
    production_payload = {
        'evidence': {
            'amp_stage_kind': evidence.amp_stage_kind,
            'cabinet_ir': evidence.cabinet_ir,
            'left_performance_id': evidence.left_performance_id,
            'right_performance_id': evidence.right_performance_id,
            'palm_mute_signature': evidence.palm_mute_signature,
            'sustain_signature': evidence.sustain_signature,
        },
        'validation': production.to_dict(),
    }
    return host, profile, instruments, tones, _report_with_production(report, production_payload), gate


def analyze_chainsaw_v5(
    *,
    out_dir: Path,
    instrument_config: Path,
    tone_config: Path,
    profile_root: Path,
    seed: int = 1988,
) -> dict:
    out_dir = Path(out_dir)
    _, _, _, _, report, gate = build_machine_gate(
        instrument_config=instrument_config,
        tone_config=tone_config,
        profile_root=profile_root,
        seed=seed,
    )
    _write_json(out_dir / 'music-dna-report.json', report.to_dict())
    payload = {
        'state': gate.state.value,
        'reasons': list(gate.reasons),
        'human_review': 'PENDING',
        'human_notes': [],
        'isolated_guitar_rendered': False,
        'full_render_allowed': False,
    }
    _write_json(out_dir / 'v5-gate.json', payload)
    return payload


def _render_rhythm_layer(
    *,
    host,
    layer: str,
    instrument,
    tone,
    humanization,
    out_dir: Path,
    sample_rate: int,
    sfizz_executable: str,
) -> tuple[Path, dict[str, Path]]:
    midi_dir = out_dir / 'midi' / 'articulations'
    raw_dir = out_dir / 'articulations' / layer
    clean_dir = out_dir / 'clean'
    stem_dir = out_dir / 'stems'
    art_midis = write_articulation_midis(host, midi_dir, layer, humanization, instrument)
    art_wavs: dict[str, Path] = {}
    for art_name, midi_path in sorted(art_midis.items()):
        articulation = instrument.articulations[art_name]
        sfz = articulation.sfz_path or instrument.sfz_path
        safe = ''.join(ch.lower() if ch.isalnum() else '_' for ch in art_name).strip('_')
        wav = raw_dir / f'{safe}.wav'
        render_sfz(midi_path, sfz, wav, sample_rate=sample_rate, executable=sfizz_executable)
        art_wavs[art_name] = wav
    clean = clean_dir / f'{layer}.wav'
    mix_production_stems(art_wavs, clean)
    final = stem_dir / f'{layer}.wav'
    apply_tone_chain(clean, final, tone)
    return final, art_wavs


def render_isolated_guitar(
    *,
    out_dir: Path,
    instrument_config: Path,
    tone_config: Path,
    profile_root: Path,
    seed: int = 1988,
    sample_rate: int = 48000,
    sfizz_executable: str = 'sfizz_render',
) -> dict:
    out_dir = Path(out_dir)
    host, profile, instruments, tones, report, machine_gate = build_machine_gate(
        instrument_config=instrument_config,
        tone_config=tone_config,
        profile_root=profile_root,
        seed=seed,
    )
    _write_json(out_dir / 'music-dna-report.json', report.to_dict())
    if machine_gate.state is GateState.REFUSE:
        payload = {
            'state': GateState.REFUSE.value,
            'reasons': list(machine_gate.reasons),
            'human_review': 'PENDING',
            'human_notes': [],
            'isolated_guitar_rendered': False,
            'full_render_allowed': False,
        }
        _write_json(out_dir / 'v5-gate.json', payload)
        raise RuntimeError('V5_MACHINE_GATE_REFUSE: ' + ','.join(machine_gate.reasons))

    check_production_dependencies(
        ProductionConfig(sample_rate, sfizz_executable),
        instruments,
        tones,
    )
    humanization = default_humanization(seed)
    processed: dict[str, Path] = {}
    articulation_wavs: dict[str, dict[str, Path]] = {}
    for layer in ('rhythm_guitar_L', 'rhythm_guitar_R'):
        final, rendered = _render_rhythm_layer(
            host=host,
            layer=layer,
            instrument=instruments[layer],
            tone=tones[layer],
            humanization=humanization[layer],
            out_dir=out_dir,
            sample_rate=sample_rate,
            sfizz_executable=sfizz_executable,
        )
        processed[layer] = final
        articulation_wavs[layer] = rendered

    left = articulation_wavs['rhythm_guitar_L']
    mute_path = left.get('PALM_MUTE_DOWNPICK') or left.get('PALM_MUTE_GALLOP')
    sustain_path = left.get('OPEN_RELEASE') or left.get('CHROMATIC_POWER')
    if mute_path is None or sustain_path is None:
        raise RuntimeError('V5_ARTICULATION_AUDIO_EVIDENCE_MISSING')
    audio_truth = validate_articulation_audio(mute_path, sustain_path)
    if not audio_truth.ok:
        payload = {
            'state': GateState.REFUSE.value,
            'reasons': list(audio_truth.reasons),
            'human_review': 'PENDING',
            'human_notes': [],
            'isolated_guitar_rendered': True,
            'full_render_allowed': False,
            'audio_truth': audio_truth.to_dict(),
        }
        _write_json(out_dir / 'v5-gate.json', payload)
        raise RuntimeError('V5_ARTICULATION_AUDIO_REFUSE: ' + ','.join(audio_truth.reasons))

    isolated_mix = out_dir / 'CHAINSAW_DIPLOMACY_V5_ISOLATED_GUITARS.wav'
    mix_production_stems(processed, isolated_mix)
    payload = {
        'state': GateState.PENDING_HUMAN_REVIEW.value,
        'reasons': [],
        'human_review': 'PENDING',
        'human_notes': [],
        'isolated_guitar_rendered': True,
        'isolated_guitar_mix': str(isolated_mix),
        'full_render_allowed': False,
        'audio_truth': audio_truth.to_dict(),
        'review_rubric': dict(chainsaw_review_rubric()),
    }
    _write_json(out_dir / 'v5-gate.json', payload)
    return payload


def record_isolated_review(*, gate_path: Path, state: str, notes: list[str]) -> dict:
    state = state.upper()
    if state not in {'PASS', 'ADJUST', 'REFUSE'}:
        raise ValueError('review state must be PASS, ADJUST, or REFUSE')
    data = json.loads(Path(gate_path).read_text())
    if not data.get('isolated_guitar_rendered'):
        raise RuntimeError('V5_ISOLATED_GUITAR_NOT_RENDERED')
    data['human_review'] = state
    data['human_notes'] = list(notes)
    if state == 'PASS' and data.get('state') == GateState.PENDING_HUMAN_REVIEW.value:
        data['state'] = GateState.ALLOW_FULL_RENDER.value
        data['full_render_allowed'] = True
    else:
        data['state'] = GateState.REFUSE.value
        data['full_render_allowed'] = False
        reasons = list(data.get('reasons', []))
        reasons.append('human_review_refused' if state == 'REFUSE' else 'human_review_adjust_required')
        data['reasons'] = sorted(set(reasons))
    _write_json(Path(gate_path), data)
    return data


def render_full_after_gate(
    *,
    out_dir: Path,
    gate_path: Path,
    instrument_config: Path,
    tone_config: Path,
    seed: int = 1988,
    sample_rate: int = 48000,
    sfizz_executable: str = 'sfizz_render',
) -> dict:
    gate = json.loads(Path(gate_path).read_text())
    if gate.get('state') != GateState.ALLOW_FULL_RENDER.value or not gate.get('full_render_allowed'):
        raise RuntimeError('V5_FULL_RENDER_REFUSED: isolated guitar gate has not passed human review')
    full_dir = Path(out_dir) / 'full'
    manifest = render_chainsaw_production(
        out_dir=full_dir,
        instrument_config=instrument_config,
        tone_config=tone_config,
        seed=seed,
        sample_rate=sample_rate,
        sfizz_executable=sfizz_executable,
    )
    manifest['music_dna_gate'] = gate
    _write_json(full_dir / 'production-manifest.json', manifest)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='python -m fusion_lab.music_dna.chainsaw_v5')
    sub = parser.add_subparsers(dest='command', required=True)

    def shared(p):
        p.add_argument('--out', type=Path, required=True)
        p.add_argument('--instrument-config', type=Path, required=True)
        p.add_argument('--tone-config', type=Path, required=True)
        p.add_argument('--profile-root', type=Path, default=Path('fusion_lab/data/music_dna/genres'))
        p.add_argument('--seed', type=int, default=1988)

    p = sub.add_parser('analyze'); shared(p)
    p = sub.add_parser('isolated'); shared(p); p.add_argument('--sample-rate', type=int, default=48000); p.add_argument('--sfizz-render', default='sfizz_render')
    p = sub.add_parser('review'); p.add_argument('--gate', type=Path, required=True); p.add_argument('--state', choices=('PASS', 'ADJUST', 'REFUSE'), required=True); p.add_argument('--note', action='append', default=[])
    p = sub.add_parser('full'); shared(p); p.add_argument('--gate', type=Path, required=True); p.add_argument('--sample-rate', type=int, default=48000); p.add_argument('--sfizz-render', default='sfizz_render')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == 'analyze':
        payload = analyze_chainsaw_v5(out_dir=args.out, instrument_config=args.instrument_config, tone_config=args.tone_config, profile_root=args.profile_root, seed=args.seed)
    elif args.command == 'isolated':
        payload = render_isolated_guitar(out_dir=args.out, instrument_config=args.instrument_config, tone_config=args.tone_config, profile_root=args.profile_root, seed=args.seed, sample_rate=args.sample_rate, sfizz_executable=args.sfizz_render)
    elif args.command == 'review':
        payload = record_isolated_review(gate_path=args.gate, state=args.state, notes=args.note)
    elif args.command == 'full':
        payload = render_full_after_gate(out_dir=args.out, gate_path=args.gate, instrument_config=args.instrument_config, tone_config=args.tone_config, seed=args.seed, sample_rate=args.sample_rate, sfizz_executable=args.sfizz_render)
    else:
        return 2
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
