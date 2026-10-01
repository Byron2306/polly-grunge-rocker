from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from .distributions import blend_categorical, blend_range_bands
from .model import (
    ArrangementDNA,
    BassDNA,
    DNAComponent,
    DrumDNA,
    GenreDNA,
    GuitarDNA,
    HardConstraint,
    HarmonyDNA,
    KeysDNA,
    ProductionDNA,
    VocalDNA,
)


@dataclass(frozen=True, slots=True)
class BlendConflict:
    id: str
    values: tuple[bool, ...]


@dataclass(frozen=True, slots=True)
class BlendResult:
    profile: GenreDNA | None
    normalized_weights: tuple[float, ...]
    conflicts: tuple[BlendConflict, ...]


def _normalized_weights(weighted: Sequence[tuple[float, GenreDNA]]) -> tuple[float, ...]:
    if not weighted:
        raise ValueError('weighted genres must be non-empty')
    values = tuple(float(weight) for weight, _ in weighted)
    if any((not isfinite(weight)) or weight < 0 for weight in values):
        raise ValueError('blend weights must be finite and >= 0')
    total = sum(values)
    if total <= 0:
        raise ValueError('blend weights must contain positive mass')
    return tuple(weight / total for weight in values)


def _constraint_conflicts(prefix: str, components: Sequence[DNAComponent]) -> tuple[BlendConflict, ...]:
    values_by_id: dict[str, set[bool]] = {}
    for component in components:
        for constraint in component.hard_constraints:
            values_by_id.setdefault(constraint.id, set()).add(constraint.required)
    return tuple(
        BlendConflict(f'{prefix}.{constraint_id}', tuple(sorted(values)))
        for constraint_id, values in sorted(values_by_id.items())
        if len(values) > 1
    )


def _blend_constraints(components: Sequence[DNAComponent]) -> tuple[HardConstraint, ...]:
    seen: dict[str, bool] = {}
    for component in components:
        for constraint in component.hard_constraints:
            seen[constraint.id] = constraint.required
    return tuple(HardConstraint(key, seen[key]) for key in sorted(seen))


def _blend_component(cls, weighted: Sequence[tuple[float, DNAComponent]]) -> DNAComponent:
    keys = sorted({key for _, component in weighted for key in component.features})
    features = {}
    for key in keys:
        rows = [(weight, component.features[key]) for weight, component in weighted if key in component.features]
        features[key] = blend_range_bands(rows)
    return cls(
        features=features,
        hard_constraints=_blend_constraints([component for _, component in weighted]),
    )


def blend_genres(weighted: Sequence[tuple[float, GenreDNA]], *, blend_id: str) -> BlendResult:
    if not blend_id:
        raise ValueError('blend_id is required')
    normalized = _normalized_weights(weighted)
    profiles = tuple(profile for _, profile in weighted)

    conflicts: list[BlendConflict] = []
    for prefix, attr in (
        ('harmony', 'harmony'),
        ('guitar', 'guitar'),
        ('bass', 'bass'),
        ('drums', 'drums'),
        ('vocals', 'vocals'),
        ('keys', 'keys'),
        ('arrangement', 'arrangement'),
        ('production', 'production'),
    ):
        conflicts.extend(_constraint_conflicts(prefix, [getattr(profile, attr) for profile in profiles]))
    if conflicts:
        return BlendResult(None, normalized, tuple(sorted(conflicts, key=lambda conflict: conflict.id)))

    normalized_profiles = tuple(zip(normalized, profiles))
    profile = GenreDNA(
        id=blend_id,
        tempo=blend_range_bands([(weight, item.tempo) for weight, item in normalized_profiles]),
        meters=blend_categorical([(weight, item.meters) for weight, item in normalized_profiles]),
        harmony=_blend_component(HarmonyDNA, [(w, p.harmony) for w, p in normalized_profiles]),
        guitar=_blend_component(GuitarDNA, [(w, p.guitar) for w, p in normalized_profiles]),
        bass=_blend_component(BassDNA, [(w, p.bass) for w, p in normalized_profiles]),
        drums=_blend_component(DrumDNA, [(w, p.drums) for w, p in normalized_profiles]),
        vocals=_blend_component(VocalDNA, [(w, p.vocals) for w, p in normalized_profiles]),
        keys=_blend_component(KeysDNA, [(w, p.keys) for w, p in normalized_profiles]),
        arrangement=_blend_component(ArrangementDNA, [(w, p.arrangement) for w, p in normalized_profiles]),
        production=_blend_component(ProductionDNA, [(w, p.production) for w, p in normalized_profiles]),
    )
    return BlendResult(profile, normalized, ())
