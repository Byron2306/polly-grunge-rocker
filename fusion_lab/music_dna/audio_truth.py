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
            'mute': self.mute.__dict__ if hasattr(self.mute, '__dict__') else {
                'rms': self.mute.rms,
                'peak': self.mute.peak,
                'crest_factor': self.mute.crest_factor,
                'early_rms': self.mute.early_rms,
                'late_rms': self.mute.late_rms,
                'alive': self.mute.alive,
            },
            'sustain': self.sustain.__dict__ if hasattr(self.sustain, '__dict__') else {
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
    return mono, channels


def _rms(values: list[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(value * value for value in values) / len(values))


def analyze_wav(path: Path) -> WavMetrics:
    values, _ = _decode_pcm_frames(Path(path))
    if not values:
        return WavMetrics(0.0, 0.0, 0.0, 0.0, 0.0, False)
    rms = _rms(values)
    peak = max(abs(value) for value in values)
    split = max(1, len(values) // 4)
    early = _rms(values[:split])
    late = _rms(values[-split:])
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
