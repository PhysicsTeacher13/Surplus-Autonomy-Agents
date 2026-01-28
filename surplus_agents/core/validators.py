from typing import Any, Dict, List, Optional
import re


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    Validate that required fields are present in data.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
    
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif data[field] is None:
            errors.append(f"Field cannot be None: {field}")
    return errors


def validate_type(value: Any, expected_type: type, field_name: str = "value") -> Optional[str]:
    """
    Validate that a value is of the expected type.
    
    Args:
        value: Value to validate
        expected_type: Expected type
        field_name: Name of the field (for error messages)
    
    Returns:
        Error message if invalid, None otherwise
    """
    if not isinstance(value, expected_type):
        return f"Field '{field_name}' must be of type {expected_type.__name__}, got {type(value).__name__}"
    return None


def validate_string_length(
    value: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    field_name: str = "value"
) -> Optional[str]:
    """
    Validate string length constraints.
    
    Args:
        value: String to validate
        min_length: Minimum length (optional)
        max_length: Maximum length (optional)
        field_name: Name of the field (for error messages)
    
    Returns:
        Error message if invalid, None otherwise
    """
    if not isinstance(value, str):
        return f"Field '{field_name}' must be a string"
    
    if min_length is not None and len(value) < min_length:
        return f"Field '{field_name}' must be at least {min_length} characters"
    
    if max_length is not None and len(value) > max_length:
        return f"Field '{field_name}' must be at most {max_length} characters"
    
    return None


def validate_numeric_range(
    value: float,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    field_name: str = "value"
) -> Optional[str]:
    """
    Validate numeric range constraints.
    
    Args:
        value: Number to validate
        min_value: Minimum value (optional)
        max_value: Maximum value (optional)
        field_name: Name of the field (for error messages)
    
    Returns:
        Error message if invalid, None otherwise
    """
    if not isinstance(value, (int, float)):
        return f"Field '{field_name}' must be numeric"
    
    if min_value is not None and value < min_value:
        return f"Field '{field_name}' must be at least {min_value}"
    
    if max_value is not None and value > max_value:
        return f"Field '{field_name}' must be at most {max_value}"
    
    return None


def validate_email(email: str, field_name: str = "email") -> Optional[str]:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        field_name: Name of the field (for error messages)
    
    Returns:
        Error message if invalid, None otherwise
    """
    if not isinstance(email, str):
        return f"Field '{field_name}' must be a string"
    
    # Basic email validation pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return f"Field '{field_name}' is not a valid email address"
    
    return None


def validate_url(url: str, field_name: str = "url") -> Optional[str]:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        field_name: Name of the field (for error messages)
    
    Returns:
        Error message if invalid, None otherwise
    """
    if not isinstance(url, str):
        return f"Field '{field_name}' must be a string"
    
    # Basic URL validation pattern
    pattern = r'^https?://[^\s/$.?#][^\s]*$'
    if not re.match(pattern, url):
        return f"Field '{field_name}' is not a valid URL"
    
    return None


def validate_result_schema(result: Dict[str, Any]) -> List[str]:
    """
    Validate that an agent result follows the expected schema.
    
    Args:
        result: Agent result dictionary
    
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    required_fields = [
        "agent_name", "agent_version", "run_id", "status",
        "data", "artifacts", "metrics", "audit", "errors"
    ]
    errors.extend(validate_required_fields(result, required_fields))
    
    if "status" in result and result["status"] not in ["ok", "blocked", "error"]:
        errors.append(f"Invalid status: {result['status']}. Must be one of: ok, blocked, error")
    
    if "data" in result:
        type_error = validate_type(result["data"], dict, "data")
        if type_error:
            errors.append(type_error)
    
    if "artifacts" in result:
        type_error = validate_type(result["artifacts"], list, "artifacts")
        if type_error:
            errors.append(type_error)
    
    if "metrics" in result:
        type_error = validate_type(result["metrics"], dict, "metrics")
        if type_error:
            errors.append(type_error)
    
    if "audit" in result:
        type_error = validate_type(result["audit"], list, "audit")
        if type_error:
            errors.append(type_error)
    
    if "errors" in result:
        type_error = validate_type(result["errors"], list, "errors")
        if type_error:
            errors.append(type_error)
    
    return errors
