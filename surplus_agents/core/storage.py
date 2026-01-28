import json
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional


class StorageManager:
    """Manages artifact storage and retrieval."""
    
    def __init__(self, base_dir: str = "./artifacts"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def get_agent_dir(self, agent_name: str, run_id: str) -> Path:
        """Get the directory for a specific agent run."""
        agent_dir = self.base_dir / agent_name / run_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        return agent_dir
    
    def write_json(self, path: Path, data: Dict[str, Any]) -> str:
        """
        Write JSON data to a file and return its SHA-256 hash.
        
        Args:
            path: File path to write to
            data: Data to serialize as JSON
        
        Returns:
            SHA-256 hash of the written file
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(data, indent=2)
        path.write_text(content)
        return self.compute_hash(path)
    
    def read_json(self, path: Path) -> Dict[str, Any]:
        """Read JSON data from a file."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        content = path.read_text()
        return json.loads(content)
    
    def write_text(self, path: Path, content: str) -> str:
        """
        Write text to a file and return its SHA-256 hash.
        
        Args:
            path: File path to write to
            content: Text content to write
        
        Returns:
            SHA-256 hash of the written file
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return self.compute_hash(path)
    
    def read_text(self, path: Path) -> str:
        """Read text from a file."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return path.read_text()
    
    def write_bytes(self, path: Path, data: bytes) -> str:
        """
        Write binary data to a file and return its SHA-256 hash.
        
        Args:
            path: File path to write to
            data: Binary data to write
        
        Returns:
            SHA-256 hash of the written file
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return self.compute_hash(path)
    
    def read_bytes(self, path: Path) -> bytes:
        """Read binary data from a file."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return path.read_bytes()
    
    def compute_hash(self, path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def file_exists(self, path: Path) -> bool:
        """Check if a file exists."""
        return path.exists() and path.is_file()
    
    def list_artifacts(self, agent_name: str, run_id: str) -> list[Path]:
        """List all artifacts for a specific agent run."""
        agent_dir = self.base_dir / agent_name / run_id
        if not agent_dir.exists():
            return []
        return list(agent_dir.iterdir())
