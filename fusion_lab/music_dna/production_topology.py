from __future__ import annotations

from pathlib import Path

from fusion_lab.production_model import InstrumentProfile, ToneProfile

from .production_truth import ProductionEvidence, REAL_AMP_KINDS


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
    )
