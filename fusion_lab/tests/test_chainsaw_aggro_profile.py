import unittest
from pathlib import Path

from fusion_lab.production_render import load_tone_profiles


ROOT = Path(__file__).resolve().parents[1]
TONES = ROOT / 'data' / 'production' / 'tone-profiles-v5.json'


class ChainsawAggroProfileTests(unittest.TestCase):
    def test_bass_has_dedicated_growl_stage(self):
        profiles = load_tone_profiles(TONES)
        stage = profiles['bass'].stages[0]
        self.assertEqual(stage.kind, 'bass_aggro_processor')
        self.assertIn('scripts/run_thr_bass.py', stage.args)

    def test_drums_have_dedicated_attack_stage_and_short_room(self):
        profiles = load_tone_profiles(TONES)
        drums = profiles['drums']
        stage = drums.stages[0]
        self.assertEqual(stage.kind, 'drum_aggro_processor')
        self.assertIn('scripts/run_thr_drums.py', stage.args)
        self.assertLessEqual(drums.controls.reverb_mix, 0.02)
        self.assertLessEqual(drums.controls.reverb_decay_s, 0.25)

    def test_guitars_remain_real_amp_with_cabinet(self):
        profiles = load_tone_profiles(TONES)
        for layer in ('rhythm_guitar_L', 'rhythm_guitar_R', 'lead_guitar'):
            self.assertEqual(profiles[layer].stages[0].kind, 'plugin_amp_with_cabinet')
            self.assertIn('scripts/run_caps_thr_amp.py', profiles[layer].stages[0].args)


if __name__ == '__main__':
    unittest.main()
