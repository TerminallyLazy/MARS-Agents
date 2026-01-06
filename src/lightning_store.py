"""Agent Lightning-inspired trajectory store and resource management."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from collections import deque
import threading
import json


@dataclass
class Span:
    """Execution span capturing a single agent action (OpenTelemetry-inspired)."""

    span_id: str
    agent_name: str
    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    input_data: str = ""
    output_data: str = ""
    error: Optional[str] = None
    metrics: dict = field(default_factory=dict)


@dataclass
class Rollout:
    """Complete execution trajectory for optimization."""

    rollout_id: str
    task: str
    spans: list[Span] = field(default_factory=list)
    total_reward: float = 0.0
    attempts: int = 0
    max_attempts: int = 3
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class Resource:
    """Optimized resource (prompt template, few-shot examples, etc.)."""

    resource_id: str
    resource_type: str
    content: Any
    version: int = 1
    score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Heartbeat:
    """Worker heartbeat for fault detection."""

    worker_id: str
    agent_name: str
    timestamp: datetime
    status: str = "alive"
    current_task: Optional[str] = None
    metrics: dict = field(default_factory=dict)


class LightningStore:
    """Central store for trajectories, resources, and coordination (Agent Lightning pattern)."""

    def __init__(self, max_rollouts: int = 100, max_resources: int = 50):
        self._lock = threading.RLock()
        self._rollouts: deque[Rollout] = deque(maxlen=max_rollouts)
        self._resources: dict[str, Resource] = {}
        self._heartbeats: dict[str, Heartbeat] = {}
        self._pending_queue: deque[str] = deque()
        self._triplets: list[tuple[str, list[Span], float]] = []

    def create_rollout(self, task: str) -> Rollout:
        with self._lock:
            rollout_id = f"rollout_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            rollout = Rollout(rollout_id=rollout_id, task=task)
            self._rollouts.append(rollout)
            self._pending_queue.append(rollout_id)
            return rollout

    def add_span(self, rollout_id: str, span: Span) -> None:
        with self._lock:
            for rollout in self._rollouts:
                if rollout.rollout_id == rollout_id:
                    rollout.spans.append(span)
                    break

    def complete_rollout(self, rollout_id: str, reward: float) -> None:
        with self._lock:
            for rollout in self._rollouts:
                if rollout.rollout_id == rollout_id:
                    rollout.status = "completed"
                    rollout.total_reward = reward
                    rollout.completed_at = datetime.now()
                    self._triplets.append((rollout.task, rollout.spans, reward))
                    break

    def fail_rollout(self, rollout_id: str, error: str) -> bool:
        with self._lock:
            for rollout in self._rollouts:
                if rollout.rollout_id == rollout_id:
                    rollout.attempts += 1
                    if rollout.attempts < rollout.max_attempts:
                        rollout.status = "retry"
                        self._pending_queue.append(rollout_id)
                        return True
                    else:
                        rollout.status = "failed"
                        return False
            return False

    def dequeue_rollout(self, worker_id: str) -> Optional[Rollout]:
        with self._lock:
            if not self._pending_queue:
                return None
            rollout_id = self._pending_queue.popleft()
            for rollout in self._rollouts:
                if rollout.rollout_id == rollout_id:
                    rollout.status = "running"
                    return rollout
            return None

    def save_resource(self, resource: Resource) -> None:
        with self._lock:
            existing = self._resources.get(resource.resource_id)
            if existing:
                resource.version = existing.version + 1
            self._resources[resource.resource_id] = resource

    def get_resource(self, resource_id: str) -> Optional[Resource]:
        with self._lock:
            return self._resources.get(resource_id)

    def get_best_resource(self, resource_type: str) -> Optional[Resource]:
        with self._lock:
            typed_resources = [
                r for r in self._resources.values() if r.resource_type == resource_type
            ]
            if not typed_resources:
                return None
            return max(typed_resources, key=lambda r: r.score)

    def update_heartbeat(self, heartbeat: Heartbeat) -> None:
        with self._lock:
            self._heartbeats[heartbeat.worker_id] = heartbeat

    def get_stale_workers(self, timeout_seconds: float = 30.0) -> list[str]:
        with self._lock:
            now = datetime.now()
            stale = []
            for worker_id, hb in self._heartbeats.items():
                if (now - hb.timestamp).total_seconds() > timeout_seconds:
                    stale.append(worker_id)
            return stale

    def get_optimization_triplets(
        self, min_reward: float = 0.0
    ) -> list[tuple[str, list[Span], float]]:
        with self._lock:
            return [(t, s, r) for t, s, r in self._triplets if r >= min_reward]

    def get_successful_patterns(self, threshold: float = 7.0) -> list[str]:
        with self._lock:
            patterns = []
            for task, spans, reward in self._triplets:
                if reward >= threshold:
                    pattern = " -> ".join([s.operation for s in spans])
                    patterns.append(pattern)
            return patterns

    def get_failed_patterns(self, threshold: float = 5.0) -> list[str]:
        with self._lock:
            patterns = []
            for task, spans, reward in self._triplets:
                if reward < threshold:
                    pattern = " -> ".join([s.operation for s in spans])
                    patterns.append(pattern)
            return patterns

    def get_stats(self) -> dict:
        with self._lock:
            completed = sum(1 for r in self._rollouts if r.status == "completed")
            failed = sum(1 for r in self._rollouts if r.status == "failed")
            avg_reward = sum(
                r.total_reward for r in self._rollouts if r.status == "completed"
            ) / max(completed, 1)
            return {
                "total_rollouts": len(self._rollouts),
                "completed": completed,
                "failed": failed,
                "pending": len(self._pending_queue),
                "avg_reward": avg_reward,
                "resources": len(self._resources),
                "triplets": len(self._triplets),
            }


_global_store: Optional[LightningStore] = None
_store_lock = threading.Lock()


def get_store() -> LightningStore:
    global _global_store
    if _global_store is None:
        with _store_lock:
            if _global_store is None:
                _global_store = LightningStore()
    return _global_store
