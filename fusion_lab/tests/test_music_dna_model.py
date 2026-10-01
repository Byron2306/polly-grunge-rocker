import math
import unittest

from fusion_lab.music_dna.distributions import (
    CategoricalDistribution,
    ScalarDistribution,
    blend_categorical,
    blend_range_bands,
)
from fusion_lab.music_dna.model import (
    DecisionState,
    FeatureVector,
    GenreDecision,
    HardConstraint,
    MusicDNAReport,
    RangeBand,
)


class MusicDNAModelTests(unittest.TestCase):
    def test_range_band_rejects_inverted_bounds(self):
        with self.assertRaises(ValueError):
            RangeBand(0.5, 0.4, 0.8, 1.0)
        with self.assertRaises(ValueError):
            RangeBand(0.0, 0.7, 0.6, 1.0)

    def test_probability_features_are_bounded(self):
        with self.assertRaises(ValueError):
            FeatureVector({'palm_mute_ratio': 1.01})
        with self.assertRaises(ValueError):
            FeatureVector({'blast_probability': -0.01})

    def test_decision_state_contract(self):
        self.assertEqual(tuple(state.value for state in DecisionState), ('ALLOW', 'MUTATE', 'REJECT'))

    def test_decision_reasons_are_immutable(self):
        decision = GenreDecision(DecisionState.MUTATE, 'THRASH_CLASSIC', ('x',), 0.25)
        self.assertIsInstance(decision.reasons, tuple)

    def test_report_serializes_deterministically(self):
        report = MusicDNAReport(
            genre_profile='THRASH_CLASSIC',
            feature_vector={'b': 0.2, 'a': 0.1},
            coupling={'guitar_kick': 0.7},
            hook_score={'total': 0.8},
            production_truth={'cabinet': True},
            decision=GenreDecision(DecisionState.ALLOW, 'THRASH_CLASSIC', (), 0.1),
        )
        first = report.to_dict()
        second = report.to_dict()
        self.assertEqual(first, second)
        self.assertEqual(list(first['feature_vector']), ['a', 'b'])
        self.assertEqual(first['decision']['state'], 'ALLOW')

    def test_normalized_distance_is_zero_inside_preferred_band(self):
        band = RangeBand(0.0, 0.4, 0.7, 1.0)
        self.assertEqual(band.normalized_distance(0.55), 0.0)
        self.assertGreater(band.normalized_distance(0.2), 0.0)
        self.assertTrue(math.isfinite(band.normalized_distance(0.2)))

    def test_hard_constraint_is_simple_and_explicit(self):
        constraint = HardConstraint('cabinet_required', True)
        self.assertEqual(constraint.id, 'cabinet_required')
        self.assertTrue(constraint.required)

    def test_scalar_distribution_rejects_empty_and_nonfinite(self):
        with self.assertRaises(ValueError):
            ScalarDistribution(())
        with self.assertRaises(ValueError):
            ScalarDistribution((1.0, float('nan')))

    def test_scalar_distribution_is_deterministic(self):
        dist = ScalarDistribution((4.0, 1.0, 3.0, 2.0))
        self.assertEqual(dist.median(), 2.5)
        self.assertEqual(dist.to_range_band(), dist.to_range_band())

    def test_categorical_distribution_normalizes_deterministically(self):
        with self.assertRaises(ValueError):
            CategoricalDistribution({'a': -1.0})
        dist = CategoricalDistribution({'b': 3.0, 'a': 1.0})
        normalized = dist.normalized()
        self.assertEqual(list(normalized), ['a', 'b'])
        self.assertAlmostEqual(sum(normalized.values()), 1.0)
        self.assertAlmostEqual(normalized['a'], 0.25)

    def test_blend_range_bands_preserves_outer_limits_and_blends_center(self):
        a = RangeBand(0.0, 0.2, 0.4, 1.0)
        b = RangeBand(0.1, 0.6, 0.8, 0.9)
        result = blend_range_bands(((0.75, a), (0.25, b)))
        self.assertEqual(result.minimum, 0.0)
        self.assertEqual(result.maximum, 1.0)
        self.assertAlmostEqual(result.preferred_minimum, 0.3)
        self.assertAlmostEqual(result.preferred_maximum, 0.5)

    def test_blend_categorical_combines_weights(self):
        result = blend_categorical(((0.5, {'a': 1.0}), (0.5, {'b': 1.0})))
        self.assertEqual(result, {'a': 0.5, 'b': 0.5})


if __name__ == '__main__':
    unittest.main()
