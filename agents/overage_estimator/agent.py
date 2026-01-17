from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common.base_agent import BaseAgent, utc_now_iso
from common.artifacts import write_json, artifact_ref


class OveragesEstimationAgent(BaseAgent):
    """
    Estimates surplus/overage amount from available numeric inputs.

    Input payload examples:
      {
        "sale_price": 250000,
        "judgment_amount": 175000,
        "known_liens_total": 12000,
        "fees_estimate": 5000
      }

    Output:
      - estimated_overage
      - confidence (v0 heuristic)
      - reasoning fields
    """

    agent_name = "overage_estimator"
    agent_version = "0.1.0"

    def __init__(self, fixtures: Optional[Any] = None):
        self.fixtures = fixtures

    def _run(self, payload: Dict[str, Any], run_config: Dict[str, Any], artifact_dir: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
        sale_price = float(payload.get("sale_price") or 0.0)
        judgment = float(payload.get("judgment_amount") or 0.0)
        liens = float(payload.get("known_liens_total") or 0.0)
        fees = float(payload.get("fees_estimate") or 0.0)

        est = sale_price - judgment - liens - fees
        est = max(est, 0.0)

        inputs_present = sum(1 for x in [sale_price, judgment, liens, fees] if x > 0)
        confidence = 0.25 + 0.15 * inputs_present  # 0.40–0.85 typical v0
        confidence = min(confidence, 0.90)

        data = {
            "sale_price": sale_price,
            "judgment_amount": judgment,
            "known_liens_total": liens,
            "fees_estimate": fees,
            "estimated_overage": est,
            "confidence": confidence,
            "ts": utc_now_iso(),
        }

        out = artifact_dir / "overage_estimate.json"
        write_json(out, data)

        artifacts = [artifact_ref(out, "json", "overage_estimate")]
        audit = [{"action": "estimate_overage", "object": "case", "result": "ok", "ts": utc_now_iso()}]
        return data, artifacts, audit
