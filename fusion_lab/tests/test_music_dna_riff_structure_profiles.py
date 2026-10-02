import unittest
from pathlib import Path

from fusion_lab.music_dna.genre_profiles import load_seed_genre_profiles
from fusion_lab.music_dna.model import DecisionState
from fusion_lab.music_dna.validator import validate_genre


DATA_ROOT = Path(__file__).resolve().parents[1] / 'data' / 'music_dna' / 'genres'


class RiffStructureProfileTests(unittest.TestCase):
    def setUp(self):
        self.profiles = load_seed_genre_profiles(DATA_ROOT)

    def test_seed_profiles_opt_in_to_genre_specific_structure(self):
        thrash = self.profiles['THRASH_CLASSIC']
        black = self.profiles['BLACK_METAL_CLASSIC']
        self.assertIsNotNone(thrash.riff_structure)
        self.assertIsNotNone(black.riff_structure)
        self.assertLess(
            thrash.riff_structure.features['longest_same_family_run_bars'].preferred_maximum,
            black.riff_structure.features['longest_same_family_run_bars'].preferred_maximum,
        )

    def test_long_trance_run_is_acceptable_for_black_metal_but_not_preferred_thrash(self):
        structure = {
            'gesture_metadata_present': True,
            'riff_family_count': 3.0,
            'riff_family_recurrence': 0.55,
            'longest_same_family_run_bars': 12.0,
            'section_riff_contrast': 0.35,
            'transition_density': 0.08,
            'gesture_diversity': 2.0,
        }
        black = validate_genre(
            self.profiles['BLACK_METAL_CLASSIC'],
            {},
            riff_structure=structure,
        )
        thrash = validate_genre(
            self.profiles['THRASH_CLASSIC'],
            {},
            riff_structure=structure,
        )
        self.assertEqual(black.state, DecisionState.ALLOW, black.reasons)
        self.assertNotEqual(thrash.state, DecisionState.ALLOW)
        self.assertIn('longest_same_family_run_bars_outside_hard_range', thrash.reasons)


if __name__ == '__main__':
    unittest.main()
