from typing import Optional
from datetime import datetime

from src.memory.base import (
    MemoryRequest,
    MemoryResponse,
    TrajectoryData,
    MemoryStatus,
)
from src.memory.dual_buffer import DualBufferMemory
from src.memory.tree import MemoryTree, MemoryNode


class HierarchicalMemory:
    """Combines DualBufferMemory (content) + MemoryTree (structure) with Thompson Sampling."""

    def __init__(
        self,
        max_short_term: int = 10,
        max_long_term: int = 30,
    ):
        self._buffer: Optional[DualBufferMemory] = None
        self._tree: Optional[MemoryTree] = None
        self._current_node_id: str = "root"
        self._max_short_term = max_short_term
        self._max_long_term = max_long_term
        self._initialized = False

    def initialize(self) -> bool:
        self._buffer = DualBufferMemory(
            max_short_term=self._max_short_term,
            max_long_term_strategic=self._max_long_term,
            max_long_term_operational=self._max_long_term,
        )
        self._buffer.initialize()

        self._tree = MemoryTree(root_content="Initial memory architecture")
        self._current_node_id = "root"
        self._initialized = True
        return True

    def provide_memory(self, request: MemoryRequest) -> MemoryResponse:
        if not self._initialized:
            return MemoryResponse(
                guidance="Memory not initialized",
                confidence=0.0,
            )

        buffer_response = self._buffer.provide_memory(request)
        tree_guidance = self._get_tree_guidance(request)
        combined_guidance = self._merge_guidance(buffer_response.guidance, tree_guidance)

        additional_params = {
            "tree_node": self._current_node_id,
            "tree_path": [n.node_id for n in self._tree.get_best_path()],
        }

        return MemoryResponse(
            guidance=combined_guidance,
            relevant_memories=buffer_response.relevant_memories,
            confidence=min(0.95, buffer_response.confidence + 0.1),
            source_type="hierarchical",
            additional_params=additional_params,
        )

    def _get_tree_guidance(self, request: MemoryRequest) -> str:
        if request.status == MemoryStatus.BEGIN:
            selected_node = self._tree.select_node_thompson()
            self._current_node_id = selected_node.node_id

            if selected_node.improvement_description:
                return f"Strategy insight: {selected_node.improvement_description}"

        current_node = self._tree.get_node(self._current_node_id)
        if current_node and current_node.improvement_description:
            return f"Current strategy: {current_node.improvement_description}"

        return ""

    def _merge_guidance(self, buffer_guidance: str, tree_guidance: str) -> str:
        parts = []

        if tree_guidance:
            parts.append(f"[Strategic]\n{tree_guidance}")

        if buffer_guidance:
            parts.append(f"[Operational]\n{buffer_guidance}")

        return "\n\n".join(parts) if parts else "No specific guidance available."

    def take_in_memory(self, trajectory_data: TrajectoryData) -> tuple[bool, str]:
        if not self._initialized:
            return False, "Memory not initialized"

        buffer_success, buffer_msg = self._buffer.take_in_memory(trajectory_data)
        tree_msg = self._update_tree(trajectory_data)

        return True, f"{buffer_msg}. {tree_msg}"

    def _update_tree(self, trajectory_data: TrajectoryData) -> str:
        improvement = (
            "; ".join(trajectory_data.learnings[:2])
            if trajectory_data.learnings
            else trajectory_data.task
        )

        new_node = self._tree.add_version(
            parent_id=self._current_node_id,
            content=f"Memory state after: {trajectory_data.task}",
            improvement_description=improvement,
        )

        if new_node:
            self._tree.update_path_utilities(new_node.node_id, trajectory_data.score)

            if trajectory_data.score >= 7.0:
                self._current_node_id = new_node.node_id
                return f"Advanced to new memory state (node: {new_node.node_id})"
            else:
                return f"Added memory node but staying on current branch"

        return "Tree update failed"

    def evolve_structure(self) -> Optional[MemoryNode]:
        target_node = self._tree.select_node_thompson()

        new_node = self._tree.add_version(
            parent_id=target_node.node_id,
            content=f"Evolved from {target_node.node_id}",
            improvement_description=f"Structural evolution targeting utility > {target_node.mean_utility:.1f}",
        )

        return new_node

    def get_memory_state(self) -> dict:
        return {
            "tree_stats": self._tree.get_stats() if self._tree else {},
            "buffer_stats": self._buffer.get_stats() if self._buffer else {},
            "current_node": self._current_node_id,
            "best_path": [n.node_id for n in self._tree.get_best_path()] if self._tree else [],
            "pareto_front_size": len(self._tree.get_pareto_front()) if self._tree else 0,
            "initialized": self._initialized,
        }

    def clear_short_term(self) -> None:
        if self._buffer:
            self._buffer.clear_short_term()
