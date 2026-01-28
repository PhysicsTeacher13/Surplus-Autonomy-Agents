class AgentError(Exception):
    """Base exception for agent failures."""

class ComplianceError(AgentError):
    """Raised when a requested action violates configured compliance rules."""

class ExternalServiceError(AgentError):
    """Raised when a third-party dependency fails (phone, email, portal, etc.)."""

class DataValidationError(AgentError):
    """Raised when required data is missing or malformed."""
