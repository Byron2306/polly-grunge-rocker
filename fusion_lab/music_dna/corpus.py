from __future__ import annotations

import json
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from types import MappingProxyType
from typing import Mapping


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
