# src/utils.py

import json
from typing import Any

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_json(json_string: str) -> bool:
    """
    Validate if a string is valid JSON.
    
    Args:
        json_string (str): String to validate as JSON
        
    Returns:
        bool: True if valid JSON, False otherwise
    """
    try:
        json.loads(json_string)
        return True
    except:
        return False

def safe_json_loads(json_string: str) -> Any:
    """
    Safely load JSON string with error handling.
    
    Args:
        json_string (str): JSON string to parse
        
    Returns:
        Any: Parsed JSON data
        
    Raises:
        ValidationError: If JSON is invalid
    """
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON: {str(e)}")
