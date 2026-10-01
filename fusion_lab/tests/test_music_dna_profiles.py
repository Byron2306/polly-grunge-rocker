import collections
import json
import tempfile
import unittest
from pathlib import Path

from fusion_lab.music_dna.corpus import load_corpus
from fusion_lab.music_dna.genre_profiles import load_genre_profile, load_seed_genre_profiles


DATA_ROOT = Path(__file__).resolve().parents[1] / 'data' / 'music_dna'


class MusicDNAProfileTests(unittest.TestCase):
    def test_seven_seed_profiles_load(self):
        profiles = load_seed_genre_profiles(DATA_ROOT / 'genres')
        self.assertEqual(
            set(profiles),
            {
                'THRASH_CLASSIC',
                'BLACK_METAL_CLASSIC',
                'DEATH_METAL_CLASSIC',
                'DOOM_METAL_CLASSIC',
                'PUNK_CLASSIC',
                'GLAM_METAL_CLASSIC',
                'PROGRESSIVE_METAL_CLASSIC',
            },
        )

    def test_thrashy_ranges_differ_from_black_death_and_doom(self):
        profiles = load_seed_genre_profiles(DATA_ROOT / 'genres')
        thrash = profiles['THRASH_CLASSIC']
        black = profiles['BLACK_METAL_CLASSIC']
        death = profiles['DEATH_METAL_CLASSIC']
        doom = profiles['DOOM_METAL_CLASSIC']
        self.assertLessEqual(thrash.tempo.minimum, 175.0)
        self.assertGreaterEqual(thrash.tempo.maximum, 225.0)
        self.assertLess(thrash.drums.features['blast_probability'].preferred_maximum, death.drums.features['blast_probability'].preferred_minimum)
        self.assertLess(black.guitar.features['palm_mute_ratio'].preferred_maximum, thrash.guitar.features['palm_mute_ratio'].preferred_minimum)
        self.assertLess(doom.guitar.features['attack_density'].preferred_maximum, thrash.guitar.features['attack_density'].preferred_minimum)

    def test_thrashy_staccato_can_be_valid_without_sustain(self):
        thrash = load_seed_genre_profiles(DATA_ROOT / 'genres')['THRASH_CLASSIC']
        self.assertEqual(thrash.guitar.features['sustain_ratio'].minimum, 0.0)

    def test_thrashy_pedal_riff_does_not_require_root_motion_fifths(self):
        thrash = load_seed_genre_profiles(DATA_ROOT / 'genres')['THRASH_CLASSIC']
        self.assertEqual(thrash.harmony.features['perfect_fifth_rate'].preferred_minimum, 0.0)

    def test_malformed_profile_fails_loudly(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'bad.json'
            path.write_text(json.dumps({'id': 'BAD', 'tempo': [1, 2, 3, 4]}))
            with self.assertRaises(ValueError):
                load_genre_profile(path)

    def test_corpus_has_five_exemplars_per_genre_without_notation_payloads(self):
        observations = load_corpus(DATA_ROOT / 'corpus.json')
        self.assertEqual(len(observations), 35)
        counts = collections.Counter(obs.genre for obs in observations)
        self.assertEqual(set(counts.values()), {5})
        for obs in observations:
            self.assertTrue(obs.provenance)
            self.assertNotIn('tab', obs.features)
            self.assertNotIn('score', obs.features)
            self.assertNotIn('notes', obs.features)


if __name__ == '__main__':
    unittest.main()
