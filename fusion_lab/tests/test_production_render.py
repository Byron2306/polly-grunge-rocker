import tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from fusion_lab.production_model import *
from fusion_lab.production_render import *
class ProductionRenderTests(unittest.TestCase):
    def test_missing_sampler_and_sfz_fail_closed(self):
        with patch('fusion_lab.production_render.shutil.which',return_value=None):
            with self.assertRaisesRegex(RuntimeError,'PRODUCTION_MISSING_SFIZZ_RENDER'): check_production_dependencies(ProductionConfig(48000))
        art=ArticulationMap('SUSTAIN')
        inst=InstrumentProfile('g','guitar',Path('/nope.sfz'),{'SUSTAIN':art},'src')
        with patch('fusion_lab.production_render.shutil.which',return_value='/x'):
            with self.assertRaisesRegex(RuntimeError,'PRODUCTION_MISSING_SFZ'): check_production_dependencies(ProductionConfig(48000),{'g':inst})
    def test_render_command_is_offline_and_has_no_fluidsynth(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); sfz=root/'x.sfz'; sfz.write_text('<region>'); midi=root/'x.mid'; midi.write_bytes(b'x')
            with patch('fusion_lab.production_render.shutil.which',return_value='/usr/bin/sfizz_render'),patch('fusion_lab.production_render.subprocess.run') as run:
                render_sfz(midi,sfz,root/'o.wav',sample_rate=48000)
                cmd=run.call_args.args[0]
                self.assertIn('--use-eot',cmd); self.assertIn('48000',cmd); self.assertNotIn('fluidsynth',' '.join(cmd).lower())
    def test_manifest_stable_order(self):
        art=ArticulationMap('SUSTAIN'); inst=InstrumentProfile('g','guitar',Path('/tmp/g.sfz'),{'SUSTAIN':art},'src')
        m1=production_manifest(host_id='h',renderer_version='1',instruments={'g':inst},tone_profiles={},humanization_seed=1,structural_signature='abc',stems={})
        m2=production_manifest(host_id='h',renderer_version='1',instruments={'g':inst},tone_profiles={},humanization_seed=1,structural_signature='abc',stems={})
        self.assertEqual(m1,m2)
if __name__=='__main__': unittest.main()
