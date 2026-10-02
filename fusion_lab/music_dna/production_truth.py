from __future__ import annotations

from dataclasses import dataclass

from .model import ProductionDNA


REAL_AMP_KINDS = {
    'real_amp_sim',
    'external_amp',
    'plugin_amp',
    'plugin_amp_with_cabinet',
    'captured_amp',
}


@dataclass(frozen=True, slots=True)
class ProductionEvidence:
    amp_stage_kind: str | None
    cabinet_ir: str | None
    left_performance_id: str | None
    right_performance_id: str | None
    palm_mute_signature: str | None
    sustain_signature: str | None
    cabinet_processor: str | None = None


@dataclass(frozen=True, slots=True)
class ProductionTruthResult:
    ok: bool
    reasons: tuple[str, ...]

    def to_dict(self) -> dict:
        return {'ok': self.ok, 'reasons': list(self.reasons)}


def validate_production_truth(profile: ProductionDNA, evidence: ProductionEvidence) -> ProductionTruthResult:
    required = {constraint.id: constraint.required for constraint in profile.hard_constraints}
    reasons: list[str] = []

    if required.get('amp_distortion_required'):
        if evidence.amp_stage_kind not in REAL_AMP_KINDS:
            reasons.append('missing_verified_amp_distortion')

    if required.get('cabinet_required'):
        if not evidence.cabinet_ir and not evidence.cabinet_processor:
            reasons.append('missing_verified_cabinet')

    if required.get('distinct_double_tracks'):
        if not evidence.left_performance_id or not evidence.right_performance_id:
            reasons.append('double_track_identity_missing')
        elif evidence.left_performance_id == evidence.right_performance_id:
            reasons.append('double_tracks_not_distinct')

    if required.get('distinct_palm_mute_envelope'):
        if not evidence.palm_mute_signature or not evidence.sustain_signature:
            reasons.append('articulation_signature_missing')
        elif evidence.palm_mute_signature == evidence.sustain_signature:
            reasons.append('palm_mute_not_distinct_from_sustain')

    return ProductionTruthResult(not reasons, tuple(sorted(reasons)))
