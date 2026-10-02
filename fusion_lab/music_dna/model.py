from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from types import MappingProxyType
from typing import Mapping


PROBABILITY_FEATURE_SUFFIXES = (
    '_ratio',
    '_probability',
    '_rate',
    '_recurrence',
    '_independence',
    '_chromaticity',
)


def _frozen_mapping(values: Mapping[str, object]) -> Mapping[str, object]:
    return MappingProxyType(dict(sorted(values.items())))


class DecisionState(str, Enum):
    ALLOW = 'ALLOW'
    MUTATE = 'MUTATE'
    REJECT = 'REJECT'


@dataclass(frozen=True, slots=True)
class RangeBand:
    minimum: float
    preferred_minimum: float
    preferred_maximum: float
    maximum: float

    def __post_init__(self) -> None:
        values = (self.minimum, self.preferred_minimum, self.preferred_maximum, self.maximum)
        if not all(isfinite(value) for value in values):
            raise ValueError('range values must be finite')
        if not self.minimum <= self.preferred_minimum <= self.preferred_maximum <= self.maximum:
            raise ValueError('range bounds must be ordered')

    def normalized_distance(self, value: float) -> float:
        if not isfinite(value):
            raise ValueError('value must be finite')
        if self.preferred_minimum <= value <= self.preferred_maximum:
            return 0.0
        if value < self.preferred_minimum:
            span = self.preferred_minimum - self.minimum
            return 1.0 if span == 0 else (self.preferred_minimum - value) / span
        span = self.maximum - self.preferred_maximum
        return 1.0 if span == 0 else (value - self.preferred_maximum) / span


@dataclass(frozen=True, slots=True)
class FeatureVector:
    values: Mapping[str, float]

    def __post_init__(self) -> None:
        clean: dict[str, float] = {}
        for name, raw in self.values.items():
            value = float(raw)
            if not isfinite(value):
                raise ValueError(f'feature must be finite: {name}')
            if name.endswith(PROBABILITY_FEATURE_SUFFIXES) and not 0.0 <= value <= 1.0:
                raise ValueError(f'probability-like feature must be within 0..1: {name}')
            clean[str(name)] = value
        object.__setattr__(self, 'values', _frozen_mapping(clean))


@dataclass(frozen=True, slots=True)
class HardConstraint:
    id: str
    required: bool

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError('constraint id must be non-empty')


@dataclass(frozen=True, slots=True)
class GenreDecision:
    state: DecisionState
    genre: str
    reasons: tuple[str, ...]
    distance: float

    def __post_init__(self) -> None:
        if not self.genre:
            raise ValueError('genre must be non-empty')
        if not isfinite(self.distance) or self.distance < 0:
            raise ValueError('distance must be finite and >= 0')
        object.__setattr__(self, 'reasons', tuple(self.reasons))


@dataclass(frozen=True, slots=True)
class MusicDNAReport:
    genre_profile: str
    feature_vector: Mapping[str, float]
    coupling: Mapping[str, float]
    hook_score: Mapping[str, float]
    riff_structure: Mapping[str, object]
    production_truth: Mapping[str, object]
    decision: GenreDecision

    def to_dict(self) -> dict:
        return {
            'genre_profile': self.genre_profile,
            'feature_vector': dict(sorted(self.feature_vector.items())),
            'coupling': dict(sorted(self.coupling.items())),
            'hook_score': dict(sorted(self.hook_score.items())),
            'riff_structure': dict(self.riff_structure),
            'production_truth': dict(sorted(self.production_truth.items())),
            'decision': {
                'state': self.decision.state.value,
                'genre': self.decision.genre,
                'reasons': list(self.decision.reasons),
                'distance': self.decision.distance,
            },
        }


@dataclass(frozen=True, slots=True)
class DNAComponent:
    features: Mapping[str, RangeBand]
    hard_constraints: tuple[HardConstraint, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, 'features', _frozen_mapping(self.features))
        object.__setattr__(self, 'hard_constraints', tuple(self.hard_constraints))


@dataclass(frozen=True, slots=True)
class HarmonyDNA(DNAComponent):
    pass


@dataclass(frozen=True, slots=True)
class GuitarDNA(DNAComponent):
    pass


@dataclass(frozen=True, slots=True)
class BassDNA(DNAComponent):
    pass


@dataclass(frozen=True, slots=True)
class DrumDNA(DNAComponent):
    pass


@dataclass(frozen=True, slots=True)
class VocalDNA(DNAComponent):
    pass


@dataclass(frozen=True, slots=True)
class KeysDNA(DNAComponent):
    pass


@dataclass(frozen=True, slots=True)
class ArrangementDNA(DNAComponent):
    pass


@dataclass(frozen=True, slots=True)
class ProductionDNA(DNAComponent):
    pass


@dataclass(frozen=True, slots=True)
class RiffStructureDNA(DNAComponent):
    pass


@dataclass(frozen=True, slots=True)
class GenreDNA:
    id: str
    tempo: RangeBand
    meters: Mapping[str, float]
    harmony: HarmonyDNA
    guitar: GuitarDNA
    bass: BassDNA
    drums: DrumDNA
    vocals: VocalDNA
    keys: KeysDNA
    arrangement: ArrangementDNA
    production: ProductionDNA
    riff_structure: RiffStructureDNA | None = None

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError('genre id must be non-empty')
        object.__setattr__(self, 'meters', _frozen_mapping(self.meters))
