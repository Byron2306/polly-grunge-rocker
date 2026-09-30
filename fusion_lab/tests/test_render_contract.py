import tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from fusion_lab.render import RenderConfig, check_render_dependencies, render_midi, render_stems, mix_stems
from fusion_lab.model import CANONICAL_ROLES

class RenderContractTests(unittest.TestCase):
    def test_missing_fluidsynth_is_actionable(self):
        with tempfile.TemporaryDirectory() as d:
            sf=Path(d)/'x.sf2'; sf.write_bytes(b'x')
            with patch('fusion_lab.render.shutil.which',return_value=None):
                with self.assertRaisesRegex(RuntimeError,'FUSION_RENDER_MISSING_FLUIDSYNTH'):
                    check_render_dependencies(RenderConfig(sf))

    def test_missing_soundfont_is_actionable(self):
        with patch('fusion_lab.render.shutil.which',return_value='/usr/bin/fluidsynth'):
            with self.assertRaisesRegex(RuntimeError,'FUSION_RENDER_MISSING_SOUNDFONT'):
                check_render_dependencies(RenderConfig(Path('/no/such.sf2')))

    def test_render_command_is_headless_and_pins_rate_gain(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); sf=root/'x.sf2'; sf.write_bytes(b'x'); midi=root/'x.mid'; midi.write_bytes(b'MThd'); wav=root/'x.wav'
            with patch('fusion_lab.render.shutil.which',return_value='/usr/bin/fluidsynth'), patch('fusion_lab.render.subprocess.run') as run:
                render_midi(midi,wav,RenderConfig(sf,48000,0.7))
                cmd=run.call_args.args[0]
                self.assertEqual(cmd[0],'/usr/bin/fluidsynth')
                self.assertIn('-ni',cmd)
                self.assertIn('48000',cmd)
                self.assertIn('0.7',cmd)

    def test_render_stems_uses_stable_filenames(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); sf=root/'x.sf2'; sf.write_bytes(b'x'); out=root/'wav'
            mids={r:root/f'{r}.mid' for r in CANONICAL_ROLES}
            for p in mids.values(): p.write_bytes(b'MThd')
            with patch('fusion_lab.render.shutil.which',return_value='/usr/bin/fluidsynth'), patch('fusion_lab.render.subprocess.run'):
                stems=render_stems(mids,out,RenderConfig(sf))
            self.assertEqual([stems[r].name for r in CANONICAL_ROLES],['drums.wav','bass.wav','rhythm_guitar.wav','lead_keys.wav','vocals.wav'])

    def test_mix_refuses_missing_canonical_stem(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); stems={r:root/f'{r}.wav' for r in CANONICAL_ROLES if r!='VOCALS'}
            for p in stems.values(): p.write_bytes(b'x')
            with self.assertRaisesRegex(RuntimeError,'FUSION_RENDER_MISSING_STEM'):
                mix_stems(stems,root/'mix.wav')

if __name__=='__main__': unittest.main()
