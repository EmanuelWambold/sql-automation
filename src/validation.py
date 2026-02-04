from typing import Any

# --- Validator Funtion ---
def validate_param_type(name: str, value: Any, expected_type: type, can_be_null: bool = False) -> None:
    """
    This method is used to validate a single parameter type and optional nullability.
    
    Args:
        - name (str): Parameter name for error reporting
        - value (Any): Value to validate
        - expected_type (type): Expected type (int, float, str, tuple of types)
        - can_be_null (bool): Allow None values (default: False)
        
    Raises:
        TypeError: if type doesn't match expected_type or nullability rules
    """
    
    if can_be_null and value is None:
        return  # None is explicitly allowed
    
    if not isinstance(value, expected_type):
        type_name = expected_type.__name__ if not isinstance(expected_type, tuple) else ', '.join(types.__name__ for types in expected_type)
        actual_type = type(value).__name__
        raise TypeError(f"{name} must be {type_name}{' or None' if can_be_null else ''}, got {actual_type} instead")