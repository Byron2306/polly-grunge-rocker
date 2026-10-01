import tempfile
import unittest
from pathlib import Path

from fusion_lab.metal_gtx_compat import prepare_metal_gtx_sfizz_clean


class MetalGtxCompatTests(unittest.TestCase):
    def test_clean_patches_strip_keyswitch_state_and_preserve_sample_resolution(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "Individual Patchs"
            samples = root / "Samples" / "Mute_Down"
            samples.mkdir(parents=True)
            (samples / "e2.flac").write_bytes(b"sample")

            for set_name in ("METAL-GTX_Full", "METAL-GTX_XTracking"):
                source = root / set_name
                source.mkdir(parents=True)
                for art in ("Mute_Down", "Mute_Up", "Sus_Down", "Sus_Up"):
                    (source / f"{art}.sfz").write_text(
                        "<global>\n"
                        "sw_lokey=e-1\n"
                        "sw_hikey=c8\n"
                        "sw_last=g#0\n"
                        "sw_default=g#0\n"
                        "<region>\n"
                        "sample=..\\Samples\\Mute_Down\\e2.flac\n"
                        "seq_length=9\n"
                        "seq_position=1\n"
                        "lokey=E2\n"
                        "hikey=E2\n"
                    )

            clean = prepare_metal_gtx_sfizz_clean(root)

            self.assertEqual(clean, root / "SFIZZ_CLEAN")
            self.assertTrue((clean / "Samples").is_symlink())
            self.assertEqual((clean / "Samples").readlink(), Path("../Samples"))

            patch = clean / "METAL-GTX_Full" / "Mute_Down.sfz"
            text = patch.read_text()
            self.assertNotIn("sw_lokey=", text)
            self.assertNotIn("sw_hikey=", text)
            self.assertNotIn("sw_last=", text)
            self.assertNotIn("sw_default=", text)
            self.assertIn(r"sample=..\Samples\Mute_Down\e2.flac", text)

            resolved_sample = clean / "Samples" / "Mute_Down" / "e2.flac"
            self.assertTrue(resolved_sample.is_file())


if __name__ == "__main__":
    unittest.main()
