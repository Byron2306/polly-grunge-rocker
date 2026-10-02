import json
import tempfile
import unittest
from pathlib import Path

from fusion_lab.music_dna.genre_profiles import load_genre_profile, load_seed_genre_profiles
from fusion_lab.music_dna.validator import validate_genre


DATA_ROOT = Path(__file__).resolve().parents[1] / 'data' / 'music_dna' / 'genres'


def _legacy_profile():
    empty = {'features': {}}
    return {
        'schema': 'polly.music-dna.genre-profile.v1',
        'id': 'LEGACY_FIXTURE',
        'tempo': [80, 100, 180, 220],
        'meters': {'4/4': 1.0},
        'harmony': empty,
        'guitar': empty,
        'bass': empty,
        'drums': empty,
        'vocals': empty,
        'keys': empty,
        'arrangement': empty,
        'production': empty,
    }


class GenreProfileRiffStructureTests(unittest.TestCase):
    def test_profile_without_riff_structure_loads_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'legacy.json'
            path.write_text(json.dumps(_legacy_profile()))
            profile = load_genre_profile(path)
        self.assertIsNone(profile.riff_structure)
        self.assertEqual(profile.id, 'LEGACY_FIXTURE')

    def test_thrash_profile_loads_riff_structure_ranges(self):
        profile = load_seed_genre_profiles(DATA_ROOT)['THRASH_CLASSIC']
        self.assertIsNotNone(profile.riff_structure)
        self.assertIn('riff_family_count', profile.riff_structure.features)
        self.assertGreaterEqual(profile.riff_structure.features['riff_family_count'].preferred_minimum, 5)
        self.assertLessEqual(profile.riff_structure.features['longest_same_family_run_bars'].preferred_maximum, 4)

    def test_black_metal_profile_allows_long_trance_runs(self):
        profiles = load_seed_genre_profiles(DATA_ROOT)
        black = profiles['BLACK_METAL_CLASSIC']
        thrash = profiles['THRASH_CLASSIC']
        structure = {
            'riff_family_count': 2,
            'riff_family_recurrence': 0.85,
            'longest_same_family_run_bars': 12,
            'section_riff_contrast': 0.08,
            'transition_density': 0.02,
            'gesture_diversity': 1,
            'gesture_metadata_present': True,
        }
        black_decision = validate_genre(black, {}, riff_structure=structure)
        thrash_decision = validate_genre(thrash, {}, riff_structure=structure)
        self.assertNotEqual(black_decision.state.value, 'REJECT')
        self.assertIn(thrash_decision.state.value, {'MUTATE', 'REJECT'})
        self.assertTrue(any('riff_family' in reason or 'longest_same_family' in reason for reason in thrash_decision.reasons))

    def test_missing_legacy_gesture_metadata_adds_no_gesture_reason(self):
        thrash = load_seed_genre_profiles(DATA_ROOT)['THRASH_CLASSIC']
        structure = {
            'riff_family_count': 5,
            'riff_family_recurrence': 0.30,
            'longest_same_family_run_bars': 4,
            'section_riff_contrast': 0.45,
            'transition_density': 0.0,
            'gesture_diversity': 0,
            'gesture_metadata_present': False,
        }
        decision = validate_genre(thrash, {}, riff_structure=structure)
        self.assertFalse(any('gesture_diversity' in reason for reason in decision.reasons))
        self.assertFalse(any('transition_density' in reason for reason in decision.reasons))


if __name__ == '__main__':
    unittest.main()
