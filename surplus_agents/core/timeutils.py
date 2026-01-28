from datetime import datetime, timezone, timedelta
from typing import Optional


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return utc_now().isoformat()


def parse_iso(timestamp: str) -> datetime:
    """
    Parse ISO 8601 timestamp string to datetime.
    
    Args:
        timestamp: ISO 8601 formatted timestamp string
    
    Returns:
        Datetime object in UTC
    """
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def format_iso(dt: datetime) -> str:
    """
    Format datetime to ISO 8601 string.
    
    Args:
        dt: Datetime object
    
    Returns:
        ISO 8601 formatted string
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def elapsed_seconds(start_time: datetime, end_time: Optional[datetime] = None) -> float:
    """
    Calculate elapsed seconds between two datetimes.
    
    Args:
        start_time: Start datetime
        end_time: End datetime (defaults to current UTC time)
    
    Returns:
        Elapsed seconds as float
    """
    if end_time is None:
        end_time = utc_now()
    delta = end_time - start_time
    return delta.total_seconds()


def elapsed_milliseconds(start_time: datetime, end_time: Optional[datetime] = None) -> int:
    """
    Calculate elapsed milliseconds between two datetimes.
    
    Args:
        start_time: Start datetime
        end_time: End datetime (defaults to current UTC time)
    
    Returns:
        Elapsed milliseconds as integer
    """
    seconds = elapsed_seconds(start_time, end_time)
    return int(seconds * 1000)


def add_seconds(dt: datetime, seconds: float) -> datetime:
    """Add seconds to a datetime."""
    return dt + timedelta(seconds=seconds)


def add_minutes(dt: datetime, minutes: float) -> datetime:
    """Add minutes to a datetime."""
    return dt + timedelta(minutes=minutes)


def add_hours(dt: datetime, hours: float) -> datetime:
    """Add hours to a datetime."""
    return dt + timedelta(hours=hours)


def add_days(dt: datetime, days: int) -> datetime:
    """Add days to a datetime."""
    return dt + timedelta(days=days)


def is_expired(timestamp: datetime, max_age_seconds: float) -> bool:
    """
    Check if a timestamp is older than max_age_seconds.
    
    Args:
        timestamp: The timestamp to check
        max_age_seconds: Maximum age in seconds
    
    Returns:
        True if expired, False otherwise
    """
    age = elapsed_seconds(timestamp)
    return age > max_age_seconds
