import pytest
from unittest.mock import MagicMock, patch
from src.optimization.reflective_mutation import (
    ReflectiveMutator,
    FailureTrace,
    MutationProposal,
)
from src.optimization.pareto import Candidate


def test_failure_trace_creation():
    """Test FailureTrace captures failure context."""
    trace = FailureTrace(
        task="Generate API documentation",
        candidate_content={"prompt": "Document this API"},
        expected_outcome="Complete API docs with examples",
        actual_outcome="Missing authentication section",
        score=5.0,
        objectives_failed=["completeness", "accuracy"],
    )
    assert trace.score == 5.0
    assert "completeness" in trace.objectives_failed


def test_mutation_proposal_creation():
    """Test MutationProposal structure."""
    proposal = MutationProposal(
        original_content={"prompt": "Be helpful"},
        proposed_content={"prompt": "Be helpful and thorough, always include examples"},
        rationale="Original lacked specificity, causing incomplete outputs",
        target_objectives=["completeness"],
        expected_improvement=1.5,
    )
    assert "thorough" in proposal.proposed_content["prompt"]


@patch("src.optimization.reflective_mutation.dspy")
def test_reflective_mutator_analyze_failure(mock_dspy):
    """Test failure analysis generates mutation proposal."""
    mock_result = MagicMock()
    mock_result.analysis = "Prompt lacks specificity about required sections"
    mock_result.root_cause = "Missing structural guidance"
    mock_result.improvement = "Add explicit section requirements"
    mock_result.confidence = 0.8
    mock_dspy.ChainOfThought.return_value.return_value = mock_result

    mutator = ReflectiveMutator()

    trace = FailureTrace(
        task="Generate report",
        candidate_content={"prompt": "Write a report"},
        expected_outcome="Structured report",
        actual_outcome="Unstructured text",
        score=4.0,
        objectives_failed=["structure"],
    )

    proposal = mutator.analyze_and_propose(trace)

    assert proposal is not None
    assert proposal.rationale != ""


@patch("src.optimization.reflective_mutation.dspy")
def test_reflective_mutator_merge_candidates(mock_dspy):
    """Test merging high-performing candidates."""
    mock_result = MagicMock()
    mock_result.merged_content = "Combined best aspects: thorough and efficient"
    mock_result.rationale = "Merged thoroughness from C1 with efficiency from C2"
    mock_dspy.ChainOfThought.return_value.return_value = mock_result

    mutator = ReflectiveMutator()

    c1 = Candidate("c1", {"prompt": "Be thorough"}, {"accuracy": 9.0, "efficiency": 6.0})
    c2 = Candidate("c2", {"prompt": "Be efficient"}, {"accuracy": 6.0, "efficiency": 9.0})

    merged = mutator.merge_candidates([c1, c2])

    assert merged is not None
    assert "merged" in merged.mutation_description.lower() or merged.parent_id is not None
