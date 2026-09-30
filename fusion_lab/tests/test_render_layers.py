import tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from fusion_lab.render import RenderConfig, render_named_stems, mix_named_stems

class RenderLayerTests(unittest.TestCase):
    def test_named_stems_preserve_layer_keys_and_stable_names(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); sf=root/'x.sf2'; sf.write_bytes(b'x')
            midis={'host_DRUMS':root/'host_drums.mid','performer_prog_synth':root/'performer_prog_synth.mid'}
            for p in midis.values(): p.write_bytes(b'MThd')
            def fake_render(midi,wav,config): Path(wav).write_bytes(b'RIFF')
            with patch('fusion_lab.render.render_midi',side_effect=fake_render):
                out=render_named_stems(midis,root/'wav',RenderConfig(sf))
            self.assertEqual(set(out),set(midis))
            self.assertEqual(out['host_DRUMS'].name,'host_DRUMS.wav')
            self.assertEqual(out['performer_prog_synth'].name,'performer_prog_synth.wav')
            self.assertTrue(all(p.is_file() for p in out.values()))

    def test_mix_named_stems_refuses_missing_files(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with self.assertRaisesRegex(RuntimeError,'FUSION_RENDER_MISSING_STEM'):
                mix_named_stems({'x':root/'missing.wav'},root/'mix.wav')

if __name__=='__main__': unittest.main()
