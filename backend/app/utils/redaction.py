import copy
from typing import Any

SENSITIVE_KEYS = {
    "accesskeyid",
    "secretaccesskey",
    "sessiontoken",
    "credentials",
    "authorization",
    "password",
    "clientsecret",
    "access_token",
    "refresh_token"
}

REDACTED_MARKER = "[REDACTED]"

def _redact_recursive(data: Any) -> Any:
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(key, str) and key.lower() in SENSITIVE_KEYS:
                result[key] = REDACTED_MARKER
            else:
                result[key] = _redact_recursive(value)
        return result
    
    if isinstance(data, list):
        return [_redact_recursive(item) for item in data]
        
    return data

def redact_sensitive_data(log: Any) -> Any:
    """
    Returns a sanitized deep copy of the input log.
    If the input is None or a primitive, it safely returns it.
    The original log is not mutated.
    """
    if log is None:
        return None
    
    # Deep copy to ensure no mutation of the original object
    try:
        log_copy = copy.deepcopy(log)
    except TypeError:
        # In case it's something not serializable/copyable, fallback to raw
        log_copy = log
        
    return _redact_recursive(log_copy)
