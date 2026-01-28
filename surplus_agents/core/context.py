from typing import Any, Dict, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class ExecutionContext:
    """Context information for an agent execution."""
    run_id: str
    agent_name: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def elapsed_seconds(self) -> float:
        """Get elapsed time since execution started."""
        now = datetime.now(timezone.utc)
        delta = now - self.started_at
        return delta.total_seconds()
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the context."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from the context."""
        return self.metadata.get(key, default)


class ContextManager:
    """Manages execution contexts for agents."""
    
    def __init__(self):
        self._contexts: Dict[str, ExecutionContext] = {}
    
    def create_context(self, run_id: str, agent_name: str) -> ExecutionContext:
        """Create a new execution context."""
        context = ExecutionContext(run_id=run_id, agent_name=agent_name)
        self._contexts[run_id] = context
        return context
    
    def get_context(self, run_id: str) -> Optional[ExecutionContext]:
        """Get an existing context by run_id."""
        return self._contexts.get(run_id)
    
    def remove_context(self, run_id: str) -> None:
        """Remove a context from the manager."""
        self._contexts.pop(run_id, None)
    
    def clear_all(self) -> None:
        """Clear all contexts."""
        self._contexts.clear()
