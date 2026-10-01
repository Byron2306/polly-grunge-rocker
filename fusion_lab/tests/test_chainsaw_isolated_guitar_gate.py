import unittest

from fusion_lab.music_dna.chainsaw_gate import (
    GateState,
    IsolatedGuitarGate,
    evaluate_isolated_guitar_gate,
)
from fusion_lab.music_dna.model import DecisionState, GenreDecision
from fusion_lab.music_dna.production_truth import ProductionTruthResult


class ChainsawIsolatedGuitarGateTests(unittest.TestCase):
    def test_symbolic_mutate_or_reject_blocks_promotion(self):
        for state in (DecisionState.MUTATE, DecisionState.REJECT):
            gate = evaluate_isolated_guitar_gate(
                GenreDecision(state, 'THRASH_CLASSIC', ('x',), 0.4),
                ProductionTruthResult(True, ()),
                human_review=None,
            )
            self.assertEqual(gate.state, GateState.REFUSE)
            self.assertIn('symbolic_genre_not_allowed', gate.reasons)

    def test_failed_production_truth_blocks_acceptance(self):
        gate = evaluate_isolated_guitar_gate(
            GenreDecision(DecisionState.ALLOW, 'THRASH_CLASSIC', (), 0.0),
            ProductionTruthResult(False, ('missing_cabinet_ir',)),
            human_review=None,
        )
        self.assertEqual(gate.state, GateState.REFUSE)
        self.assertIn('missing_cabinet_ir', gate.reasons)

    def test_valid_machine_gate_waits_for_human_review(self):
        gate = evaluate_isolated_guitar_gate(
            GenreDecision(DecisionState.ALLOW, 'THRASH_CLASSIC', (), 0.0),
            ProductionTruthResult(True, ()),
            human_review=None,
        )
        self.assertEqual(gate.state, GateState.PENDING_HUMAN_REVIEW)

    def test_human_pass_allows_full_render(self):
        gate = evaluate_isolated_guitar_gate(
            GenreDecision(DecisionState.ALLOW, 'THRASH_CLASSIC', (), 0.0),
            ProductionTruthResult(True, ()),
            human_review='PASS',
        )
        self.assertEqual(gate.state, GateState.ALLOW_FULL_RENDER)

    def test_human_refuse_blocks_full_render(self):
        gate = evaluate_isolated_guitar_gate(
            GenreDecision(DecisionState.ALLOW, 'THRASH_CLASSIC', (), 0.0),
            ProductionTruthResult(True, ()),
            human_review='REFUSE',
        )
        self.assertEqual(gate.state, GateState.REFUSE)
        self.assertIn('human_review_refused', gate.reasons)


if __name__ == '__main__':
    unittest.main()
