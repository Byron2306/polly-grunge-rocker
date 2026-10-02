import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

from fusion_lab.mix_truth import calibrate_thrash_mix_levels, mix_with_levels


def write_peak_wave(path: Path, peak_db: float):
    amp = 10.0 ** (peak_db / 20.0)
    sample = int(max(-32767, min(32767, amp * 32767)))
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(48000)
        wav.writeframes(struct.pack('<h', sample) * 4800)


class MixTruthTests(unittest.TestCase):
    def test_mix_uses_explicit_per_stem_faders(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stems = {}
            for name in ("rhythm_guitar_L", "rhythm_guitar_R", "bass", "drums", "lead_guitar"):
                p = root / f"{name}.wav"
                p.write_bytes(b"x")
                stems[name] = p
            levels = {
                "rhythm_guitar_L": 1.0,
                "rhythm_guitar_R": 1.0,
                "bass": 0.32,
                "drums": 0.78,
                "lead_guitar": 0.42,
            }
            with patch("fusion_lab.mix_truth.shutil.which", return_value="/usr/bin/ffmpeg"), patch("fusion_lab.mix_truth.subprocess.run") as run:
                mix_with_levels(stems, root / "mix.wav", levels=levels)
                cmd = run.call_args.args[0]
                graph = cmd[cmd.index("-filter_complex") + 1]
                self.assertIn("volume=1.000000", graph)
                self.assertIn("volume=0.320000", graph)
                self.assertIn("volume=0.780000", graph)
                self.assertIn("amix=inputs=5:normalize=0", graph)

    def test_mix_refuses_missing_level(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = root / "g.wav"
            p.write_bytes(b"x")
            with self.assertRaisesRegex(RuntimeError, "PRODUCTION_MISSING_MIX_LEVEL"):
                mix_with_levels({"g": p}, root / "mix.wav", levels={})

    def test_thrash_calibration_recovers_quiet_drums_without_strangling_bass(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            peaks = {
                'rhythm_guitar_L': -12.8,
                'rhythm_guitar_R': -13.4,
                'bass': -12.5,
                'drums': -39.6,
                'lead_guitar': -12.2,
            }
            stems = {}
            for name, peak_db in peaks.items():
                path = root / f'{name}.wav'
                write_peak_wave(path, peak_db)
                stems[name] = path

            levels, evidence = calibrate_thrash_mix_levels(stems)

            self.assertGreater(levels['drums'], 10.0)
            self.assertGreater(levels['bass'], 0.5)
            self.assertLess(levels['bass'], 1.0)
            self.assertLess(levels['lead_guitar'], 0.8)
            self.assertAlmostEqual(evidence['drums']['target_peak_dbfs'], -14.0)
            self.assertAlmostEqual(evidence['bass']['target_peak_dbfs'], -16.0)
            for name, row in evidence.items():
                achieved = row['source_peak_dbfs'] + 20.0 * math.log10(row['gain'])
                self.assertAlmostEqual(achieved, row['target_peak_dbfs'], delta=0.15, msg=name)

    def test_thrash_calibration_refuses_dead_stem(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stems = {}
            for name in ('rhythm_guitar_L', 'rhythm_guitar_R', 'bass', 'drums', 'lead_guitar'):
                path = root / f'{name}.wav'
                write_peak_wave(path, -120.0 if name == 'drums' else -14.0)
                stems[name] = path
            with self.assertRaisesRegex(RuntimeError, 'PRODUCTION_INAUDIBLE_STEM: drums'):
                calibrate_thrash_mix_levels(stems)


if __name__ == "__main__":
    unittest.main()
