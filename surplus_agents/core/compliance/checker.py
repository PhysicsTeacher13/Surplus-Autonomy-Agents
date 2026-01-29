"""Compliance controls and policy enforcement."""

from typing import Dict, Set, Optional, List, Any
from dataclasses import dataclass


@dataclass
class ComplianceRule:
    """Represents a compliance rule."""
    name: str
    description: str
    severity: str  # "error", "warning", "info"
    
    def validate(self, data: Any) -> Optional[str]:
        """
        Validate data against this rule.
        
        Returns:
            Error message if validation fails, None if passes
        """
        raise NotImplementedError("Subclasses must implement validate()")


class ModeComplianceChecker:
    """
    Enforces mode-based restrictions (TEST/DRY_RUN/LIVE).
    
    Blocks certain actions in non-LIVE modes to prevent unintended operations.
    """
    
    # Actions that are blocked in TEST and DRY_RUN modes
    RESTRICTED_ACTIONS: Dict[str, Set[str]] = {
        "TEST": {
            "send_email",
            "submit_form",
            "place_call",
            "send_fax",
            "ship_fedex",
            "make_payment",
            "file_document",
            "send_notification"
        },
        "DRY_RUN": {
            "send_email",
            "submit_form",
            "place_call",
            "send_fax",
            "ship_fedex",
            "make_payment",
            "file_document",
            "send_notification"
        },
        "LIVE": set()
    }
    
    def __init__(self, mode: str = "TEST"):
        """
        Initialize compliance checker.
        
        Args:
            mode: Operating mode (TEST, DRY_RUN, LIVE)
        """
        if mode not in self.RESTRICTED_ACTIONS:
            raise ValueError(f"Invalid mode: {mode}. Must be TEST, DRY_RUN, or LIVE")
        self.mode = mode
    
    def is_action_allowed(self, action: str) -> bool:
        """
        Check if an action is allowed in the current mode.
        
        Args:
            action: Action to check
            
        Returns:
            True if allowed, False if blocked
        """
        blocked = self.RESTRICTED_ACTIONS.get(self.mode, set())
        return action not in blocked
    
    def assert_action_allowed(self, action: str) -> None:
        """
        Assert that an action is allowed, raise exception if blocked.
        
        Args:
            action: Action to check
            
        Raises:
            PermissionError: If action is blocked in current mode
        """
        if not self.is_action_allowed(action):
            raise PermissionError(
                f"Action '{action}' is blocked in mode={self.mode}. "
                f"Switch to LIVE mode to perform this action."
            )


class DataComplianceChecker:
    """
    Validates data against compliance rules.
    
    Ensures data meets regulatory and business requirements.
    """
    
    def __init__(self):
        """Initialize data compliance checker."""
        self.rules: List[ComplianceRule] = []
    
    def add_rule(self, rule: ComplianceRule) -> None:
        """Add a compliance rule."""
        self.rules.append(rule)
    
    def validate(self, data: Any) -> List[Dict[str, str]]:
        """
        Validate data against all rules.
        
        Args:
            data: Data to validate
            
        Returns:
            List of validation errors/warnings
        """
        issues = []
        for rule in self.rules:
            error = rule.validate(data)
            if error:
                issues.append({
                    "rule": rule.name,
                    "severity": rule.severity,
                    "message": error
                })
        return issues


class RequiredFieldRule(ComplianceRule):
    """Rule to check for required fields in a dictionary."""
    
    def __init__(self, fields: List[str], severity: str = "error"):
        super().__init__(
            name="required_fields",
            description=f"Required fields: {', '.join(fields)}",
            severity=severity
        )
        self.fields = fields
    
    def validate(self, data: Any) -> Optional[str]:
        if not isinstance(data, dict):
            return "Data must be a dictionary"
        
        missing = [f for f in self.fields if f not in data or not data[f]]
        if missing:
            return f"Missing required fields: {', '.join(missing)}"
        return None


class DataFormatRule(ComplianceRule):
    """Rule to validate data format."""
    
    def __init__(self, field: str, validator_func, error_message: str, severity: str = "error"):
        super().__init__(
            name=f"format_{field}",
            description=f"Validate format of {field}",
            severity=severity
        )
        self.field = field
        self.validator_func = validator_func
        self.error_message = error_message
    
    def validate(self, data: Any) -> Optional[str]:
        if not isinstance(data, dict):
            return "Data must be a dictionary"
        
        if self.field not in data:
            return None  # Field not present, skip validation
        
        if not self.validator_func(data[self.field]):
            return f"{self.field}: {self.error_message}"
        return None
