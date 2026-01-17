from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common.base_agent import BaseAgent, utc_now_iso
from common.artifacts import write_json, artifact_ref


class LienPriorityVerificationAgent(BaseAgent):
    """
    Produces a structured 'priority_result' from known lien/mortgage/creditor inputs.

    Payload example:
    {
      "program": "TSSF" or "SCP50",
      "liens": [{"type":"mortgage","amount":12345,"recorded_date":"YYYY-MM-DD","holder":"Bank"}],
      "creditor": {"name":"...", "claim_amount":..., "priority_basis":"..."}   # for SCP50
    }
    """

    agent_name = "lien_priority"
    agent_version = "0.1.0"

    def __init__(self, fixtures: Optional[Any] = None):
        self.fixtures = fixtures

    def _run(self, payload: Dict[str, Any], run_config: Dict[str, Any], artifact_dir: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
        program = (payload.get("program") or "TSSF").upper()
        liens = payload.get("liens") or []
        if not isinstance(liens, list):
            raise ValueError("payload.liens must be a list")

        total_liens = 0.0
        has_mortgage = False
        for l in liens:
            amt = float(l.get("amount") or 0.0)
            total_liens += max(amt, 0.0)
            if str(l.get("type") or "").lower() in ("mortgage", "deed of trust"):
                has_mortgage = True

        # v0 heuristic outcomes
        if program == "TSSF":
            status = "ok" if len(liens) >= 0 else "needs_review"
            notes = "TSSF requires lien/mortgage checks; v0 uses provided liens only."
        else:
            creditor = payload.get("creditor") or {}
            status = "ok" if creditor.get("name") else "needs_creditor_info"
            notes = "SCP50 requires creditor priority claim; v0 validates presence only."

        data = {
            "program": program,
            "liens_count": len(liens),
            "total_liens_amount": total_liens,
            "has_mortgage": has_mortgage,
            "priority_status": status,
            "notes": notes,
            "ts": utc_now_iso(),
        }

        out = artifact_dir / "priority_result.json"
        write_json(out, data)

        artifacts = [artifact_ref(out, "json", "priority_result")]
        audit = [{"action": "verify_lien_priority", "object": "case", "result": "ok", "ts": utc_now_iso()}]
        return data, artifacts, audit
