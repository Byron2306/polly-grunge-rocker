from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from types import MappingProxyType
from typing import Mapping, Sequence

from .model import RangeBand


@dataclass(frozen=True, slots=True)
class ScalarDistribution:
    samples: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.samples:
            raise ValueError('samples must be non-empty')
        clean = tuple(float(v) for v in self.samples)
        if not all(isfinite(v) for v in clean):
            raise ValueError('samples must be finite')
        object.__setattr__(self, 'samples', clean)

    def median(self) -> float:
        values = sorted(self.samples)
        n = len(values)
        mid = n // 2
        if n % 2:
            return values[mid]
        return (values[mid - 1] + values[mid]) / 2.0

    def to_range_band(self) -> RangeBand:
        values = sorted(self.samples)
        n = len(values)
        q1 = values[max(0, (n - 1) // 4)]
        q3 = values[min(n - 1, ((n - 1) * 3) // 4)]
        return RangeBand(values[0], q1, q3, values[-1])


@dataclass(frozen=True, slots=True)
class CategoricalDistribution:
    weights: Mapping[str, float]

    def __post_init__(self) -> None:
        clean: dict[str, float] = {}
        for key, raw in self.weights.items():
            value = float(raw)
            if not isfinite(value) or value < 0:
                raise ValueError('categorical weights must be finite and >= 0')
            clean[str(key)] = value
        if not clean or sum(clean.values()) <= 0:
            raise ValueError('categorical weights must contain positive mass')
        object.__setattr__(self, 'weights', MappingProxyType(dict(sorted(clean.items()))))

    def normalized(self) -> Mapping[str, float]:
        total = sum(self.weights.values())
        return MappingProxyType({key: value / total for key, value in self.weights.items()})


def _normalize_mix_weights(weighted: Sequence[tuple[float, object]]) -> tuple[tuple[float, object], ...]:
    if not weighted:
        raise ValueError('weighted inputs must be non-empty')
    clean: list[tuple[float, object]] = []
    total = 0.0
    for raw_weight, value in weighted:
        weight = float(raw_weight)
        if not isfinite(weight) or weight < 0:
            raise ValueError('blend weights must be finite and >= 0')
        clean.append((weight, value))
        total += weight
    if total <= 0:
        raise ValueError('blend weights must contain positive mass')
    return tuple((weight / total, value) for weight, value in clean)


def blend_range_bands(weighted: Sequence[tuple[float, RangeBand]]) -> RangeBand:
    normalized = _normalize_mix_weights(weighted)
    bands = [band for _, band in normalized]
    preferred_minimum = sum(weight * band.preferred_minimum for weight, band in normalized)
    preferred_maximum = sum(weight * band.preferred_maximum for weight, band in normalized)
    return RangeBand(
        min(band.minimum for band in bands),
        preferred_minimum,
        preferred_maximum,
        max(band.maximum for band in bands),
    )


def blend_categorical(
    weighted: Sequence[tuple[float, Mapping[str, float]]],
) -> Mapping[str, float]:
    normalized = _normalize_mix_weights(weighted)
    totals: dict[str, float] = {}
    for weight, values in normalized:
        dist = CategoricalDistribution(values).normalized()
        for key, value in dist.items():
            totals[key] = totals.get(key, 0.0) + weight * value
    total = sum(totals.values())
    return MappingProxyType({key: totals[key] / total for key in sorted(totals)})
