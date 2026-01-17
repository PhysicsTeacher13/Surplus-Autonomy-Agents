from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common.base_agent import BaseAgent, utc_now_iso
from common.artifacts import write_json, artifact_ref


class CourthouseDiscoveryAgent(BaseAgent):
    """
    v0 stub: normalizes courthouse records from structured inputs.

    In production, this agent will also parse PDFs (fixtures/courthouse_pdfs/...)
    and output normalized courthouse entities.
    """

    agent_name = "courthouse_discovery"
    agent_version = "0.1.0"

    def __init__(self, fixtures: Optional[Any] = None):
        self.fixtures = fixtures

    def _run(
        self,
        payload: Dict[str, Any],
        run_config: Dict[str, Any],
        artifact_dir: Path
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:

        # Minimal deterministic input for early testing
        courthouses = payload.get("courthouses", [])
        if not isinstance(courthouses, list):
            raise ValueError("payload.courthouses must be a list")

        normalized = []
        for c in courthouses:
            name = (c.get("name") or "").strip()
            address = (c.get("address") or "").strip()
            state = (c.get("state") or "").strip().upper()
            county = (c.get("county") or "").strip()

            if not name or not state:
                continue

            normalized.append({
                "name": name,
                "address": address,
                "state": state,
                "county": county,
                "phone": (c.get("phone") or "").strip(),
                "source": c.get("source", "manual"),
            })

        data = {
            "input_count": len(courthouses),
            "normalized_count": len(normalized),
            "courthouses": normalized,
            "ts": utc_now_iso(),
        }

        out = artifact_dir / "courthouses_normalized.json"
        write_json(out, data)

        artifacts = [artifact_ref(out, "json", "courthouses_normalized")]
        audit = [{"action": "normalize_courthouses", "object": "courthouse", "result": "ok", "ts": utc_now_iso()}]

        return data, artifacts, audit
