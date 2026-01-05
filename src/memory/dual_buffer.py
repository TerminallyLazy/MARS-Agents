"""Dual-buffer memory provider inspired by MemEvolve's LightweightMemoryProvider.

Architecture:
1. Short-term Memory: In-memory list of key facts for current task (evicts oldest)
2. Long-term Memory (Strategic): High-level patterns and approaches (BEGIN phase)
3. Long-term Memory (Operational): Specific techniques and fixes (IN phase)

Reference: EvolveLab/providers/lightweight_memory_provider.py
"""

from datetime import datetime

from src.memory.base import (
    MemoryRequest,
    MemoryResponse,
    TrajectoryData,
    MemoryStatus,
)


class DualBufferMemory:
    """Implements the dual-buffer pattern from MemEvolve.

    Frequency Control (from LightweightMemoryProvider):
    - Short-term: Retrieved every N steps during IN phase
    - Long-term strategic: Only at BEGIN phase
    - Long-term operational: During IN phase when relevant
    """

    def __init__(
        self,
        max_short_term: int = 10,
        max_long_term_strategic: int = 30,
        max_long_term_operational: int = 30,
        retrieval_frequency: int = 3,
    ):
        self.max_short_term = max_short_term
        self.max_long_term_strategic = max_long_term_strategic
        self.max_long_term_operational = max_long_term_operational
        self.retrieval_frequency = retrieval_frequency

        self._short_term: list[str] = []
        self._long_term_strategic: list[dict] = []
        self._long_term_operational: list[dict] = []
        self._initialized = False

    def initialize(self) -> bool:
        self._short_term = []
        self._long_term_strategic = []
        self._long_term_operational = []
        self._initialized = True
        return True

    def provide_memory(self, request: MemoryRequest) -> MemoryResponse:
        if not self._initialized:
            return MemoryResponse(
                guidance="Memory not initialized",
                confidence=0.0,
            )

        if request.status == MemoryStatus.BEGIN:
            return self._provide_strategic(request)
        elif request.status == MemoryStatus.IN:
            return self._provide_operational(request)
        else:
            return self._provide_summary(request)

    def _provide_strategic(self, request: MemoryRequest) -> MemoryResponse:
        relevant = self._search_memories(
            request.query,
            self._long_term_strategic,
            top_k=3,
        )

        if not relevant:
            return MemoryResponse(
                guidance="No prior strategic knowledge. Proceed with careful exploration.",
                confidence=0.3,
                source_type="long_term",
            )

        guidance_parts = [m["learning"] for m in relevant]
        return MemoryResponse(
            guidance="\n".join(f"- {g}" for g in guidance_parts),
            relevant_memories=[m["task"] for m in relevant],
            confidence=min(0.9, 0.5 + len(relevant) * 0.15),
            source_type="long_term",
        )

    def _provide_operational(self, request: MemoryRequest) -> MemoryResponse:
        step_num = request.additional_params.get("step_number", 1)

        memories = []
        source = "hybrid"

        if self._short_term:
            memories.extend(self._short_term[-5:])
            source = "short_term"

        if step_num % self.retrieval_frequency == 0:
            relevant_ops = self._search_memories(
                request.query,
                self._long_term_operational,
                top_k=2,
            )
            if relevant_ops:
                memories.extend([m["learning"] for m in relevant_ops])
                source = "hybrid"

        if not memories:
            return MemoryResponse(
                guidance="No relevant operational memories. Continue with current approach.",
                confidence=0.4,
                source_type=source,
            )

        return MemoryResponse(
            guidance="\n".join(f"- {m}" for m in memories),
            relevant_memories=memories,
            confidence=min(0.85, 0.4 + len(memories) * 0.1),
            source_type=source,
        )

    def _provide_summary(self, request: MemoryRequest) -> MemoryResponse:
        return MemoryResponse(
            guidance="Task completed. Learnings will be consolidated.",
            relevant_memories=self._short_term[-3:],
            confidence=0.7,
            source_type="short_term",
        )

    def take_in_memory(self, trajectory_data: TrajectoryData) -> tuple[bool, str]:
        if not self._initialized:
            return False, "Memory not initialized"

        timestamp = datetime.now().isoformat()

        if trajectory_data.outcome == "success" and trajectory_data.score >= 7.0:
            for learning in trajectory_data.learnings:
                self._add_strategic(
                    {
                        "task": trajectory_data.task,
                        "learning": learning,
                        "score": trajectory_data.score,
                        "timestamp": timestamp,
                    }
                )
            return (
                True,
                f"Learned {len(trajectory_data.learnings)} strategic patterns from successful execution",
            )

        elif trajectory_data.outcome == "success":
            for learning in trajectory_data.learnings:
                self._add_operational(
                    {
                        "task": trajectory_data.task,
                        "learning": learning,
                        "score": trajectory_data.score,
                        "timestamp": timestamp,
                    }
                )
            return True, f"Stored {len(trajectory_data.learnings)} operational patterns"

        else:
            anti_pattern = (
                f"AVOID: {trajectory_data.task} - {trajectory_data.error_trace or 'Failed'}"
            )
            self._add_operational(
                {
                    "task": trajectory_data.task,
                    "learning": anti_pattern,
                    "score": trajectory_data.score,
                    "timestamp": timestamp,
                    "is_anti_pattern": True,
                }
            )
            return True, f"Recorded failure to avoid: {trajectory_data.task}"

    def _add_short_term(self, fact: str) -> None:
        self._short_term.append(fact)
        if len(self._short_term) > self.max_short_term:
            self._short_term = self._short_term[-self.max_short_term :]

    def _add_strategic(self, memory: dict) -> None:
        self._long_term_strategic.append(memory)
        if len(self._long_term_strategic) > self.max_long_term_strategic:
            self._long_term_strategic.sort(key=lambda m: m.get("score", 0))
            self._long_term_strategic = self._long_term_strategic[1:]

    def _add_operational(self, memory: dict) -> None:
        self._long_term_operational.append(memory)
        if len(self._long_term_operational) > self.max_long_term_operational:
            non_anti = [m for m in self._long_term_operational if not m.get("is_anti_pattern")]
            if non_anti:
                self._long_term_operational.remove(non_anti[0])
            else:
                self._long_term_operational = self._long_term_operational[1:]

    def _search_memories(
        self,
        query: str,
        memories: list[dict],
        top_k: int = 3,
    ) -> list[dict]:
        if not memories:
            return []

        query_words = set(query.lower().split())
        scored = []

        for mem in memories:
            task_words = set(mem.get("task", "").lower().split())
            learning_words = set(mem.get("learning", "").lower().split())
            all_words = task_words | learning_words

            overlap = len(query_words & all_words)
            if overlap > 0:
                score = overlap + mem.get("score", 0) * 0.1
                scored.append((score, mem))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:top_k]]

    def clear_short_term(self) -> None:
        self._short_term = []

    def get_stats(self) -> dict:
        return {
            "short_term_count": len(self._short_term),
            "strategic_count": len(self._long_term_strategic),
            "operational_count": len(self._long_term_operational),
            "initialized": self._initialized,
        }
