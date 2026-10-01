import unittest

from fusion_lab.music_dna.model import (
    ArrangementDNA,
    BassDNA,
    DrumDNA,
    GenreDNA,
    GuitarDNA,
    HarmonyDNA,
    KeysDNA,
    ProductionDNA,
    RangeBand,
    VocalDNA,
    DecisionState,
)
from fusion_lab.music_dna.validator import validate_genre


def component(features):
    return features


def profile():
    return GenreDNA(
        id='TEST',
        tempo=RangeBand(100, 120, 180, 220),
        meters={'4/4': 1.0},
        harmony=HarmonyDNA({'pedal_note_ratio': RangeBand(0.2, 0.4, 0.8, 1.0)}),
        guitar=GuitarDNA({'palm_mute_ratio': RangeBand(0.2, 0.4, 0.8, 1.0)}),
        bass=BassDNA({}),
        drums=DrumDNA({'guitar_kick_coupling': RangeBand(0.2, 0.4, 0.8, 1.0)}),
        vocals=VocalDNA({}),
        keys=KeysDNA({}),
        arrangement=ArrangementDNA({'phrase_end_mutation': RangeBand(0.1, 0.3, 0.8, 1.0)}),
        production=ProductionDNA({}),
    )


class ValidatorTests(unittest.TestCase):
    def test_allow_when_core_features_are_preferred(self):
        decision = validate_genre(
            profile(),
            {
                'tempo_bpm': 160,
                'harmony.pedal_note_ratio': 0.6,
                'guitar.palm_mute_ratio': 0.6,
                'coupling.guitar_kick_coupling': 0.6,
                'arrangement.phrase_end_mutation': 0.5,
            },
        )
        self.assertEqual(decision.state, DecisionState.ALLOW)
        self.assertEqual(decision.reasons, ())

    def test_mutate_reports_specific_out_of_preferred_features(self):
        decision = validate_genre(
            profile(),
            {
                'tempo_bpm': 160,
                'harmony.pedal_note_ratio': 0.25,
                'guitar.palm_mute_ratio': 0.25,
                'coupling.guitar_kick_coupling': 0.25,
                'arrangement.phrase_end_mutation': 0.2,
            },
        )
        self.assertEqual(decision.state, DecisionState.MUTATE)
        self.assertIn('palm_mute_ratio_below_range', decision.reasons)
        self.assertIn('guitar_kick_coupling_below_range', decision.reasons)

    def test_reject_when_feature_violates_outer_band(self):
        decision = validate_genre(
            profile(),
            {'tempo_bpm': 70, 'guitar.palm_mute_ratio': 0.6},
        )
        self.assertEqual(decision.state, DecisionState.REJECT)
        self.assertIn('tempo_bpm_outside_hard_range', decision.reasons)


if __name__ == '__main__':
    unittest.main()
