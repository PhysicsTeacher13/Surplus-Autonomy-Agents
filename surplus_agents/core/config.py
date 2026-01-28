from typing import Dict, Any
from dataclasses import dataclass, field
from .models import Mode, Network


@dataclass
class AgentConfig:
    """Configuration for agent execution."""
    mode: Mode = "TEST"
    network: Network = "OFF"
    artifact_dir: str = "./artifacts"
    run_id: str = ""
    timeout_seconds: int = 300
    max_retries: int = 3
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunConfig:
    """Runtime configuration for a specific agent run."""
    mode: Mode
    network: Network
    artifact_dir: str
    run_id: str
    timeout_seconds: int = 300
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "mode": self.mode,
            "network": self.network,
            "artifact_dir": self.artifact_dir,
            "run_id": self.run_id,
            "timeout_seconds": self.timeout_seconds,
            "extra": self.extra,
        }


def validate_mode(mode: str) -> Mode:
    """Validate and return a valid mode."""
    valid_modes = ["TEST", "DRY_RUN", "LIVE"]
    if mode not in valid_modes:
        raise ValueError(f"Invalid mode: {mode}. Must be one of {valid_modes}")
    return mode  # type: ignore


def validate_network(network: str) -> Network:
    """Validate and return a valid network setting."""
    valid_networks = ["OFF", "ON"]
    if network not in valid_networks:
        raise ValueError(f"Invalid network: {network}. Must be one of {valid_networks}")
    return network  # type: ignore
