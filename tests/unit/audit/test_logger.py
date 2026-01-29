"""Unit tests for audit logger."""

import pytest
from pathlib import Path
import tempfile
import json

from surplus_agents.core.audit.logger import AuditLogger, AuditEntry


@pytest.fixture
def temp_audit_dir():
    """Create a temporary directory for audit logs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.mark.unit
def test_audit_logger_initialization(temp_audit_dir):
    """Test audit logger initialization."""
    logger = AuditLogger(temp_audit_dir, mode="TEST")
    assert logger.audit_dir == temp_audit_dir
    assert logger.mode == "TEST"
    assert len(logger.entries) == 0


@pytest.mark.unit
def test_audit_logger_log_entry(temp_audit_dir):
    """Test logging an audit entry."""
    logger = AuditLogger(temp_audit_dir, mode="TEST")
    
    entry = logger.log(
        action="create",
        actor="test_agent",
        object_type="document",
        object_id="doc123",
        result="ok",
        details={"file": "test.pdf"}
    )
    
    assert isinstance(entry, AuditEntry)
    assert entry.action == "create"
    assert entry.actor == "test_agent"
    assert entry.object_type == "document"
    assert entry.object_id == "doc123"
    assert entry.result == "ok"
    assert entry.mode == "TEST"
    assert len(logger.entries) == 1


@pytest.mark.unit
def test_audit_logger_save(temp_audit_dir):
    """Test saving audit entries to file."""
    logger = AuditLogger(temp_audit_dir, mode="TEST")
    
    logger.log("create", "agent1", "doc", "1", "ok")
    logger.log("update", "agent2", "doc", "2", "ok")
    
    audit_file = logger.save()
    
    assert audit_file.exists()
    
    # Read and verify content
    with audit_file.open('r') as f:
        lines = f.readlines()
    
    assert len(lines) == 2
    
    # Verify JSON format
    entry1 = json.loads(lines[0])
    assert entry1["action"] == "create"
    assert entry1["actor"] == "agent1"


@pytest.mark.unit
def test_audit_logger_query(temp_audit_dir):
    """Test querying audit entries."""
    logger = AuditLogger(temp_audit_dir, mode="TEST")
    
    logger.log("create", "agent1", "doc", "1", "ok")
    logger.log("update", "agent1", "doc", "2", "ok")
    logger.log("delete", "agent2", "doc", "3", "error")
    
    # Query by action
    creates = logger.get_entries(action="create")
    assert len(creates) == 1
    assert creates[0].action == "create"
    
    # Query by actor
    agent1_entries = logger.get_entries(actor="agent1")
    assert len(agent1_entries) == 2
    
    # Query by result
    errors = logger.get_entries(result="error")
    assert len(errors) == 1
    assert errors[0].result == "error"


@pytest.mark.unit
def test_audit_logger_load_from_file(temp_audit_dir):
    """Test loading audit entries from file."""
    logger = AuditLogger(temp_audit_dir, mode="TEST")
    
    logger.log("create", "agent1", "doc", "1", "ok")
    audit_file = logger.save()
    
    # Load entries
    loaded_entries = AuditLogger.load_from_file(audit_file)
    
    assert len(loaded_entries) == 1
    assert loaded_entries[0]["action"] == "create"


@pytest.mark.unit
def test_audit_entry_to_dict():
    """Test converting AuditEntry to dictionary."""
    entry = AuditEntry(
        timestamp="2024-01-01T00:00:00Z",
        action="create",
        actor="test_agent",
        object_type="doc",
        object_id="123",
        result="ok",
        details={"key": "value"},
        mode="TEST"
    )
    
    entry_dict = entry.to_dict()
    
    assert entry_dict["action"] == "create"
    assert entry_dict["actor"] == "test_agent"
    assert entry_dict["mode"] == "TEST"
    assert entry_dict["details"]["key"] == "value"
