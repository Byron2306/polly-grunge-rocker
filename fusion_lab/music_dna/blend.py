from __future__ import annotations

from types import MappingProxyType
from typing import Iterable, Sequence

from .distributions import blend_categorical, blend_range_bands
from .model import (
    ArrangementDNA,
    BassDNA,
    DrumDNA,
    GenreDNA,
    GuitarDNA,
    HarmonyDNA,
    KeysDNA,
    ProductionDNA,
    VocalDNA,
    HardConstraint,
    DNAComponent,
)


class BlendConflictError(ValueError):
    pass


def _blend_constraints(weighted_components: Sequence[tuple[float, DNAComponent]]) -> tuple[HardConstraint, ...]:
    seen: dict[str, bool] = {}
    for _, component in weighted_components:
        for constraint in component.hard_constraints:
            previous = seen.get(constraint.id)
            if previous is not None and previous != constraint.required:
                raise BlendConflictError(f'conflicting hard constraint: {constraint.id}')
            seen[constraint.id] = constraint.required
    return tuple(HardConstraint(key, seen[key]) for key in sorted(seen))


def _blend_component(cls, weighted: Sequence[tuple[float, DNAComponent]]) -> DNAComponent:
    keys = sorted({key for _, component in weighted for key in component.features})
    features = {}
    for key in keys:
        rows = [(weight, component.features[key]) for weight, component in weighted if key in component.features]
        features[key] = blend_range_bands(rows)
    return cls(features=features, hard_constraints=_blend_constraints(weighted))


def blend_genres(weighted: Sequence[tuple[float, GenreDNA]], *, blend_id: str) -> GenreDNA:
    if not blend_id:
        raise ValueError('blend_id is required')
    if not weighted:
        raise ValueError('weighted genres must be non-empty')

    return GenreDNA(
        id=blend_id,
        tempo=blend_range_bands([(weight, profile.tempo) for weight, profile in weighted]),
        meters=blend_categorical([(weight, profile.meters) for weight, profile in weighted]),
        harmony=_blend_component(HarmonyDNA, [(w, p.harmony) for w, p in weighted]),
        guitar=_blend_component(GuitarDNA, [(w, p.guitar) for w, p in weighted]),
        bass=_blend_component(BassDNA, [(w, p.bass) for w, p in weighted]),
        drums=_blend_component(DrumDNA, [(w, p.drums) for w, p in weighted]),
        vocals=_blend_component(VocalDNA, [(w, p.vocals) for w, p in weighted]),
        keys=_blend_component(KeysDNA, [(w, p.keys) for w, p in weighted]),
        arrangement=_blend_component(ArrangementDNA, [(w, p.arrangement) for w, p in weighted]),
        production=_blend_component(ProductionDNA, [(w, p.production) for w, p in weighted]),
    )
