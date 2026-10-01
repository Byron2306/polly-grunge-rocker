import unittest

from fusion_lab.music_dna.model import HardConstraint, ProductionDNA
from fusion_lab.music_dna.production_truth import ProductionEvidence, validate_production_truth


class ProductionTruthTests(unittest.TestCase):
    def setUp(self):
        self.profile = ProductionDNA(
            features={},
            hard_constraints=(
                HardConstraint('amp_distortion_required', True),
                HardConstraint('cabinet_required', True),
                HardConstraint('distinct_double_tracks', True),
                HardConstraint('distinct_palm_mute_envelope', True),
            ),
        )

    def test_softclip_only_does_not_count_as_real_amp(self):
        result = validate_production_truth(
            self.profile,
            ProductionEvidence(
                amp_stage_kind='generic_softclip',
                cabinet_ir=None,
                left_performance_id='L1',
                right_performance_id='R1',
                palm_mute_signature='mute',
                sustain_signature='sus',
            ),
        )
        self.assertFalse(result.ok)
        self.assertIn('missing_verified_amp_distortion', result.reasons)

    def test_missing_cabinet_is_refused(self):
        result = validate_production_truth(
            self.profile,
            ProductionEvidence('real_amp_sim', None, 'L1', 'R1', 'mute', 'sus'),
        )
        self.assertFalse(result.ok)
        self.assertIn('missing_cabinet_ir', result.reasons)

    def test_identical_double_track_ids_are_refused(self):
        result = validate_production_truth(
            self.profile,
            ProductionEvidence('real_amp_sim', '/tmp/cab.wav', 'same', 'same', 'mute', 'sus'),
        )
        self.assertIn('double_tracks_not_distinct', result.reasons)

    def test_identical_mute_and_sustain_signatures_are_refused(self):
        result = validate_production_truth(
            self.profile,
            ProductionEvidence('real_amp_sim', '/tmp/cab.wav', 'L', 'R', 'same', 'same'),
        )
        self.assertIn('palm_mute_not_distinct_from_sustain', result.reasons)

    def test_truthful_chain_passes(self):
        result = validate_production_truth(
            self.profile,
            ProductionEvidence('real_amp_sim', '/tmp/cab.wav', 'L', 'R', 'mute', 'sus'),
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.reasons, ())


if __name__ == '__main__':
    unittest.main()
