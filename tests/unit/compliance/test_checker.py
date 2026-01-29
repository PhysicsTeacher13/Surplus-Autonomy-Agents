"""Unit tests for compliance checker."""

import pytest

from surplus_agents.core.compliance.checker import (
    ModeComplianceChecker,
    DataComplianceChecker,
    RequiredFieldRule,
    DataFormatRule
)


@pytest.mark.unit
def test_mode_compliance_checker_initialization():
    """Test mode compliance checker initialization."""
    checker = ModeComplianceChecker(mode="TEST")
    assert checker.mode == "TEST"
    
    checker = ModeComplianceChecker(mode="DRY_RUN")
    assert checker.mode == "DRY_RUN"
    
    checker = ModeComplianceChecker(mode="LIVE")
    assert checker.mode == "LIVE"


@pytest.mark.unit
def test_mode_compliance_checker_invalid_mode():
    """Test that invalid mode raises error."""
    with pytest.raises(ValueError, match="Invalid mode"):
        ModeComplianceChecker(mode="INVALID")


@pytest.mark.unit
def test_mode_compliance_test_mode_blocks_actions():
    """Test that TEST mode blocks restricted actions."""
    checker = ModeComplianceChecker(mode="TEST")
    
    # Restricted actions should be blocked
    assert not checker.is_action_allowed("send_email")
    assert not checker.is_action_allowed("submit_form")
    assert not checker.is_action_allowed("place_call")
    assert not checker.is_action_allowed("make_payment")
    
    # Safe actions should be allowed
    assert checker.is_action_allowed("read_data")
    assert checker.is_action_allowed("validate")


@pytest.mark.unit
def test_mode_compliance_dry_run_mode_blocks_actions():
    """Test that DRY_RUN mode blocks restricted actions."""
    checker = ModeComplianceChecker(mode="DRY_RUN")
    
    # Restricted actions should be blocked
    assert not checker.is_action_allowed("send_email")
    assert not checker.is_action_allowed("submit_form")
    assert not checker.is_action_allowed("make_payment")


@pytest.mark.unit
def test_mode_compliance_live_mode_allows_all():
    """Test that LIVE mode allows all actions."""
    checker = ModeComplianceChecker(mode="LIVE")
    
    # All actions should be allowed in LIVE mode
    assert checker.is_action_allowed("send_email")
    assert checker.is_action_allowed("submit_form")
    assert checker.is_action_allowed("make_payment")
    assert checker.is_action_allowed("read_data")


@pytest.mark.unit
def test_mode_compliance_assert_action_allowed():
    """Test assert_action_allowed raises PermissionError when blocked."""
    checker = ModeComplianceChecker(mode="TEST")
    
    # Should raise PermissionError for blocked action
    with pytest.raises(PermissionError, match="send_email.*blocked"):
        checker.assert_action_allowed("send_email")
    
    # Should not raise for allowed action
    checker.assert_action_allowed("read_data")


@pytest.mark.unit
def test_data_compliance_checker():
    """Test data compliance checker."""
    checker = DataComplianceChecker()
    
    # No rules initially
    issues = checker.validate({"field": "value"})
    assert len(issues) == 0


@pytest.mark.unit
def test_required_field_rule():
    """Test required field rule."""
    rule = RequiredFieldRule(fields=["name", "email"])
    
    # Valid data
    assert rule.validate({"name": "John", "email": "john@example.com"}) is None
    
    # Missing field
    error = rule.validate({"name": "John"})
    assert error is not None
    assert "email" in error
    
    # Empty field
    error = rule.validate({"name": "John", "email": ""})
    assert error is not None
    
    # Not a dictionary
    error = rule.validate("not a dict")
    assert error is not None
    assert "dictionary" in error


@pytest.mark.unit
def test_data_format_rule():
    """Test data format rule."""
    def is_email(value):
        return "@" in str(value)
    
    rule = DataFormatRule(
        field="email",
        validator_func=is_email,
        error_message="must contain @"
    )
    
    # Valid email
    assert rule.validate({"email": "test@example.com"}) is None
    
    # Invalid email
    error = rule.validate({"email": "invalid"})
    assert error is not None
    assert "@" in error
    
    # Field not present (should pass)
    assert rule.validate({"other_field": "value"}) is None


@pytest.mark.unit
def test_data_compliance_with_rules():
    """Test data compliance checker with multiple rules."""
    checker = DataComplianceChecker()
    
    # Add rules
    checker.add_rule(RequiredFieldRule(fields=["name", "email"]))
    
    def is_email(value):
        return "@" in str(value)
    
    checker.add_rule(DataFormatRule(
        field="email",
        validator_func=is_email,
        error_message="must be valid email"
    ))
    
    # Valid data
    issues = checker.validate({"name": "John", "email": "john@example.com"})
    assert len(issues) == 0
    
    # Missing field
    issues = checker.validate({"name": "John"})
    assert len(issues) >= 1
    assert any("required" in i["message"].lower() for i in issues)
    
    # Invalid format
    issues = checker.validate({"name": "John", "email": "invalid"})
    assert len(issues) >= 1
    assert any("email" in i["message"].lower() for i in issues)
