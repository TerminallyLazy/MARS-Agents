import pytest
from unittest.mock import patch, MagicMock
from src.graph import judge_node, _get_pareto_tracker
from src.state import create_initial_state, OptimizationConfig


@patch("src.dspy_agents.DocumentJudge")
def test_judge_tracks_pareto_candidate(mock_judge_class):
    """Test judge node adds candidate to Pareto tracker."""
    mock_judge = MagicMock()
    mock_judge.return_value = {
        "overall_score": 7.5,
        "feedback": "Good work",
        "criteria_scores": {"accuracy": 8.0, "completeness": 7.0, "clarity": 7.5},
    }
    mock_judge_class.return_value = mock_judge

    state = create_initial_state("Test task for pareto")
    state["current_draft"] = "Some content"
    state["optimization_config"] = OptimizationConfig(
        objectives=["accuracy", "completeness", "clarity"]
    )

    result = judge_node(state)

    assert "scores" in result
    assert result["scores"][0] == 7.5

    task_id = f"task_{hash(state['task'])}"
    tracker = _get_pareto_tracker(state["optimization_config"], task_id)
    assert len(tracker.candidates) >= 1
