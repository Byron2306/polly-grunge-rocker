import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from fusion_lab.music_dna.audio_truth import analyze_wav, validate_articulation_audio


def write_wave(path: Path, *, amplitude: float, decay: float = 1.0, frames: int = 4800):
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(48000)
        payload = bytearray()
        for i in range(frames):
            env = math.exp(-decay * i / frames)
            sample = int(max(-32767, min(32767, amplitude * env * 32767 * math.sin(2 * math.pi * 220 * i / 48000))))
            payload += struct.pack('<h', sample)
        wav.writeframes(bytes(payload))


class AudioTruthTests(unittest.TestCase):
    def test_constant_near_zero_wav_is_dead(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'dead.wav'
            with wave.open(str(path), 'wb') as wav:
                wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(48000)
                wav.writeframes(struct.pack('<h', -1) * 4800)
            metrics = analyze_wav(path)
            self.assertLess(metrics.rms, 0.001)
            self.assertFalse(metrics.alive)

    def test_live_mute_and_sustain_need_distinct_envelopes(self):
        with tempfile.TemporaryDirectory() as d:
            mute = Path(d) / 'mute.wav'; sustain = Path(d) / 'sustain.wav'
            write_wave(mute, amplitude=0.5, decay=6.0)
            write_wave(sustain, amplitude=0.5, decay=0.5)
            result = validate_articulation_audio(mute, sustain)
            self.assertTrue(result.ok)
            self.assertGreater(result.envelope_distance, 0.05)

    def test_dead_mute_is_refused_even_when_sustain_is_healthy(self):
        with tempfile.TemporaryDirectory() as d:
            mute = Path(d) / 'mute.wav'; sustain = Path(d) / 'sustain.wav'
            write_wave(mute, amplitude=0.00001, decay=6.0)
            write_wave(sustain, amplitude=0.5, decay=0.5)
            result = validate_articulation_audio(mute, sustain)
            self.assertFalse(result.ok)
            self.assertIn('palm_mute_render_dead', result.reasons)


if __name__ == '__main__':
    unittest.main()
