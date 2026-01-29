"""Unit tests for pipeline orchestrator."""

import pytest
from pathlib import Path
import tempfile

from surplus_agents.pipelines.orchestrator.pipeline import (
    PipelineOrchestrator,
    PipelineStage,
    StageResult
)
from surplus_agents.core.audit.logger import AuditLogger


@pytest.fixture
def temp_artifact_dir():
    """Create temporary artifact directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.mark.unit
def test_pipeline_initialization(temp_artifact_dir):
    """Test pipeline orchestrator initialization."""
    pipeline = PipelineOrchestrator(
        name="test_pipeline",
        mode="TEST",
        artifact_dir=temp_artifact_dir
    )
    
    assert pipeline.name == "test_pipeline"
    assert pipeline.mode == "TEST"
    assert len(pipeline.stages) == 0


@pytest.mark.unit
def test_pipeline_add_stage(temp_artifact_dir):
    """Test adding stages to pipeline."""
    pipeline = PipelineOrchestrator(
        name="test_pipeline",
        artifact_dir=temp_artifact_dir
    )
    
    def handler(data):
        return data
    
    pipeline.add_stage(
        name="stage1",
        handler=handler,
        description="Test stage"
    )
    
    assert len(pipeline.stages) == 1
    assert pipeline.stages[0].name == "stage1"
    assert pipeline.stages[0].handler == handler


@pytest.mark.unit
def test_pipeline_execute_simple(temp_artifact_dir):
    """Test executing a simple pipeline."""
    pipeline = PipelineOrchestrator(
        name="test_pipeline",
        artifact_dir=temp_artifact_dir
    )
    
    def stage1(data):
        return {"stage1": data}
    
    def stage2(data):
        data["stage2"] = "done"
        return data
    
    pipeline.add_stage("stage1", stage1)
    pipeline.add_stage("stage2", stage2)
    
    result = pipeline.execute({"input": "test"})
    
    assert result["status"] == "ok"
    assert result["output"]["stage1"]["input"] == "test"
    assert result["output"]["stage2"] == "done"
    assert len(result["stages"]) == 2


@pytest.mark.unit
def test_pipeline_stage_error_required(temp_artifact_dir):
    """Test pipeline stops on required stage failure."""
    pipeline = PipelineOrchestrator(
        name="test_pipeline",
        artifact_dir=temp_artifact_dir
    )
    
    def stage1(data):
        raise ValueError("Stage 1 failed")
    
    def stage2(data):
        return {"stage2": "should not run"}
    
    pipeline.add_stage("stage1", stage1, required=True)
    pipeline.add_stage("stage2", stage2)
    
    result = pipeline.execute({"input": "test"})
    
    assert result["status"] == "error"
    # Only stage1 should have run
    assert len(result["stages"]) == 1
    assert result["stages"][0]["status"] == "error"


@pytest.mark.unit
def test_pipeline_stage_error_optional(temp_artifact_dir):
    """Test pipeline continues on optional stage failure."""
    pipeline = PipelineOrchestrator(
        name="test_pipeline",
        artifact_dir=temp_artifact_dir
    )
    
    def stage1(data):
        raise ValueError("Stage 1 failed")
    
    def stage2(data):
        return {"stage2": "completed"}
    
    pipeline.add_stage("stage1", stage1, required=False)
    pipeline.add_stage("stage2", stage2, required=True)
    
    result = pipeline.execute({"input": "test"})
    
    # Pipeline should have partial success
    assert result["status"] == "partial"
    assert len(result["stages"]) == 2
    assert result["stages"][0]["status"] == "error"
    assert result["stages"][1]["status"] == "ok"


@pytest.mark.unit
def test_pipeline_with_audit_logger(temp_artifact_dir):
    """Test pipeline with audit logging."""
    audit_dir = temp_artifact_dir / "audit"
    audit_logger = AuditLogger(audit_dir, mode="TEST")
    
    pipeline = PipelineOrchestrator(
        name="test_pipeline",
        mode="TEST",
        audit_logger=audit_logger,
        artifact_dir=temp_artifact_dir
    )
    
    def stage1(data):
        return {"result": "ok"}
    
    pipeline.add_stage("stage1", stage1)
    pipeline.execute({"input": "test"})
    
    # Check audit logs
    assert len(audit_logger.entries) >= 2  # start + complete + stage
    
    start_entries = audit_logger.get_entries(action="pipeline_start")
    assert len(start_entries) == 1
    
    complete_entries = audit_logger.get_entries(action="pipeline_complete")
    assert len(complete_entries) == 1


@pytest.mark.unit
def test_pipeline_retry_on_error(temp_artifact_dir):
    """Test stage retry on error."""
    pipeline = PipelineOrchestrator(
        name="test_pipeline",
        artifact_dir=temp_artifact_dir
    )
    
    call_count = {"count": 0}
    
    def flaky_stage(data):
        call_count["count"] += 1
        if call_count["count"] < 3:
            raise ValueError("Temporary error")
        return {"success": True}
    
    pipeline.add_stage(
        "flaky",
        flaky_stage,
        retry_on_error=True,
        max_retries=3
    )
    
    result = pipeline.execute({"input": "test"})
    
    assert result["status"] == "ok"
    assert call_count["count"] == 3  # Failed twice, succeeded on third


@pytest.mark.unit
def test_pipeline_saves_result(temp_artifact_dir):
    """Test pipeline saves result to artifact directory."""
    pipeline = PipelineOrchestrator(
        name="test_pipeline",
        artifact_dir=temp_artifact_dir
    )
    
    def stage1(data):
        return {"result": "ok"}
    
    pipeline.add_stage("stage1", stage1)
    pipeline.execute({"input": "test"})
    
    # Check that result file was created
    result_file = temp_artifact_dir / "test_pipeline_result.json"
    assert result_file.exists()


@pytest.mark.unit
def test_pipeline_get_stage_results(temp_artifact_dir):
    """Test getting stage results."""
    pipeline = PipelineOrchestrator(
        name="test_pipeline",
        artifact_dir=temp_artifact_dir
    )
    
    def stage1(data):
        return {"stage1": "ok"}
    
    pipeline.add_stage("stage1", stage1)
    pipeline.execute({"input": "test"})
    
    results = pipeline.get_stage_results()
    assert len(results) == 1
    
    result = pipeline.get_stage_result("stage1")
    assert result is not None
    assert result.stage_name == "stage1"
    assert result.status == "ok"


@pytest.mark.unit
def test_stage_result_to_dict():
    """Test converting StageResult to dictionary."""
    result = StageResult(
        stage_name="test",
        status="ok",
        output={"data": "value"},
        duration_ms=100,
        timestamp="2024-01-01T00:00:00Z"
    )
    
    result_dict = result.to_dict()
    
    assert result_dict["stage_name"] == "test"
    assert result_dict["status"] == "ok"
    assert result_dict["output"]["data"] == "value"
    assert result_dict["duration_ms"] == 100
