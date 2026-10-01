import unittest

from pathlib import Path

from fusion_lab.music_dna.blend import BlendConflictError, blend_genres
from fusion_lab.music_dna.genre_profiles import load_seed_genre_profiles
from fusion_lab.music_dna.model import HardConstraint, ProductionDNA, GenreDNA


DATA_ROOT = Path(__file__).resolve().parents[1] / 'data' / 'music_dna' / 'genres'


class BlendTests(unittest.TestCase):
    def test_weighted_blend_interpolates_feature_ranges(self):
        profiles = load_seed_genre_profiles(DATA_ROOT)
        blend = blend_genres(
            ((0.6, profiles['THRASH_CLASSIC']), (0.25, profiles['BLACK_METAL_CLASSIC']), (0.15, profiles['PROGRESSIVE_METAL_CLASSIC'])),
            blend_id='THRASH_BLACK_PROG',
        )
        self.assertEqual(blend.id, 'THRASH_BLACK_PROG')
        self.assertGreater(blend.guitar.features['palm_mute_ratio'].preferred_minimum, profiles['BLACK_METAL_CLASSIC'].guitar.features['palm_mute_ratio'].preferred_minimum)
        self.assertGreater(blend.guitar.features['tremolo_ratio'].preferred_maximum, profiles['THRASH_CLASSIC'].guitar.features['tremolo_ratio'].preferred_maximum)

    def test_conflicting_hard_constraints_raise_explicit_error(self):
        profiles = load_seed_genre_profiles(DATA_ROOT)
        base = profiles['THRASH_CLASSIC']
        conflict = GenreDNA(
            id='CONFLICT', tempo=base.tempo, meters=base.meters,
            harmony=base.harmony, guitar=base.guitar, bass=base.bass, drums=base.drums,
            vocals=base.vocals, keys=base.keys, arrangement=base.arrangement,
            production=ProductionDNA(base.production.features, (HardConstraint('cabinet_required', False),)),
        )
        with self.assertRaises(BlendConflictError):
            blend_genres(((0.5, base), (0.5, conflict)), blend_id='BAD')


if __name__ == '__main__':
    unittest.main()
