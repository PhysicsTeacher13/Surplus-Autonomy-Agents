from typing import Any, Dict, List

REQUIRED_TOP_KEYS = [
    "agent_name",
    "agent_version",
    "run_id",
    "status",
    "data",
    "artifacts",
    "metrics",
    "audit",
    "errors",
]

ALLOWED_STATUS = {"ok", "blocked", "error"}

def validate_result(result: Dict[str, Any]) -> List[str]:
    errs: List[str] = []

    for k in REQUIRED_TOP_KEYS:
        if k not in result:
            errs.append(f"Missing key: {k}")

    if "status" in result and result["status"] not in ALLOWED_STATUS:
        errs.append(f"Invalid status: {result.get('status')}")

    if "artifacts" in result and not isinstance(result["artifacts"], list):
        errs.append("artifacts must be a list")

    if "errors" in result and not isinstance(result["errors"], list):
        errs.append("errors must be a list")

    if "audit" in result and not isinstance(result["audit"], list):
        errs.append("audit must be a list")

    if "metrics" in result and not isinstance(result["metrics"], dict):
        errs.append("metrics must be a dict")

    if "data" in result and not isinstance(result["data"], dict):
        errs.append("data must be a dict")

    return errs
