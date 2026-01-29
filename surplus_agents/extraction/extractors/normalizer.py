"""Data normalizer for standardizing extracted data."""

from typing import Any, Dict, List, Optional
from datetime import datetime
import re


class DataNormalizer:
    """
    Normalizes and standardizes extracted data.
    
    Handles common data cleaning, formatting, and standardization tasks.
    """
    
    def __init__(self):
        """Initialize data normalizer."""
        pass
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text by cleaning whitespace and formatting.
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Trim
        text = text.strip()
        return text
    
    def normalize_phone(self, phone: str) -> Optional[str]:
        """
        Normalize phone number to standard format.
        
        Args:
            phone: Input phone number
            
        Returns:
            Normalized phone number or None if invalid
        """
        if not phone:
            return None
        
        # Extract digits only
        digits = re.sub(r'\D', '', phone)
        
        # Handle US phone numbers
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        return phone  # Return original if can't normalize
    
    def normalize_address(self, address: Dict[str, str]) -> Dict[str, str]:
        """
        Normalize address components.
        
        Args:
            address: Dictionary with address components
            
        Returns:
            Normalized address dictionary
        """
        normalized = {}
        
        # Normalize street
        if 'street' in address:
            normalized['street'] = self.normalize_text(address['street'])
        
        # Normalize city
        if 'city' in address:
            normalized['city'] = self.normalize_text(address['city']).title()
        
        # Normalize state
        if 'state' in address:
            state = address['state'].strip().upper()
            normalized['state'] = self._normalize_state(state)
        
        # Normalize zip
        if 'zip' in address or 'zip_code' in address:
            zip_code = address.get('zip') or address.get('zip_code', '')
            normalized['zip'] = self._normalize_zip(zip_code)
        
        return normalized
    
    def _normalize_state(self, state: str) -> str:
        """Normalize US state code."""
        # Map common state names to abbreviations
        state_map = {
            'CALIFORNIA': 'CA',
            'TEXAS': 'TX',
            'FLORIDA': 'FL',
            'NEW YORK': 'NY',
            # Add more as needed
        }
        
        state_upper = state.upper()
        if state_upper in state_map:
            return state_map[state_upper]
        
        # If already 2 letters, assume it's an abbreviation
        if len(state_upper) == 2:
            return state_upper
        
        return state
    
    def _normalize_zip(self, zip_code: str) -> str:
        """Normalize ZIP code."""
        # Extract digits and hyphen
        cleaned = re.sub(r'[^\d-]', '', zip_code)
        
        # Format as XXXXX or XXXXX-XXXX
        if '-' in cleaned:
            parts = cleaned.split('-')
            if len(parts[0]) == 5 and len(parts[1]) == 4:
                return cleaned
        elif len(cleaned) == 5:
            return cleaned
        elif len(cleaned) == 9:
            return f"{cleaned[:5]}-{cleaned[5:]}"
        
        return zip_code
    
    def normalize_date(self, date_str: str, output_format: str = "%Y-%m-%d") -> Optional[str]:
        """
        Normalize date string to standard format.
        
        Args:
            date_str: Input date string
            output_format: Desired output format
            
        Returns:
            Normalized date string or None if invalid
        """
        if not date_str:
            return None
        
        # Common date formats to try
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%m-%d-%Y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime(output_format)
            except ValueError:
                continue
        
        return None
    
    def normalize_currency(self, amount: Any) -> Optional[float]:
        """
        Normalize currency amount to float.
        
        Args:
            amount: Input amount (string or number)
            
        Returns:
            Normalized amount as float or None if invalid
        """
        if amount is None:
            return None
        
        if isinstance(amount, (int, float)):
            return float(amount)
        
        # Remove currency symbols and commas
        cleaned = re.sub(r'[$,]', '', str(amount))
        
        try:
            return float(cleaned)
        except ValueError:
            return None
