from __future__ import annotations

from typing import Mapping

from .model import DecisionState, FeatureVector, GenreDNA, GenreDecision, MusicDNAReport, RangeBand


_COUPLING_ALIASES = {
    'coupling.guitar_kick_coupling': 'drums.guitar_kick_coupling',
    'coupling.bass_guitar_lock_rate': 'bass.guitar_lock_rate',
    'coupling.bass_kick_lock_rate': 'bass.kick_lock_rate',
}


def _flatten_profile(profile: GenreDNA) -> dict[str, RangeBand]:
    result: dict[str, RangeBand] = {'tempo_bpm': profile.tempo}
    for prefix, component in (
        ('harmony', profile.harmony),
        ('guitar', profile.guitar),
        ('bass', profile.bass),
        ('drums', profile.drums),
        ('vocals', profile.vocals),
        ('keys', profile.keys),
        ('arrangement', profile.arrangement),
        ('production', profile.production),
    ):
        for name, band in component.features.items():
            result[f'{prefix}.{name}'] = band
    if profile.riff_structure is not None:
        for name, band in profile.riff_structure.features.items():
            result[f'riff_structure.{name}'] = band
    for alias, target in _COUPLING_ALIASES.items():
        if target in result:
            result[alias] = result[target]
    return result


def _reason_name(key: str, suffix: str) -> str:
    return f"{key.split('.')[-1]}_{suffix}"


def _feature_mapping(features: FeatureVector | Mapping[str, float]) -> dict[str, float]:
    if isinstance(features, FeatureVector):
        return dict(features.values)
    return {str(key): float(value) for key, value in features.items()}


def _numeric_riff_metrics(riff_structure: Mapping[str, object] | None) -> dict[str, float]:
    if not riff_structure:
        return {}
    result: dict[str, float] = {}
    gesture_metadata_present = bool(riff_structure.get('gesture_metadata_present', False))
    for key, value in riff_structure.items():
        if key in {'gesture_metadata_present', 'gesture_by_bar', 'family_by_bar', 'families'}:
            continue
        if key in {'gesture_diversity', 'transition_density'} and not gesture_metadata_present:
            continue
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            result[str(key)] = float(value)
    return result


def _merge_validation_inputs(
    features: FeatureVector | Mapping[str, float],
    coupling: Mapping[str, float] | None,
    hook: Mapping[str, float] | None,
    riff_structure: Mapping[str, object] | None = None,
) -> dict[str, float]:
    merged = _feature_mapping(features)
    if coupling:
        for key, value in coupling.items():
            merged[f'coupling.{key}'] = float(value)
    if hook:
        if 'phrase_end_mutation' in hook:
            merged['arrangement.phrase_end_mutation'] = float(hook['phrase_end_mutation'])
        if 'recurrence' in hook:
            merged['guitar.hook_recurrence'] = float(hook['recurrence'])
    for key, value in _numeric_riff_metrics(riff_structure).items():
        merged[f'riff_structure.{key}'] = value
    return merged


def validate_genre(
    profile: GenreDNA,
    features: FeatureVector | Mapping[str, float],
    coupling: Mapping[str, float] | None = None,
    hook: Mapping[str, float] | None = None,
    production_truth=None,
    riff_structure: Mapping[str, object] | None = None,
) -> GenreDecision:
    bands = _flatten_profile(profile)
    merged = _merge_validation_inputs(features, coupling, hook, riff_structure)
    reasons: list[str] = []
    distances: list[float] = []
    hard_failure = False

    for key, value in merged.items():
        band = bands.get(key)
        if band is None:
            continue
        if value < band.minimum or value > band.maximum:
            hard_failure = True
            reasons.append(_reason_name(key, 'outside_hard_range'))
            distances.append(max(1.0, band.normalized_distance(float(value))))
            continue
        distance = band.normalized_distance(float(value))
        distances.append(distance)
        if distance > 0:
            suffix = 'below_range' if value < band.preferred_minimum else 'above_range'
            reasons.append(_reason_name(key, suffix))

    if production_truth is not None and not getattr(production_truth, 'ok', True):
        hard_failure = True
        reasons.extend(getattr(production_truth, 'reasons', ('production_truth_failed',)))

    if hard_failure:
        state = DecisionState.REJECT
    elif reasons:
        state = DecisionState.MUTATE
    else:
        state = DecisionState.ALLOW

    mean_distance = sum(distances) / len(distances) if distances else 0.0
    return GenreDecision(state, profile.id, tuple(sorted(set(reasons))), mean_distance)


def build_music_dna_report(
    profile: GenreDNA,
    features: FeatureVector | Mapping[str, float],
    coupling: Mapping[str, float],
    hook: Mapping[str, float],
    production_truth=None,
    riff_structure: Mapping[str, object] | None = None,
) -> MusicDNAReport:
    riff_payload = dict(riff_structure or {})
    decision = validate_genre(
        profile,
        features,
        coupling,
        hook,
        production_truth,
        riff_structure=riff_payload,
    )
    production_payload = {}
    if production_truth is not None:
        production_payload = (
            production_truth.to_dict()
            if hasattr(production_truth, 'to_dict')
            else {'ok': bool(getattr(production_truth, 'ok', False)), 'reasons': list(getattr(production_truth, 'reasons', ())) }
        )
    return MusicDNAReport(
        genre_profile=profile.id,
        feature_vector=_feature_mapping(features),
        coupling=dict(coupling),
        hook_score=dict(hook),
        production_truth=production_payload,
        decision=decision,
        riff_structure=riff_payload,
    )
