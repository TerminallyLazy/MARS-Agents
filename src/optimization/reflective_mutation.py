import dspy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
import uuid

from src.optimization.pareto import Candidate


@dataclass
class FailureTrace:
    task: str
    candidate_content: dict[str, Any]
    expected_outcome: str
    actual_outcome: str
    score: float
    objectives_failed: list[str] = field(default_factory=list)
    error_details: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MutationProposal:
    original_content: dict[str, Any]
    proposed_content: dict[str, Any]
    rationale: str
    target_objectives: list[str]
    expected_improvement: float
    confidence: float = 0.5


class ReflectiveAnalysisSignature(dspy.Signature):
    task: str = dspy.InputField(desc="The task that was attempted")
    candidate_content: str = dspy.InputField(desc="The candidate (prompt/config) that failed")
    expected_outcome: str = dspy.InputField(desc="What was expected")
    actual_outcome: str = dspy.InputField(desc="What actually happened")
    failed_objectives: str = dspy.InputField(desc="Which objectives scored poorly")

    analysis: str = dspy.OutputField(desc="Analysis of what went wrong")
    root_cause: str = dspy.OutputField(desc="The fundamental cause of the failure")
    improvement: str = dspy.OutputField(desc="Specific change to fix this")
    confidence: float = dspy.OutputField(desc="Confidence this improvement will work (0-1)")


class MergeSignature(dspy.Signature):
    candidates: str = dspy.InputField(desc="JSON list of candidates with their scores")
    objectives: str = dspy.InputField(desc="The objectives being optimized")

    merged_content: str = dspy.OutputField(desc="The merged candidate content")
    rationale: str = dspy.OutputField(desc="Why these aspects were combined")


class ReflectiveMutator:
    def __init__(self):
        self._analyzer = dspy.ChainOfThought(ReflectiveAnalysisSignature)
        self._merger = dspy.ChainOfThought(MergeSignature)

    def analyze_and_propose(self, trace: FailureTrace) -> Optional[MutationProposal]:
        try:
            result = self._analyzer(
                task=trace.task,
                candidate_content=str(trace.candidate_content),
                expected_outcome=trace.expected_outcome,
                actual_outcome=trace.actual_outcome,
                failed_objectives=", ".join(trace.objectives_failed),
            )

            proposed = trace.candidate_content.copy()
            if "prompt" in proposed:
                proposed["prompt"] = f"{proposed['prompt']}\n\nImprovement: {result.improvement}"
            else:
                proposed["_improvement"] = result.improvement

            confidence = result.confidence
            if isinstance(confidence, str):
                try:
                    confidence = float(confidence)
                except ValueError:
                    confidence = 0.5

            return MutationProposal(
                original_content=trace.candidate_content,
                proposed_content=proposed,
                rationale=f"{result.analysis}\n\nRoot cause: {result.root_cause}",
                target_objectives=trace.objectives_failed,
                expected_improvement=1.0,
                confidence=min(1.0, max(0.0, confidence)),
            )

        except Exception as e:
            proposed = trace.candidate_content.copy()
            proposed["_mutation"] = f"auto_fix_{datetime.now().timestamp()}"
            return MutationProposal(
                original_content=trace.candidate_content,
                proposed_content=proposed,
                rationale=f"Auto-mutation due to analysis failure: {str(e)}",
                target_objectives=trace.objectives_failed,
                expected_improvement=0.5,
                confidence=0.2,
            )

    def merge_candidates(self, candidates: list[Candidate]) -> Optional[Candidate]:
        if len(candidates) < 2:
            return None

        try:
            candidates_str = "\n".join(
                [
                    f"Candidate {i + 1}: {c.content} | Scores: {c.scores}"
                    for i, c in enumerate(candidates)
                ]
            )

            objectives_str = ", ".join(candidates[0].scores.keys())

            result = self._merger(
                candidates=candidates_str,
                objectives=objectives_str,
            )

            merged_content = {"merged": result.merged_content}

            avg_scores = {}
            for obj in candidates[0].scores.keys():
                avg_scores[obj] = sum(c.scores.get(obj, 0) for c in candidates) / len(candidates)

            return Candidate(
                candidate_id=f"merged_{uuid.uuid4().hex[:8]}",
                content=merged_content,
                scores=avg_scores,
                generation=max(c.generation for c in candidates) + 1,
                parent_id=candidates[0].candidate_id,
                mutation_description=f"Merged from {len(candidates)} candidates: {result.rationale}",
            )

        except Exception:
            return None

    def create_mutation(
        self,
        candidate: Candidate,
        trace: FailureTrace,
    ) -> Candidate:
        proposal = self.analyze_and_propose(trace)

        if proposal is None:
            new_content = candidate.content.copy()
            new_content["_mutated"] = True
            return Candidate(
                candidate_id=f"mut_{uuid.uuid4().hex[:8]}",
                content=new_content,
                scores=candidate.scores.copy(),
                generation=candidate.generation + 1,
                parent_id=candidate.candidate_id,
                mutation_description="Random mutation (analysis failed)",
            )

        return Candidate(
            candidate_id=f"mut_{uuid.uuid4().hex[:8]}",
            content=proposal.proposed_content,
            scores=candidate.scores.copy(),
            generation=candidate.generation + 1,
            parent_id=candidate.candidate_id,
            mutation_description=proposal.rationale[:200],
        )
