from __future__ import annotations

from fusion_lab.model import HostComposition

from .coupling import extract_coupling_features
from .feature_extractors import extract_host_features
from .hook_score import score_hook
from .model import GenreDNA, MusicDNAReport
from .validator import build_music_dna_report


def analyze_host(host: HostComposition, profile: GenreDNA) -> MusicDNAReport:
    feature_vector = extract_host_features(host)
    coupling = dict(extract_coupling_features(host))
    guitar = tuple(host.tracks['RHYTHM_GUITAR'].events)
    hook = score_hook(guitar, host.ticks_per_beat, host.numerator).to_dict()
    return build_music_dna_report(profile, feature_vector, coupling, hook)
