import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fusion_lab.production_render import mix_production_stems


class ProductionMixDiagnosticsTests(unittest.TestCase):
    def test_ffmpeg_mix_failure_includes_stderr_and_stem_names(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stems = {}
            for name in ('mute', 'sustain'):
                p = root / f'{name}.wav'
                p.write_bytes(b'RIFF')
                stems[name] = p

            failure = subprocess.CalledProcessError(
                254,
                ['/usr/bin/ffmpeg'],
                stderr='filter graph exploded',
            )
            with patch('fusion_lab.production_render.shutil.which', return_value='/usr/bin/ffmpeg'), patch(
                'fusion_lab.production_render.subprocess.run', side_effect=failure
            ):
                with self.assertRaises(RuntimeError) as ctx:
                    mix_production_stems(stems, root / 'mix.wav')

            message = str(ctx.exception)
            self.assertIn('PRODUCTION_MIX_FAILED', message)
            self.assertIn('filter graph exploded', message)
            self.assertIn('mute=', message)
            self.assertIn('sustain=', message)

    def test_mix_creates_destination_parent_before_ffmpeg_runs(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / 'source.wav'
            source.write_bytes(b'RIFF')
            destination = root / 'nested' / 'clean' / 'mix.wav'

            def verify_parent_then_succeed(*args, **kwargs):
                self.assertTrue(destination.parent.is_dir())
                return subprocess.CompletedProcess(args[0], 0, '', '')

            with patch('fusion_lab.production_render.shutil.which', return_value='/usr/bin/ffmpeg'), patch(
                'fusion_lab.production_render.subprocess.run', side_effect=verify_parent_then_succeed
            ):
                mix_production_stems({'source': source}, destination)


if __name__ == '__main__':
    unittest.main()
