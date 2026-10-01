from __future__ import annotations

from typing import Mapping

from .model import DecisionState, GenreDNA, GenreDecision, RangeBand


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
    for alias, target in _COUPLING_ALIASES.items():
        if target in result:
            result[alias] = result[target]
    return result


def _reason_name(key: str, suffix: str) -> str:
    return f"{key.split('.')[-1]}_{suffix}"


def validate_genre(profile: GenreDNA, features: Mapping[str, float]) -> GenreDecision:
    bands = _flatten_profile(profile)
    reasons: list[str] = []
    distances: list[float] = []
    hard_failure = False

    for key, value in features.items():
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

    if hard_failure:
        state = DecisionState.REJECT
    elif reasons:
        state = DecisionState.MUTATE
    else:
        state = DecisionState.ALLOW

    mean_distance = sum(distances) / len(distances) if distances else 0.0
    return GenreDecision(state, profile.id, tuple(sorted(set(reasons))), mean_distance)
