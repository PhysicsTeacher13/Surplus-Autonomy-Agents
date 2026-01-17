from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common.base_agent import BaseAgent, utc_now_iso
from common.artifacts import write_json, artifact_ref
from common.policy import assert_allowed


class TemplateAgent(BaseAgent):
    """
    Canonical agent template.

    All agents MUST:
    - subclass BaseAgent
    - implement _run(payload, run_config, artifact_dir)
    - return (data, artifacts, audit)
    - respect policy gates for real-world actions
    """

    agent_name = "template_agent"
    agent_version = "0.1.0"

    def __init__(self, fixtures: Optional[Any] = None):
        self.fixtures = fixtures

    def _run(
        self,
        payload: Dict[str, Any],
        run_config: Dict[str, Any],
        artifact_dir: Path
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:

        # Example: if this agent would send an email, enforce policy:
        # assert_allowed(run_config, "send_email")

        if "example_input" not in payload:
            raise ValueError("Missing required field: example_input")

        processed_value = str(payload["example_input"]).upper()

        data = {
            "input_received": payload["example_input"],
            "processed_value": processed_value,
            "mode": run_config.get("mode", "TEST"),
            "network": run_config.get("network", "OFF"),
            "timestamp": utc_now_iso(),
        }

        out_path = artifact_dir / "output.json"
        write_json(out_path, data)

        artifacts = [artifact_ref(out_path, "json", "processed_output")]
        audit = [{"action": "process_input", "object": "example_input", "result": "ok", "ts": utc_now_iso()}]

        return data, artifacts, audit
