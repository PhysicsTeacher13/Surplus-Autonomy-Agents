"""Pipeline orchestrator for managing multi-stage workflows."""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json
import traceback


@dataclass
class PipelineStage:
    """Represents a single stage in a pipeline."""
    name: str
    handler: Callable
    description: str = ""
    required: bool = True
    retry_on_error: bool = False
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (exclude handler)."""
        return {
            'name': self.name,
            'description': self.description,
            'required': self.required,
            'retry_on_error': self.retry_on_error,
            'max_retries': self.max_retries
        }


@dataclass
class StageResult:
    """Result of executing a pipeline stage."""
    stage_name: str
    status: str  # "ok", "error", "skipped"
    output: Any
    error: Optional[str] = None
    duration_ms: int = 0
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class PipelineOrchestrator:
    """
    Orchestrates multi-stage data processing pipelines.
    
    Features:
    - Stage-by-stage execution with dependencies
    - Error handling and retry logic
    - Progress tracking and reporting
    - Audit logging
    - TEST/DRY_RUN/LIVE mode support
    """
    
    def __init__(
        self,
        name: str,
        mode: str = "TEST",
        audit_logger: Optional[Any] = None,
        artifact_dir: Optional[Path] = None
    ):
        """
        Initialize pipeline orchestrator.
        
        Args:
            name: Pipeline name
            mode: Operating mode (TEST, DRY_RUN, LIVE)
            audit_logger: Audit logger instance
            artifact_dir: Directory for artifacts
        """
        self.name = name
        self.mode = mode
        self.audit_logger = audit_logger
        self.artifact_dir = Path(artifact_dir) if artifact_dir else Path("./artifacts")
        self.stages: List[PipelineStage] = []
        self.stage_results: List[StageResult] = []
    
    def add_stage(
        self,
        name: str,
        handler: Callable,
        description: str = "",
        required: bool = True,
        retry_on_error: bool = False,
        max_retries: int = 3
    ) -> None:
        """
        Add a stage to the pipeline.
        
        Args:
            name: Stage name
            handler: Function to execute for this stage
            description: Stage description
            required: Whether stage is required (pipeline fails if required stage fails)
            retry_on_error: Whether to retry on error
            max_retries: Maximum retry attempts
        """
        stage = PipelineStage(
            name=name,
            handler=handler,
            description=description,
            required=required,
            retry_on_error=retry_on_error,
            max_retries=max_retries
        )
        self.stages.append(stage)
    
    def execute(self, initial_data: Any) -> Dict[str, Any]:
        """
        Execute the pipeline.
        
        Args:
            initial_data: Initial input data for the pipeline
            
        Returns:
            Pipeline execution result
        """
        start_time = datetime.now(timezone.utc)
        self.stage_results = []
        current_data = initial_data
        
        if self.audit_logger:
            self.audit_logger.log(
                action="pipeline_start",
                actor=self.name,
                object_type="pipeline",
                object_id=self.name,
                result="ok",
                details={"stage_count": len(self.stages)}
            )
        
        # Execute each stage
        for stage in self.stages:
            result = self._execute_stage(stage, current_data)
            self.stage_results.append(result)
            
            if result.status == "error":
                if stage.required:
                    # Required stage failed, stop pipeline
                    break
                # Non-required stage failed, continue
            else:
                # Update current_data with stage output
                current_data = result.output
        
        # Determine overall pipeline status
        has_errors = any(r.status == "error" for r in self.stage_results)
        failed_required = any(
            r.status == "error" and s.required
            for r, s in zip(self.stage_results, self.stages)
        )
        
        if failed_required:
            status = "error"
        elif has_errors:
            status = "partial"
        else:
            status = "ok"
        
        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        pipeline_result = {
            "pipeline": self.name,
            "status": status,
            "mode": self.mode,
            "output": current_data,
            "stages": [r.to_dict() for r in self.stage_results],
            "metadata": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_ms": duration_ms,
                "total_stages": len(self.stages),
                "successful_stages": sum(1 for r in self.stage_results if r.status == "ok"),
                "failed_stages": sum(1 for r in self.stage_results if r.status == "error")
            }
        }
        
        # Save pipeline result
        self._save_result(pipeline_result)
        
        if self.audit_logger:
            self.audit_logger.log(
                action="pipeline_complete",
                actor=self.name,
                object_type="pipeline",
                object_id=self.name,
                result=status,
                details=pipeline_result["metadata"]
            )
        
        return pipeline_result
    
    def _execute_stage(self, stage: PipelineStage, input_data: Any) -> StageResult:
        """
        Execute a single pipeline stage.
        
        Args:
            stage: Stage to execute
            input_data: Input data for the stage
            
        Returns:
            Stage execution result
        """
        import time
        
        start_time = time.time()
        timestamp = datetime.now(timezone.utc).isoformat()
        attempts = 0
        max_attempts = stage.max_retries + 1 if stage.retry_on_error else 1
        
        last_error = None
        
        while attempts < max_attempts:
            attempts += 1
            
            try:
                output = stage.handler(input_data)
                duration_ms = int((time.time() - start_time) * 1000)
                
                if self.audit_logger:
                    self.audit_logger.log(
                        action="stage_execute",
                        actor=self.name,
                        object_type="stage",
                        object_id=stage.name,
                        result="ok",
                        details={"attempts": attempts, "duration_ms": duration_ms}
                    )
                
                return StageResult(
                    stage_name=stage.name,
                    status="ok",
                    output=output,
                    duration_ms=duration_ms,
                    timestamp=timestamp
                )
                
            except Exception as e:
                last_error = str(e)
                
                if attempts < max_attempts:
                    # Will retry
                    continue
                
                # All retries exhausted
                duration_ms = int((time.time() - start_time) * 1000)
                
                if self.audit_logger:
                    self.audit_logger.log(
                        action="stage_execute",
                        actor=self.name,
                        object_type="stage",
                        object_id=stage.name,
                        result="error",
                        details={
                            "error": last_error,
                            "attempts": attempts,
                            "duration_ms": duration_ms,
                            "traceback": traceback.format_exc()
                        }
                    )
                
                return StageResult(
                    stage_name=stage.name,
                    status="error",
                    output=None,
                    error=last_error,
                    duration_ms=duration_ms,
                    timestamp=timestamp
                )
        
        # Should not reach here
        return StageResult(
            stage_name=stage.name,
            status="error",
            output=None,
            error="Unknown error"
        )
    
    def _save_result(self, result: Dict[str, Any]) -> None:
        """Save pipeline result to artifact directory."""
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        result_file = self.artifact_dir / f"{self.name}_result.json"
        
        with result_file.open('w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    def get_stage_results(self) -> List[StageResult]:
        """Get results of all executed stages."""
        return self.stage_results
    
    def get_stage_result(self, stage_name: str) -> Optional[StageResult]:
        """Get result of a specific stage by name."""
        for result in self.stage_results:
            if result.stage_name == stage_name:
                return result
        return None
