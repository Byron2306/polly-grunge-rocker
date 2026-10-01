from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .model import DecisionState, GenreDecision
from .production_truth import ProductionTruthResult


class GateState(str, Enum):
    REFUSE = 'REFUSE'
    PENDING_HUMAN_REVIEW = 'PENDING_HUMAN_REVIEW'
    ALLOW_FULL_RENDER = 'ALLOW_FULL_RENDER'


@dataclass(frozen=True, slots=True)
class IsolatedGuitarGate:
    state: GateState
    reasons: tuple[str, ...]

    def to_dict(self) -> dict:
        return {'state': self.state.value, 'reasons': list(self.reasons)}


def evaluate_isolated_guitar_gate(
    genre_decision: GenreDecision,
    production_truth: ProductionTruthResult,
    *,
    human_review: str | None,
) -> IsolatedGuitarGate:
    reasons: list[str] = []

    if genre_decision.state is not DecisionState.ALLOW:
        reasons.append('symbolic_genre_not_allowed')
        reasons.extend(genre_decision.reasons)

    if not production_truth.ok:
        reasons.extend(production_truth.reasons)

    if reasons:
        return IsolatedGuitarGate(GateState.REFUSE, tuple(sorted(set(reasons))))

    if human_review is None or human_review == 'PENDING':
        return IsolatedGuitarGate(GateState.PENDING_HUMAN_REVIEW, ())
    if human_review == 'PASS':
        return IsolatedGuitarGate(GateState.ALLOW_FULL_RENDER, ())
    if human_review in {'REFUSE', 'ADJUST'}:
        return IsolatedGuitarGate(GateState.REFUSE, ('human_review_refused',))
    raise ValueError('human_review must be PASS, ADJUST, REFUSE, PENDING, or None')
