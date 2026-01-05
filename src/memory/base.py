"""Base memory provider protocol following MemEvolve architecture.

Reference: https://github.com/bingreeky/MemEvolve
Paper: https://arxiv.org/abs/2512.18746

The dual-loop architecture:
- Inner Loop (Content Evolution): Agent learns task-specific info as experiences
- Outer Loop (Architecture Evolution): Meta-process optimizes memory structure itself
"""

from enum import Enum
from typing import Any, Optional, Protocol, runtime_checkable
from pydantic import BaseModel, Field
from datetime import datetime


class MemoryStatus(str, Enum):
    """Memory retrieval timing in agent lifecycle."""

    BEGIN = "BEGIN"
    IN = "IN"
    END = "END"


class MemoryRequest(BaseModel):
    """Request for memory guidance from the provider."""

    query: str = Field(description="The task or question requiring memory support")
    context: str = Field(default="", description="Current execution context")
    status: MemoryStatus = Field(description="Current phase in agent lifecycle")
    additional_params: dict[str, Any] = Field(
        default_factory=dict,
        description="Extra parameters (e.g., step_number, agent_name)",
    )
    timestamp: datetime = Field(default_factory=datetime.now)


class MemoryResponse(BaseModel):
    """Response containing memory-guided information."""

    guidance: str = Field(description="Strategic or operational guidance from memory")
    relevant_memories: list[str] = Field(
        default_factory=list,
        description="Retrieved memory excerpts supporting the guidance",
    )
    confidence: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Confidence in the guidance quality"
    )
    source_type: str = Field(
        default="hybrid",
        description="Memory source: 'short_term', 'long_term', 'hybrid'",
    )
    additional_params: dict[str, Any] = Field(
        default_factory=dict,
        description="Extra parameters (e.g., tree_path, tree_node)",
    )


class TrajectoryData(BaseModel):
    """Execution trajectory for memory learning (take_in_memory input)."""

    task: str = Field(description="The task that was executed")
    steps: list[str] = Field(default_factory=list, description="Execution steps taken")
    outcome: str = Field(description="Result: 'success', 'partial', 'failure'")
    score: float = Field(ge=0.0, le=10.0, description="Performance score")
    learnings: list[str] = Field(
        default_factory=list,
        description="Key insights extracted from this trajectory",
    )
    error_trace: Optional[str] = Field(default=None, description="Error details if failed")
    timestamp: datetime = Field(default_factory=datetime.now)


@runtime_checkable
class BaseMemoryProvider(Protocol):
    """Protocol defining the memory provider interface.

    Any memory system (Voyager, ExpeL, DILU, or custom) must implement
    this interface to work with the MemEvolve framework.

    The dual-buffer pattern (from LightweightMemoryProvider):
    1. Short-term: In-memory facts for current task
    2. Long-term: Persistent strategic + operational memories
    """

    def initialize(self) -> bool:
        """Setup storage, load indices, connect to backends."""
        ...

    def provide_memory(self, request: MemoryRequest) -> MemoryResponse:
        """Retrieve guidance based on task query and current context."""
        ...

    def take_in_memory(self, trajectory_data: TrajectoryData) -> tuple[bool, str]:
        """Ingest learnings from a completed execution trajectory."""
        ...
