from dataclasses import dataclass
from typing import Any, Dict, List, Literal

Status = Literal["ok", "blocked", "error"]
Mode = Literal["TEST", "DRY_RUN", "LIVE"]
Network = Literal["OFF", "ON"]


@dataclass
class ArtifactRef:
    type: str
    path: str
    sha256: str
    label: str = ""


@dataclass
class AgentResult:
    agent_name: str
    agent_version: str
    run_id: str
    status: Status
    data: Dict[str, Any]
    artifacts: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    audit: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
