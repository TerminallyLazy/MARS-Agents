import pytest
from src.optimization.pareto import ParetoState, Candidate, ParetoTracker


def test_candidate_creation():
    """Test Candidate can track multi-objective scores."""
    candidate = Candidate(
        candidate_id="cand_001",
        content={"prompt": "Be helpful and accurate"},
        scores={"accuracy": 8.5, "efficiency": 7.0, "clarity": 9.0},
    )
    assert candidate.candidate_id == "cand_001"
    assert candidate.scores["accuracy"] == 8.5
    assert candidate.overall_score == pytest.approx((8.5 + 7.0 + 9.0) / 3, rel=0.01)


def test_candidate_dominates():
    """Test Pareto dominance check."""
    c1 = Candidate("c1", {}, {"a": 8.0, "b": 7.0})
    c2 = Candidate("c2", {}, {"a": 7.0, "b": 6.0})  # Dominated by c1
    c3 = Candidate("c3", {}, {"a": 9.0, "b": 6.0})  # Not dominated (better a, worse b)

    assert c1.dominates(c2) is True
    assert c1.dominates(c3) is False
    assert c3.dominates(c1) is False


def test_pareto_tracker_add_candidate():
    """Test adding candidates to tracker."""
    tracker = ParetoTracker(objectives=["accuracy", "efficiency"])

    tracker.add_candidate(
        content={"prompt": "v1"},
        scores={"accuracy": 7.0, "efficiency": 8.0},
    )

    assert len(tracker.candidates) == 1
    assert len(tracker.get_pareto_front()) == 1


def test_pareto_front_computation():
    """Test Pareto front identifies non-dominated solutions."""
    tracker = ParetoTracker(objectives=["accuracy", "efficiency"])

    # Add candidates
    tracker.add_candidate({"v": 1}, {"accuracy": 8.0, "efficiency": 6.0})  # Front
    tracker.add_candidate({"v": 2}, {"accuracy": 6.0, "efficiency": 8.0})  # Front
    tracker.add_candidate({"v": 3}, {"accuracy": 7.0, "efficiency": 7.0})  # Front (balanced)
    tracker.add_candidate({"v": 4}, {"accuracy": 5.0, "efficiency": 5.0})  # Dominated

    front = tracker.get_pareto_front()

    assert len(front) == 3  # v1, v2, v3
    front_ids = {c.candidate_id for c in front}
    dominated_id = tracker.candidates[-1].candidate_id
    assert dominated_id not in front_ids


def test_epsilon_greedy_selection():
    """Test epsilon-greedy occasionally explores non-optimal."""
    tracker = ParetoTracker(objectives=["accuracy"])

    tracker.add_candidate({"v": 1}, {"accuracy": 9.0})  # Best
    tracker.add_candidate({"v": 2}, {"accuracy": 5.0})  # Worst

    # With epsilon=0.5, should sometimes select non-best
    selections = [tracker.select_epsilon_greedy(epsilon=0.5) for _ in range(100)]

    # Both candidates should appear
    ids = {c.candidate_id for c in selections}
    assert len(ids) == 2


def test_pareto_state_serialization():
    """Test ParetoState can be serialized."""
    tracker = ParetoTracker(objectives=["a", "b"])
    tracker.add_candidate({"x": 1}, {"a": 7.0, "b": 8.0})

    state = tracker.get_state()

    assert "candidates" in state
    assert "pareto_front" in state
    assert "objectives" in state
