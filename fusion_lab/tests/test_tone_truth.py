import unittest
from pathlib import Path
from fusion_lab.production_model import ToneControls, ToneProfile
from fusion_lab.production_render import tone_filter_string, production_manifest

class ToneTruthTests(unittest.TestCase):
    def test_controls_are_bounded(self):
        ToneControls(amp_gain=6.5,distortion=7.0,reverb_mix=0.2,pitch_shift_semitones=-5)
        with self.assertRaises(ValueError): ToneControls(amp_gain=11)
        with self.assertRaises(ValueError): ToneControls(distortion=-1)
        with self.assertRaises(ValueError): ToneControls(reverb_mix=1.1)
        with self.assertRaises(ValueError): ToneControls(pitch_shift_semitones=-25)

    def test_drop_distortion_and_reverb_emit_real_filters(self):
        controls=ToneControls(
            tuning_profile='DROP_B',
            pitch_shift_semitones=-5,
            boost_drive=1.0,
            boost_level=8.0,
            amp_gain=7.0,
            distortion=8.0,
            bass=6.0,
            mid=4.0,
            treble=6.0,
            presence=6.5,
            master=5.0,
            reverb_mix=0.15,
            reverb_decay_s=2.0,
            reverb_predelay_ms=35,
        )
        filt=tone_filter_string(controls)
        self.assertIn('rubberband=pitch=',filt)
        self.assertIn('asoftclip=type=tanh',filt)
        self.assertIn('aecho=',filt)
        self.assertIn('equalizer=f=950',filt)

    def test_manifest_exposes_knobs(self):
        controls=ToneControls(
            tuning_profile='E_STANDARD',
            amp_gain=6.4,
            distortion=6.8,
            reverb_mix=0.035,
            reverb_decay_s=0.55,
            reverb_predelay_ms=18,
        )
        profile=ToneProfile('THRASH_1988',(),controls=controls)
        data=production_manifest(
            host_id='host',renderer_version='test',instruments={},
            tone_profiles={'rhythm_guitar_L':profile},humanization_seed=1,
            structural_signature='sig',stems={},mix_path=None,
        )
        row=data['tone_profiles']['rhythm_guitar_L']['controls']
        self.assertEqual(row['tuning_profile'],'E_STANDARD')
        self.assertEqual(row['amp_gain'],6.4)
        self.assertEqual(row['distortion'],6.8)
        self.assertEqual(row['reverb_mix'],0.035)

if __name__=='__main__': unittest.main()
