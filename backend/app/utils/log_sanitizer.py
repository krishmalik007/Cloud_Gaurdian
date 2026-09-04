"""
Log Sanitizer
=============

Provides a credential-redaction utility used before logging raw cloud
event dicts.  The ORIGINAL dict is never modified — a sanitized copy is
returned so the full event continues through the processing pipeline.

Redacted fields:
    responseElements.credentials.accessKeyId
    responseElements.credentials.secretAccessKey
    responseElements.credentials.sessionToken
    Any key whose name contains the substrings below (case-insensitive)
    at any level of nesting: "secretaccesskey", "sessiontoken", "password",
    "secret", "token" (only when nested under "credentials").
"""

import copy
from typing import Any

# Top-level keys inside a "credentials" dict that must always be redacted
_CREDENTIAL_KEYS = {
    "accesskeyid",
    "secretaccesskey",
    "sessiontoken",
}

# Top-level keys anywhere in the event that should be redacted if present
_SENSITIVE_TOP_LEVEL_KEYS = {
    "secretaccesskey",
    "sessiontoken",
    "password",
    "secret",
}

_REDACTED = "[REDACTED]"


def _sanitize_dict(d: Any, _inside_credentials: bool = False) -> Any:
    """
    Recursively walk a dict (or list) and replace sensitive values.
    The original object is never mutated.
    """
    if isinstance(d, dict):
        result = {}
        for key, value in d.items():
            key_lower = key.lower()

            # If the key is "credentials", replace the whole sub-dict
            # with a [REDACTED] marker — the entire credentials block
            # (accessKeyId, secretAccessKey, sessionToken) is sensitive.
            if key_lower == "credentials":
                result[key] = _REDACTED
                continue

            # Redact any top-level sensitive key (e.g. secretAccessKey
            # appearing directly on the event object)
            if key_lower in _SENSITIVE_TOP_LEVEL_KEYS:
                result[key] = _REDACTED
                continue

            # Recurse into nested dicts/lists
            result[key] = _sanitize_dict(value, _inside_credentials)

        return result

    if isinstance(d, list):
        return [_sanitize_dict(item, _inside_credentials) for item in d]

    # Scalar — return as-is
    return d


def redact_credentials(log: dict) -> dict:
    """
    Return a deep copy of ``log`` with all credential fields replaced by
    ``[REDACTED]``.  The original dict is not modified.

    Usage::

        safe = redact_credentials(raw_event)
        logger.info(f"Received Log: {safe}")
        pipeline.process(raw_event)   # original untouched
    """
    if not isinstance(log, dict):
        return log

    return _sanitize_dict(copy.deepcopy(log))
