"""Storage utilities for Surplus Autonomy Agents."""

import json
from pathlib import Path
from typing import Any, Dict, List


class StorageManager:
    """
    Manages artifact and data storage.
    
    Provides utilities for saving and loading structured data,
    organizing files by run_id and agent name.
    """
    
    def __init__(self, base_dir: Path = Path("./artifacts")):
        """
        Initialize storage manager.
        
        Args:
            base_dir: Base directory for all storage
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def get_agent_dir(self, agent_name: str, run_id: str) -> Path:
        """
        Get storage directory for a specific agent run.
        
        Args:
            agent_name: Name of the agent
            run_id: Run identifier
            
        Returns:
            Path to agent's run directory
        """
        agent_dir = self.base_dir / agent_name / run_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        return agent_dir
    
    def save_json(self, path: Path, data: Any) -> Path:
        """
        Save data as JSON.
        
        Args:
            path: File path
            data: Data to save
            
        Returns:
            Path to saved file
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return path
    
    def load_json(self, path: Path) -> Any:
        """
        Load data from JSON file.
        
        Args:
            path: File path
            
        Returns:
            Loaded data
        """
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_text(self, path: Path, text: str) -> Path:
        """
        Save text content.
        
        Args:
            path: File path
            text: Text content
            
        Returns:
            Path to saved file
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path
    
    def load_text(self, path: Path) -> str:
        """
        Load text content.
        
        Args:
            path: File path
            
        Returns:
            Text content
        """
        return path.read_text(encoding='utf-8')
    
    def list_runs(self, agent_name: str) -> List[str]:
        """
        List all run IDs for an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            List of run IDs
        """
        agent_dir = self.base_dir / agent_name
        if not agent_dir.exists():
            return []
        
        return [d.name for d in agent_dir.iterdir() if d.is_dir()]
