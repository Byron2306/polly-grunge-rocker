from __future__ import annotations

from fusion_lab.model import HostComposition

from .coupling import extract_coupling_features
from .feature_extractors import extract_host_features
from .hook_score import score_hook
from .model import GenreDNA, MusicDNAReport
from .validator import validate_genre


def analyze_host(host: HostComposition, profile: GenreDNA) -> MusicDNAReport:
    feature_vector = extract_host_features(host)
    coupling = dict(extract_coupling_features(host))
    guitar = tuple(host.tracks['RHYTHM_GUITAR'].events)
    hook = dict(score_hook(guitar, host.ticks_per_beat))

    merged = dict(feature_vector.values)
    for key, value in coupling.items():
        merged[f'coupling.{key}'] = value
    merged['arrangement.phrase_end_mutation'] = hook['phrase_end_mutation']
    merged['guitar.hook_recurrence'] = hook['recurrence']

    decision = validate_genre(profile, merged)
    return MusicDNAReport(
        genre_profile=profile.id,
        feature_vector=feature_vector.values,
        coupling=coupling,
        hook_score=hook,
        production_truth={},
        decision=decision,
    )
