from __future__ import annotations

import json
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Sequence

from .distributions import ScalarDistribution
from .model import RangeBand


FORBIDDEN_PAYLOAD_KEYS = {'tab', 'tabs', 'score', 'notation', 'notes', 'lyrics', 'melody'}


@dataclass(frozen=True, slots=True)
class CorpusObservation:
    genre: str
    artist: str
    track: str
    features: Mapping[str, float]
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.genre or not self.artist or not self.track:
            raise ValueError('genre, artist, and track are required')
        clean: dict[str, float] = {}
        for key, raw in self.features.items():
            if key.lower() in FORBIDDEN_PAYLOAD_KEYS:
                raise ValueError(f'copyrighted notation payload is not allowed: {key}')
            value = float(raw)
            if not isfinite(value):
                raise ValueError(f'feature must be finite: {key}')
            clean[str(key)] = value
        if not self.provenance:
            raise ValueError('provenance is required')
        object.__setattr__(self, 'features', MappingProxyType(dict(sorted(clean.items()))))
        object.__setattr__(self, 'provenance', tuple(str(x) for x in self.provenance))


@dataclass(frozen=True, slots=True)
class CorpusGenreSummary:
    genre: str
    observation_count: int
    medians: Mapping[str, float]
    feature_bands: Mapping[str, RangeBand]

    def __post_init__(self) -> None:
        if not self.genre:
            raise ValueError('genre is required')
        if self.observation_count <= 0:
            raise ValueError('observation_count must be > 0')
        object.__setattr__(self, 'medians', MappingProxyType(dict(sorted(self.medians.items()))))
        object.__setattr__(self, 'feature_bands', MappingProxyType(dict(sorted(self.feature_bands.items()))))

    def to_dict(self) -> dict:
        return {
            'genre': self.genre,
            'observation_count': self.observation_count,
            'medians': dict(self.medians),
            'feature_bands': {
                key: {
                    'minimum': band.minimum,
                    'preferred_minimum': band.preferred_minimum,
                    'preferred_maximum': band.preferred_maximum,
                    'maximum': band.maximum,
                }
                for key, band in self.feature_bands.items()
            },
        }


def load_corpus(path: Path) -> tuple[CorpusObservation, ...]:
    raw = json.loads(Path(path).read_text())
    if raw.get('schema') != 'polly.music-dna.corpus.v1':
        raise ValueError('invalid corpus schema')
    rows = raw.get('observations')
    if not isinstance(rows, list):
        raise ValueError('corpus observations must be a list')
    return tuple(
        CorpusObservation(
            genre=row['genre'],
            artist=row['artist'],
            track=row['track'],
            features=row.get('features', {}),
            provenance=tuple(row.get('provenance', ())),
        )
        for row in rows
    )


def summarize_corpus(observations: Sequence[CorpusObservation]) -> Mapping[str, CorpusGenreSummary]:
    if not observations:
        raise ValueError('corpus must contain observations')
    grouped: dict[str, list[CorpusObservation]] = {}
    for observation in observations:
        grouped.setdefault(observation.genre, []).append(observation)

    summaries: dict[str, CorpusGenreSummary] = {}
    for genre in sorted(grouped):
        rows = grouped[genre]
        feature_names = sorted({name for row in rows for name in row.features})
        medians: dict[str, float] = {}
        bands: dict[str, RangeBand] = {}
        for feature_name in feature_names:
            samples = tuple(row.features[feature_name] for row in rows if feature_name in row.features)
            if not samples:
                continue
            distribution = ScalarDistribution(samples)
            medians[feature_name] = distribution.median()
            bands[feature_name] = distribution.to_range_band()
        summaries[genre] = CorpusGenreSummary(
            genre=genre,
            observation_count=len(rows),
            medians=medians,
            feature_bands=bands,
        )
    return MappingProxyType(dict(sorted(summaries.items())))
