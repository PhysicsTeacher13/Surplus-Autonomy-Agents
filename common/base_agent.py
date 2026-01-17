import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .artifacts import write_json, artifact_ref
from .validate import validate_result

class BaseAgent:
    """
    Production-aligned base agent:
    - standardized output schema
    - artifact directory per run_id
    - catches errors into structured result
    - writes result.json always
    """

    agent_name: str = "base"
    agent_version: str = "0.1.0"

    def run(self, payload: Dict[str, Any], run_config: Dict[str, Any]) -> Dict[str, Any]:
        run_id = run_config.get("run_id") or str(uuid.uuid4())
        t0 = time.time()

        artifacts: List[Dict[str, Any]] = []
        audit: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []

        artifact_root = Path(run_config.get("artifact_dir", "./artifacts"))
        artifact_dir = artifact_root / self.agent_name / run_id
        artifact_dir.mkdir(parents=True, exist_ok=True)

        try:
            data, artifacts2, audit2 = self._run(payload, run_config, artifact_dir)
            artifacts.extend(artifacts2 or [])
            audit.extend(audit2 or [])
            status = "ok"
        except PermissionError as e:
            data = {}
            status = "blocked"
            errors.append({"code": "POLICY_BLOCK", "message": str(e), "details": {}})
        except Exception as e:
            data = {}
            status = "error"
            errors.append({"code": "UNHANDLED", "message": str(e), "details": {}})

        duration_ms = int((time.time() - t0) * 1000)

        result: Dict[str, Any] = {
            "agent_name": self.agent_name,
            "agent_version": self.agent_version,
            "run_id": run_id,
            "status": status,
            "data": data,
            "artifacts": artifacts,
            "metrics": {"duration_ms": duration_ms},
            "audit": audit,
            "errors": errors,
        }

        # Always write result.json
        result_path = artifact_dir / "result.json"
        write_json(result_path, result)
        result["artifacts"].append(artifact_ref(result_path, "json", "agent_result"))

        # Validate schema shape
        schema_errs = validate_result(result)
        if schema_errs:
            result["status"] = "error"
            result["errors"].append({
                "code": "SCHEMA_INVALID",
                "message": "; ".join(schema_errs),
                "details": {}
            })
            write_json(result_path, result)

        return result

    def _run(
        self,
        payload: Dict[str, Any],
        run_config: Dict[str, Any],
        artifact_dir: Path
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
        raise NotImplementedError("Subclasses must implement _run().")

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
