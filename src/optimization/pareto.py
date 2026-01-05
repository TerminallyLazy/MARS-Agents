from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import random
import uuid


@dataclass
class Candidate:
    candidate_id: str
    content: dict[str, Any]
    scores: dict[str, float]

    generation: int = 0
    parent_id: Optional[str] = None
    mutation_description: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def overall_score(self) -> float:
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)

    def dominates(self, other: "Candidate") -> bool:
        dominated_in_all = True
        strictly_better_in_one = False

        for obj, score in self.scores.items():
            other_score = other.scores.get(obj, 0)
            if score < other_score:
                dominated_in_all = False
                break
            if score > other_score:
                strictly_better_in_one = True

        return dominated_in_all and strictly_better_in_one


@dataclass
class ParetoState:
    candidates: list[dict]
    pareto_front: list[str]
    objectives: list[str]
    generation: int
    best_overall_id: Optional[str]


class ParetoTracker:
    def __init__(self, objectives: list[str]):
        self.objectives = objectives
        self.candidates: list[Candidate] = []
        self._generation = 0

    def add_candidate(
        self,
        content: dict[str, Any],
        scores: dict[str, float],
        parent_id: Optional[str] = None,
        mutation_description: str = "",
    ) -> Candidate:
        candidate = Candidate(
            candidate_id=f"cand_{uuid.uuid4().hex[:8]}",
            content=content,
            scores={obj: scores.get(obj, 0.0) for obj in self.objectives},
            generation=self._generation,
            parent_id=parent_id,
            mutation_description=mutation_description,
        )
        self.candidates.append(candidate)
        return candidate

    def get_pareto_front(self) -> list[Candidate]:
        if not self.candidates:
            return []

        front = []
        for candidate in self.candidates:
            is_dominated = False
            for other in self.candidates:
                if other.candidate_id == candidate.candidate_id:
                    continue
                if other.dominates(candidate):
                    is_dominated = True
                    break

            if not is_dominated:
                front.append(candidate)

        return front

    def select_pareto(self) -> Optional[Candidate]:
        front = self.get_pareto_front()
        return random.choice(front) if front else None

    def select_epsilon_greedy(self, epsilon: float = 0.1) -> Optional[Candidate]:
        if not self.candidates:
            return None

        if random.random() < epsilon:
            return random.choice(self.candidates)
        else:
            return self.select_pareto()

    def select_best_overall(self) -> Optional[Candidate]:
        if not self.candidates:
            return None
        return max(self.candidates, key=lambda c: c.overall_score)

    def advance_generation(self) -> None:
        self._generation += 1

    def get_dominated_candidates(self) -> list[Candidate]:
        front_ids = {c.candidate_id for c in self.get_pareto_front()}
        return [c for c in self.candidates if c.candidate_id not in front_ids]

    def prune_dominated(self, keep_n: int = 10) -> int:
        front = self.get_pareto_front()
        front_ids = {c.candidate_id for c in front}

        dominated = [c for c in self.candidates if c.candidate_id not in front_ids]
        dominated.sort(key=lambda c: c.created_at, reverse=True)

        to_keep_ids = front_ids | {c.candidate_id for c in dominated[:keep_n]}

        original_count = len(self.candidates)
        self.candidates = [c for c in self.candidates if c.candidate_id in to_keep_ids]

        return original_count - len(self.candidates)

    def get_state(self) -> dict:
        front = self.get_pareto_front()
        best = self.select_best_overall()

        return {
            "candidates": [
                {
                    "id": c.candidate_id,
                    "scores": c.scores,
                    "overall": c.overall_score,
                    "generation": c.generation,
                }
                for c in self.candidates
            ],
            "pareto_front": [c.candidate_id for c in front],
            "objectives": self.objectives,
            "generation": self._generation,
            "best_overall_id": best.candidate_id if best else None,
            "total_candidates": len(self.candidates),
            "front_size": len(front),
        }
