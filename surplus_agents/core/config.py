"""Configuration management for Surplus Autonomy Agents."""

from typing import Dict, Any, Optional
from pathlib import Path
import os


class Config:
    """
    Configuration manager for the application.
    
    Supports multiple operating modes: TEST, DRY_RUN, LIVE
    """
    
    # Valid operating modes
    VALID_MODES = {"TEST", "DRY_RUN", "LIVE"}
    
    # Valid network settings
    VALID_NETWORK = {"ON", "OFF"}
    
    def __init__(
        self,
        mode: str = "TEST",
        network: str = "OFF",
        artifact_dir: Optional[Path] = None,
        audit_dir: Optional[Path] = None
    ):
        """
        Initialize configuration.
        
        Args:
            mode: Operating mode (TEST, DRY_RUN, LIVE)
            network: Network setting (ON, OFF)
            artifact_dir: Directory for artifacts
            audit_dir: Directory for audit logs
        """
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {self.VALID_MODES}")
        
        if network not in self.VALID_NETWORK:
            raise ValueError(f"Invalid network: {network}. Must be one of {self.VALID_NETWORK}")
        
        self.mode = mode
        self.network = network
        self.artifact_dir = Path(artifact_dir) if artifact_dir else Path("./artifacts")
        self.audit_dir = Path(audit_dir) if audit_dir else Path("./audit")
        
        # Ensure directories exist
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary
        """
        return {
            "mode": self.mode,
            "network": self.network,
            "artifact_dir": str(self.artifact_dir),
            "audit_dir": str(self.audit_dir)
        }
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        Create configuration from environment variables.
        
        Environment variables:
            - SURPLUS_MODE: Operating mode
            - SURPLUS_NETWORK: Network setting
            - SURPLUS_ARTIFACT_DIR: Artifact directory
            - SURPLUS_AUDIT_DIR: Audit directory
            
        Returns:
            Config instance
        """
        mode = os.getenv("SURPLUS_MODE", "TEST")
        network = os.getenv("SURPLUS_NETWORK", "OFF")
        artifact_dir = os.getenv("SURPLUS_ARTIFACT_DIR")
        audit_dir = os.getenv("SURPLUS_AUDIT_DIR")
        
        return cls(
            mode=mode,
            network=network,
            artifact_dir=Path(artifact_dir) if artifact_dir else None,
            audit_dir=Path(audit_dir) if audit_dir else None
        )
