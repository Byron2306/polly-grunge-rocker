import os
import sys
import tempfile
import unittest
import wave
from pathlib import Path

from fusion_lab.music_dna.production_topology import execute_tone_chain_with_evidence
from fusion_lab.production_model import ToneControls, ToneProfile, ToneStage


def write_silence(path: Path):
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(48000)
        wav.writeframes(b'\x00\x00' * 480)


class RealAmpCabChainTests(unittest.TestCase):
    def test_fake_external_stage_executes_in_order_and_records_cabinet(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / 'in.wav'; output = root / 'out.wav'; cab = root / 'cab.wav'; script = root / 'fake.py'
            write_silence(source); write_silence(cab)
            script.write_text('''from pathlib import Path\nimport shutil,sys\nsrc,out,cab=sys.argv[1:4]\nassert Path(cab).is_file()\nshutil.copyfile(src,out)\n''')
            profile = ToneProfile(
                'real',
                (ToneStage('real_amp_sim', executable=sys.executable, args=(str(script), '{in}', '{out}', '{asset}'), asset_path=cab),),
                controls=ToneControls(amp_gain=0.0, distortion=0.0),
            )
            evidence = execute_tone_chain_with_evidence(source, output, profile)
            self.assertTrue(output.is_file())
            self.assertEqual(evidence.executed_stages, ('controls', 'real_amp_sim'))
            self.assertEqual(evidence.cabinet_ir, str(cab))
            self.assertEqual(evidence.amp_stage_kind, 'real_amp_sim')

    def test_missing_amp_asset_refuses_before_execution(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / 'in.wav'; output = root / 'out.wav'
            write_silence(source)
            profile = ToneProfile(
                'bad',
                (ToneStage('real_amp_sim', executable=sys.executable, args=('noop.py', '{in}', '{out}', '{asset}'), asset_path=root / 'missing.wav'),),
                controls=ToneControls(amp_gain=0.0, distortion=0.0),
            )
            with self.assertRaises(RuntimeError):
                execute_tone_chain_with_evidence(source, output, profile)


if __name__ == '__main__':
    unittest.main()
