from __future__ import annotations

import math
import shutil
import struct
import subprocess
import wave
from pathlib import Path
from typing import Mapping


def _peak_dbfs(path: Path) -> float:
    path = Path(path)
    with wave.open(str(path), 'rb') as wav:
        if wav.getsampwidth() != 2:
            raise RuntimeError(f'PRODUCTION_UNSUPPORTED_STEM_FORMAT: {path}')
        channels = wav.getnchannels()
        frames = wav.readframes(wav.getnframes())
    if not frames:
        return -120.0
    values = struct.unpack('<' + 'h' * (len(frames) // 2), frames)
    peak = max(abs(value) for value in values) / 32768.0
    if channels < 1 or peak <= 0.0:
        return -120.0
    return 20.0 * math.log10(peak)


# Thrash target hierarchy: drums lead the violence, bass is audible as a
# picked instrument, and the two rhythm guitars remain wide without masking
# the whole rhythm section.
THRASH_1988_TARGET_PEAKS_DBFS = {
    'rhythm_guitar_L': -16.0,
    'rhythm_guitar_R': -16.0,
    'bass': -13.5,
    'drums': -12.5,
    'lead_guitar': -18.0,
}


def calibrate_thrash_mix_levels(
    stems: Mapping[str, Path],
    *,
    targets: Mapping[str, float] = THRASH_1988_TARGET_PEAKS_DBFS,
    max_makeup_db: float = 30.0,
    minimum_live_peak_dbfs: float = -70.0,
) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    expected = set(targets)
    if set(stems) != expected:
        missing = sorted(expected - set(stems))
        extra = sorted(set(stems) - expected)
        raise RuntimeError(f'PRODUCTION_MIX_STEM_SET_MISMATCH: missing={missing}; extra={extra}')

    levels: dict[str, float] = {}
    evidence: dict[str, dict[str, float]] = {}
    for name in sorted(stems):
        source_peak = _peak_dbfs(Path(stems[name]))
        if source_peak < minimum_live_peak_dbfs:
            raise RuntimeError(f'PRODUCTION_INAUDIBLE_STEM: {name}; peak_dbfs={source_peak:.2f}')
        target_peak = float(targets[name])
        gain_db = target_peak - source_peak
        if gain_db > max_makeup_db:
            raise RuntimeError(
                f'PRODUCTION_EXCESSIVE_MAKEUP_REQUIRED: {name}; '
                f'source_peak_dbfs={source_peak:.2f}; target_peak_dbfs={target_peak:.2f}; gain_db={gain_db:.2f}'
            )
        gain = 10.0 ** (gain_db / 20.0)
        levels[name] = gain
        evidence[name] = {
            'source_peak_dbfs': source_peak,
            'target_peak_dbfs': target_peak,
            'gain_db': gain_db,
            'gain': gain,
        }
    return levels, evidence


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
    mix_path = Path(mix_path)
    mix_path.parent.mkdir(parents=True, exist_ok=True)
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


# Legacy fixed faders retained for old tests/configs only. V5 production uses
# calibrate_thrash_mix_levels() against the rendered stems instead.
THRASH_1988_MIX_LEVELS = {
    "rhythm_guitar_L": 1.00,
    "rhythm_guitar_R": 1.00,
    "bass": 0.32,
    "drums": 0.78,
    "lead_guitar": 0.42,
}
