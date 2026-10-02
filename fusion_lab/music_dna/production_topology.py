from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from fusion_lab.production_model import InstrumentProfile, ToneProfile

from .production_truth import ProductionEvidence, REAL_AMP_KINDS


@dataclass(frozen=True, slots=True)
class ExecutedToneEvidence:
    executed_stages: tuple[str, ...]
    amp_stage_kind: str | None
    cabinet_ir: str | None
    cabinet_processor: str | None
    output_path: str

    def to_dict(self) -> dict:
        return {
            'executed_stages': list(self.executed_stages),
            'amp_stage_kind': self.amp_stage_kind,
            'cabinet_ir': self.cabinet_ir,
            'cabinet_processor': self.cabinet_processor,
            'output_path': self.output_path,
        }


def _amp_kind(profile: ToneProfile) -> str | None:
    for stage in profile.stages:
        if stage.kind in REAL_AMP_KINDS:
            return stage.kind
    if profile.controls is not None and profile.controls.distortion > 0:
        return 'generic_softclip'
    return None


def _cabinet(profile: ToneProfile) -> str | None:
    if profile.controls is not None and profile.controls.cabinet_ir:
        return str(profile.controls.cabinet_ir)
    for stage in profile.stages:
        if stage.asset_path is not None and stage.kind in {'cabinet_ir', *REAL_AMP_KINDS}:
            return str(stage.asset_path)
    return None


def _cabinet_processor(profile: ToneProfile) -> str | None:
    for stage in profile.stages:
        if stage.kind == 'plugin_amp_with_cabinet':
            joined = ' '.join(stage.args)
            if 'run_caps_thr_amp.py' in joined:
                return 'caps:AmpVTS+CabinetIV'
            if 'run_guitarix_thr_amp.py' in joined:
                return 'guitarix:gx_amp:built_in_cabinet'
            return 'plugin_amp_with_cabinet'
        if stage.kind == 'plugin_cabinet':
            return 'plugin_cabinet'
    return None


def _articulation_signature(instrument: InstrumentProfile, names: tuple[str, ...]) -> str | None:
    for name in names:
        articulation = instrument.articulations.get(name)
        if articulation is None:
            continue
        path = articulation.sfz_path or instrument.sfz_path
        return f'{path}|ks={articulation.keyswitch}|ch={articulation.midi_channel}'
    return None


def evidence_from_profiles(
    left_tone: ToneProfile,
    right_tone: ToneProfile,
    left_instrument: InstrumentProfile,
    right_instrument: InstrumentProfile,
    *,
    seed: int,
) -> ProductionEvidence:
    left_amp = _amp_kind(left_tone)
    right_amp = _amp_kind(right_tone)
    amp_kind = left_amp if left_amp == right_amp else None

    left_cab = _cabinet(left_tone)
    right_cab = _cabinet(right_tone)
    cabinet = left_cab if left_cab == right_cab else None

    left_cab_processor = _cabinet_processor(left_tone)
    right_cab_processor = _cabinet_processor(right_tone)
    cabinet_processor = left_cab_processor if left_cab_processor == right_cab_processor else None

    palm = _articulation_signature(
        left_instrument,
        ('PALM_MUTE_DOWNPICK', 'PALM_MUTE_GALLOP', 'PALM_MUTE'),
    )
    sustain = _articulation_signature(
        left_instrument,
        ('OPEN_RELEASE', 'CHROMATIC_POWER', 'SUSTAIN'),
    )

    return ProductionEvidence(
        amp_stage_kind=amp_kind,
        cabinet_ir=cabinet,
        left_performance_id=f'{left_instrument.id}:L:{seed}:timing2:velocity7',
        right_performance_id=f'{right_instrument.id}:R:{seed}:timing4:velocity9',
        palm_mute_signature=palm,
        sustain_signature=sustain,
        cabinet_processor=cabinet_processor,
    )


def execute_tone_chain_with_evidence(source: Path, destination: Path, profile: ToneProfile) -> ExecutedToneEvidence:
    from fusion_lab.production_render import apply_tone_chain

    source = Path(source)
    destination = Path(destination)
    if not source.is_file():
        raise RuntimeError(f'PRODUCTION_MISSING_SOURCE_WAV: {source}')

    for stage in profile.stages:
        if stage.executable and shutil.which(stage.executable) is None:
            raise RuntimeError(f'PRODUCTION_MISSING_TONE_EXECUTABLE: {stage.executable}')
        if stage.asset_path is not None and not stage.asset_path.is_file():
            raise RuntimeError(f'PRODUCTION_MISSING_TONE_ASSET: {stage.asset_path}')

    apply_tone_chain(source, destination, profile)
    if not destination.is_file() or destination.stat().st_size == 0:
        raise RuntimeError('PRODUCTION_TONE_OUTPUT_MISSING')

    stages: list[str] = []
    if profile.controls is not None:
        stages.append('controls')
    stages.extend(stage.kind for stage in profile.stages)
    return ExecutedToneEvidence(
        executed_stages=tuple(stages),
        amp_stage_kind=_amp_kind(profile),
        cabinet_ir=_cabinet(profile),
        cabinet_processor=_cabinet_processor(profile),
        output_path=str(destination),
    )
