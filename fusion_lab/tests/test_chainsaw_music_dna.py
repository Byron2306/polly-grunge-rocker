import unittest
from pathlib import Path

from fusion_lab.chainsaw_diplomacy import build_chainsaw_diplomacy
from fusion_lab.music_dna.analysis import analyze_host
from fusion_lab.music_dna.genre_profiles import load_seed_genre_profiles


DATA_ROOT = Path(__file__).resolve().parents[1] / 'data' / 'music_dna' / 'genres'


class ChainsawMusicDNATests(unittest.TestCase):
    def test_chainsaw_analysis_is_deterministic_and_explainable(self):
        profile = load_seed_genre_profiles(DATA_ROOT)['THRASH_CLASSIC']
        host = build_chainsaw_diplomacy()
        a = analyze_host(host, profile)
        b = analyze_host(host, profile)
        self.assertEqual(a.to_dict(), b.to_dict())
        self.assertEqual(a.genre_profile, 'THRASH_CLASSIC')
        self.assertIn('guitar_kick_coupling', a.coupling)
        self.assertIn('total', a.hook_score)
        self.assertIn(a.decision.state.value, {'ALLOW', 'MUTATE', 'REJECT'})

    def test_chainsaw_report_contains_no_opaque_only_score(self):
        profile = load_seed_genre_profiles(DATA_ROOT)['THRASH_CLASSIC']
        report = analyze_host(build_chainsaw_diplomacy(), profile)
        payload = report.to_dict()
        self.assertIn('reasons', payload['decision'])
        self.assertIn('feature_vector', payload)
        self.assertIn('coupling', payload)
        self.assertIn('hook_score', payload)


if __name__ == '__main__':
    unittest.main()
