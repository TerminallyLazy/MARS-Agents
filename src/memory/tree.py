from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import random
import math
import uuid


@dataclass
class MemoryNode:
    node_id: str
    content: str
    parent_id: Optional[str] = None
    children: list["MemoryNode"] = field(default_factory=list)

    mean_utility: float = 0.0
    utility_samples: list[float] = field(default_factory=list)
    visit_count: int = 0

    improvement_description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    score: float = 0.0

    def add_child(self, child: "MemoryNode") -> None:
        child.parent_id = self.node_id
        self.children.append(child)

    def update_utility(self, utility: float) -> None:
        self.utility_samples.append(utility)
        self.visit_count += 1
        self.mean_utility = sum(self.utility_samples) / len(self.utility_samples)
        self.score = self.mean_utility

    def get_ucb_score(self, total_visits: int, c: float = 1.414) -> float:
        if self.visit_count == 0:
            return float("inf")

        exploitation = self.mean_utility
        exploration = c * math.sqrt(math.log(total_visits + 1) / self.visit_count)
        return exploitation + exploration

    def sample_thompson(self) -> float:
        if self.visit_count < 2:
            return random.random() * 10

        alpha = max(1, self.mean_utility)
        beta = max(1, 10 - self.mean_utility)

        return random.betavariate(alpha, beta) * 10


class MemoryTree:
    def __init__(self, root_content: str = "Initial memory state"):
        self._nodes: dict[str, MemoryNode] = {}
        self.root = MemoryNode(
            node_id="root",
            content=root_content,
        )
        self._nodes["root"] = self.root
        self._total_visits = 0

    def add_version(
        self,
        parent_id: str,
        content: str,
        improvement_description: str,
    ) -> Optional[MemoryNode]:
        parent = self._nodes.get(parent_id)
        if parent is None:
            return None

        node_id = f"node_{uuid.uuid4().hex[:8]}"
        new_node = MemoryNode(
            node_id=node_id,
            content=content,
            parent_id=parent_id,
            improvement_description=improvement_description,
        )

        parent.add_child(new_node)
        self._nodes[node_id] = new_node
        return new_node

    def get_node(self, node_id: str) -> Optional[MemoryNode]:
        return self._nodes.get(node_id)

    def get_best_path(self) -> list[MemoryNode]:
        path = [self.root]
        current = self.root

        while current.children:
            best_child = max(current.children, key=lambda n: n.mean_utility)
            path.append(best_child)
            current = best_child

        return path

    def select_node_thompson(self) -> MemoryNode:
        candidates: list[MemoryNode] = []
        self._collect_candidates(self.root, candidates)

        if not candidates:
            return self.root

        samples = [(node, node.sample_thompson()) for node in candidates]

        best_node, _ = max(samples, key=lambda x: x[1])
        return best_node

    def _collect_candidates(
        self,
        node: MemoryNode,
        candidates: list[MemoryNode],
        max_depth: int = 10,
        depth: int = 0,
    ) -> None:
        if depth >= max_depth:
            return

        if node.visit_count < 5 or node.mean_utility < 9.0:
            candidates.append(node)

        for child in node.children:
            self._collect_candidates(child, candidates, max_depth, depth + 1)

    def update_path_utilities(self, leaf_node_id: str, utility: float) -> None:
        current = self._nodes.get(leaf_node_id)
        self._total_visits += 1

        while current:
            current.update_utility(utility)
            if current.parent_id:
                current = self._nodes.get(current.parent_id)
            else:
                break

    def get_pareto_front(self) -> list[MemoryNode]:
        all_nodes = list(self._nodes.values())
        pareto_front = []

        for node in all_nodes:
            is_dominated = False
            for other in all_nodes:
                if other.node_id == node.node_id:
                    continue
                if (
                    other.mean_utility >= node.mean_utility
                    and other.visit_count <= node.visit_count
                    and (
                        other.mean_utility > node.mean_utility
                        or other.visit_count < node.visit_count
                    )
                ):
                    is_dominated = True
                    break

            if not is_dominated:
                pareto_front.append(node)

        return pareto_front

    def get_stats(self) -> dict:
        return {
            "total_nodes": len(self._nodes),
            "total_visits": self._total_visits,
            "max_depth": self._get_max_depth(self.root, 0),
            "pareto_front_size": len(self.get_pareto_front()),
        }

    def _get_max_depth(self, node: MemoryNode, depth: int) -> int:
        if not node.children:
            return depth
        return max(self._get_max_depth(c, depth + 1) for c in node.children)
