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

    def test_chainsaw_enters_preferred_classic_thrash_envelope(self):
        profile = load_seed_genre_profiles(DATA_ROOT)['THRASH_CLASSIC']
        report = analyze_host(build_chainsaw_diplomacy(), profile)
        values = report.feature_vector
        self.assertEqual(report.decision.state.value, 'ALLOW', report.decision.reasons)
        self.assertGreaterEqual(values['guitar.downpick_ratio'], 0.55)
        self.assertGreaterEqual(values['harmony.chromaticity'], 0.30)
        self.assertGreaterEqual(values['harmony.tritone_rate'], 0.08)
        self.assertGreaterEqual(values['drums.double_kick_density'], 0.12)
        self.assertGreaterEqual(values['bass.fill_probability'], 0.08)
        self.assertLessEqual(report.coupling['bass_guitar_lock_rate'], 0.90)


if __name__ == '__main__':
    unittest.main()
