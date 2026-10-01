import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fusion_lab.mix_truth import mix_with_levels


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


if __name__ == "__main__":
    unittest.main()
