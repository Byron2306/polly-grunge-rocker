from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import struct
import wave


@dataclass(frozen=True, slots=True)
class WavMetrics:
    rms: float
    peak: float
    crest_factor: float
    early_rms: float
    late_rms: float
    alive: bool


@dataclass(frozen=True, slots=True)
class ArticulationAudioTruth:
    ok: bool
    reasons: tuple[str, ...]
    envelope_distance: float
    mute: WavMetrics
    sustain: WavMetrics

    def to_dict(self) -> dict:
        return {
            'ok': self.ok,
            'reasons': list(self.reasons),
            'envelope_distance': self.envelope_distance,
            'mute': {
                'rms': self.mute.rms,
                'peak': self.mute.peak,
                'crest_factor': self.mute.crest_factor,
                'early_rms': self.mute.early_rms,
                'late_rms': self.mute.late_rms,
                'alive': self.mute.alive,
            },
            'sustain': {
                'rms': self.sustain.rms,
                'peak': self.sustain.peak,
                'crest_factor': self.sustain.crest_factor,
                'early_rms': self.sustain.early_rms,
                'late_rms': self.sustain.late_rms,
                'alive': self.sustain.alive,
            },
        }


def _decode_pcm_frames(path: Path) -> tuple[list[float], int]:
    with wave.open(str(path), 'rb') as wav:
        channels = wav.getnchannels()
        sampwidth = wav.getsampwidth()
        sample_rate = wav.getframerate()
        frames = wav.readframes(wav.getnframes())
    if sampwidth != 2:
        raise ValueError('only 16-bit PCM WAV is supported for audio truth')
    values = struct.unpack('<' + 'h' * (len(frames) // 2), frames)
    if channels <= 1:
        mono = [value / 32768.0 for value in values]
    else:
        mono = []
        for i in range(0, len(values), channels):
            frame = values[i:i + channels]
            mono.append(sum(frame) / (len(frame) * 32768.0))
    return mono, sample_rate


def _rms(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return math.sqrt(sum(value * value for value in values) / len(values))


def _mean(values: list[float]) -> float:
    return 0.0 if not values else sum(values) / len(values)


def _local_envelope(values: list[float], sample_rate: int) -> tuple[float, float]:
    """Estimate attack and tail energy around actual note onsets.

    Articulation stems are often tens of seconds long with silence between notes.
    Comparing the first/last quarter of the entire file measures arrangement, not
    articulation. Use short RMS blocks, find attacks that begin after silence,
    and compare the local attack to its immediate tail instead.
    """
    if not values or sample_rate <= 0:
        return 0.0, 0.0

    block_frames = max(1, int(sample_rate * 0.010))  # 10 ms
    blocks = [
        _rms(values[i:i + block_frames])
        for i in range(0, len(values), block_frames)
    ]
    if not blocks:
        return 0.0, 0.0

    peak_block = max(blocks)
    threshold = max(0.001, peak_block * 0.08)
    quiet_threshold = threshold * 0.50

    onsets: list[int] = []
    for i, energy in enumerate(blocks):
        if energy < threshold:
            continue
        if i == 0 or all(blocks[j] < quiet_threshold for j in range(max(0, i - 3), i)):
            onsets.append(i)

    # Continuous synthetic probes may begin immediately and never cross back
    # through silence. Their start is still a valid attack.
    if not onsets and blocks[0] >= threshold:
        onsets = [0]

    early_values: list[float] = []
    late_values: list[float] = []
    for onset in onsets:
        early_slice = blocks[onset:min(len(blocks), onset + 3)]       # 0-30 ms
        late_slice = blocks[min(len(blocks), onset + 8):min(len(blocks), onset + 18)]  # 80-180 ms
        if not early_slice or not late_slice:
            continue
        early_values.append(max(early_slice))
        late_values.append(_mean(late_slice))

    if early_values:
        return _mean(early_values), _mean(late_values)

    # Last-resort fallback for very short files: compare local beginning/end,
    # never file quarters on a long sparse stem.
    window = min(len(values), max(1, int(sample_rate * 0.050)))
    return _rms(values[:window]), _rms(values[-window:])


def analyze_wav(path: Path) -> WavMetrics:
    values, sample_rate = _decode_pcm_frames(Path(path))
    if not values:
        return WavMetrics(0.0, 0.0, 0.0, 0.0, 0.0, False)
    rms = _rms(values)
    peak = max(abs(value) for value in values)
    early, late = _local_envelope(values, sample_rate)
    crest = 0.0 if rms == 0 else peak / rms
    alive = rms >= 0.001 and peak >= 0.003
    return WavMetrics(rms, peak, crest, early, late, alive)


def validate_articulation_audio(mute_path: Path, sustain_path: Path) -> ArticulationAudioTruth:
    mute = analyze_wav(mute_path)
    sustain = analyze_wav(sustain_path)
    reasons: list[str] = []
    if not mute.alive:
        reasons.append('palm_mute_render_dead')
    if not sustain.alive:
        reasons.append('sustain_render_dead')

    mute_decay = 0.0 if mute.early_rms == 0 else max(0.0, 1.0 - mute.late_rms / mute.early_rms)
    sustain_decay = 0.0 if sustain.early_rms == 0 else max(0.0, 1.0 - sustain.late_rms / sustain.early_rms)
    envelope_distance = abs(mute_decay - sustain_decay)
    if mute.alive and sustain.alive and envelope_distance < 0.05:
        reasons.append('palm_mute_envelope_not_distinct')

    return ArticulationAudioTruth(not reasons, tuple(sorted(reasons)), envelope_distance, mute, sustain)
