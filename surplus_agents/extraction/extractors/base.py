"""Base extractor class for data extraction."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional


class BaseExtractor(ABC):
    """
    Base class for all data extractors.
    
    Extractors handle parsing and normalization of data from various sources
    (PDFs, HTML, JSON, etc.) into standardized formats.
    """
    
    def __init__(self, mode: str = "TEST"):
        """
        Initialize extractor.
        
        Args:
            mode: Operating mode (TEST, DRY_RUN, LIVE)
        """
        self.mode = mode
    
    @abstractmethod
    def extract(self, source: Any, **kwargs) -> Dict[str, Any]:
        """
        Extract and normalize data from source.
        
        Args:
            source: Data source (file path, string content, etc.)
            **kwargs: Additional extraction parameters
            
        Returns:
            Normalized data dictionary
        """
        pass
    
    def validate_output(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate extracted data.
        
        Args:
            data: Extracted data
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        if not isinstance(data, dict):
            errors.append("Output must be a dictionary")
        return errors
