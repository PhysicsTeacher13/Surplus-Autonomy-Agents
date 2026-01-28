import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup a logger with consistent formatting.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        format_string: Custom format string (optional)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        if format_string is None:
            format_string = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
        
        formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


class AgentLogger:
    """Logger wrapper for agent operations."""
    
    def __init__(self, agent_name: str, run_id: str):
        self.agent_name = agent_name
        self.run_id = run_id
        self.logger = setup_logger(f"agent.{agent_name}")
    
    def _format_message(self, message: str) -> str:
        """Format message with run_id context."""
        return f"[{self.run_id}] {message}"
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(self._format_message(message))
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(self._format_message(message))
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(self._format_message(message))
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(self._format_message(message))
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(self._format_message(message))
