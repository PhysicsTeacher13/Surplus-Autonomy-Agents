"""Structured audit logger for tracking all operations."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class AuditEntry:
    """Represents a single audit log entry."""
    timestamp: str
    action: str
    actor: str
    object_type: str
    object_id: str
    result: str
    details: Dict[str, Any]
    mode: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class AuditLogger:
    """
    Centralized audit logger for tracking all operations.
    
    Supports TEST, DRY_RUN, and LIVE modes.
    All audit entries are timestamped and stored in structured format.
    """
    
    def __init__(self, audit_dir: Path, mode: str = "TEST"):
        """
        Initialize audit logger.
        
        Args:
            audit_dir: Directory to store audit logs
            mode: Operating mode (TEST, DRY_RUN, LIVE)
        """
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.mode = mode
        self.entries: List[AuditEntry] = []
    
    def log(
        self,
        action: str,
        actor: str,
        object_type: str,
        object_id: str,
        result: str,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """
        Log an audit entry.
        
        Args:
            action: Action performed (e.g., "create", "update", "delete")
            actor: Who performed the action (agent name, user, etc.)
            object_type: Type of object affected
            object_id: Identifier of the object
            result: Result of the action ("ok", "error", "blocked")
            details: Additional context/details
            
        Returns:
            Created audit entry
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        entry = AuditEntry(
            timestamp=timestamp,
            action=action,
            actor=actor,
            object_type=object_type,
            object_id=object_id,
            result=result,
            details=details or {},
            mode=self.mode
        )
        self.entries.append(entry)
        return entry
    
    def save(self, filename: str = "audit.jsonl") -> Path:
        """
        Save all audit entries to a JSONL file.
        
        Args:
            filename: Name of the audit file
            
        Returns:
            Path to saved audit file
        """
        audit_file = self.audit_dir / filename
        with audit_file.open("a", encoding="utf-8") as f:
            for entry in self.entries:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
        return audit_file
    
    def get_entries(
        self,
        action: Optional[str] = None,
        actor: Optional[str] = None,
        object_type: Optional[str] = None,
        result: Optional[str] = None
    ) -> List[AuditEntry]:
        """
        Query audit entries with filters.
        
        Args:
            action: Filter by action
            actor: Filter by actor
            object_type: Filter by object type
            result: Filter by result
            
        Returns:
            List of matching audit entries
        """
        filtered = self.entries
        
        if action:
            filtered = [e for e in filtered if e.action == action]
        if actor:
            filtered = [e for e in filtered if e.actor == actor]
        if object_type:
            filtered = [e for e in filtered if e.object_type == object_type]
        if result:
            filtered = [e for e in filtered if e.result == result]
            
        return filtered
    
    @staticmethod
    def load_from_file(audit_file: Path) -> List[Dict[str, Any]]:
        """
        Load audit entries from a JSONL file.
        
        Args:
            audit_file: Path to audit file
            
        Returns:
            List of audit entry dictionaries
        """
        entries = []
        if audit_file.exists():
            with audit_file.open("r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
        return entries
