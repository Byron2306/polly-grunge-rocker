from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Mapping


def mix_with_levels(
    stems: Mapping[str, Path],
    mix_path: Path,
    *,
    levels: Mapping[str, float],
    limiter: float = 0.95,
) -> None:
    if not stems:
        raise RuntimeError("PRODUCTION_NO_STEMS")
    for name, path in stems.items():
        if not Path(path).is_file():
            raise RuntimeError(f"PRODUCTION_MISSING_STEM: {name}")
        if name not in levels:
            raise RuntimeError(f"PRODUCTION_MISSING_MIX_LEVEL: {name}")
        if levels[name] < 0:
            raise RuntimeError(f"PRODUCTION_INVALID_MIX_LEVEL: {name}")
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("PRODUCTION_MISSING_MIXER: ffmpeg")
    ordered = list(stems.items())
    cmd = [ffmpeg, "-y"]
    for _, path in ordered:
        cmd += ["-i", str(path)]
    labels = []
    chains = []
    for i, (name, _) in enumerate(ordered):
        label = f"s{i}"
        labels.append(f"[{label}]")
        chains.append(f"[{i}:a]volume={levels[name]:.6f}[{label}]")
    graph = ";".join(chains + [f"{''.join(labels)}amix=inputs={len(ordered)}:normalize=0,alimiter=limit={limiter:.3f}[mix]"])
    cmd += ["-filter_complex", graph, "-map", "[mix]", "-c:a", "pcm_s16le", str(mix_path)]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


THRASH_1988_MIX_LEVELS = {
    "rhythm_guitar_L": 1.00,
    "rhythm_guitar_R": 1.00,
    "bass": 0.32,
    "drums": 0.78,
    "lead_guitar": 0.42,
}
