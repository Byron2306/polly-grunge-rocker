from __future__ import annotations

import json
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Type

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
    RangeBand,
    VocalDNA,
)


_COMPONENTS: dict[str, Type[DNAComponent]] = {
    'harmony': HarmonyDNA,
    'guitar': GuitarDNA,
    'bass': BassDNA,
    'drums': DrumDNA,
    'vocals': VocalDNA,
    'keys': KeysDNA,
    'arrangement': ArrangementDNA,
    'production': ProductionDNA,
}


def _band(raw) -> RangeBand:
    if not isinstance(raw, list) or len(raw) != 4:
        raise ValueError('range bands must contain four numbers')
    return RangeBand(*(float(x) for x in raw))


def _component(name: str, raw: dict) -> DNAComponent:
    if not isinstance(raw, dict) or 'features' not in raw:
        raise ValueError(f'missing required component data: {name}')
    features = {key: _band(value) for key, value in raw['features'].items()}
    constraints = tuple(
        HardConstraint(str(row['id']), bool(row['required']))
        for row in raw.get('hard_constraints', ())
    )
    return _COMPONENTS[name](features=features, hard_constraints=constraints)


def load_genre_profile(path: Path) -> GenreDNA:
    raw = json.loads(Path(path).read_text())
    required = {'id', 'tempo', 'meters', *_COMPONENTS.keys()}
    missing = sorted(required - set(raw))
    if missing:
        raise ValueError(f'missing required profile components: {missing}')
    if raw.get('schema') != 'polly.music-dna.genre-profile.v1':
        raise ValueError('invalid genre profile schema')
    return GenreDNA(
        id=str(raw['id']),
        tempo=_band(raw['tempo']),
        meters=MappingProxyType(dict(sorted((str(k), float(v)) for k, v in raw['meters'].items()))),
        **{name: _component(name, raw[name]) for name in _COMPONENTS},
    )


def load_seed_genre_profiles(root: Path) -> Mapping[str, GenreDNA]:
    profiles = [load_genre_profile(path) for path in sorted(Path(root).glob('*.json'))]
    if not profiles:
        raise ValueError('no genre profiles found')
    result: dict[str, GenreDNA] = {}
    for profile in profiles:
        if profile.id in result:
            raise ValueError(f'duplicate genre profile id: {profile.id}')
        result[profile.id] = profile
    return MappingProxyType(dict(sorted(result.items())))
