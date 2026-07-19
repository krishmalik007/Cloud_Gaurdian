"""
Correlation Rule Configuration

Every detection rule has its own threshold
and time window.

This file keeps all rule parameters in one place.
"""

RULE_CONFIG = {

    "MULTIPLE_FAILED_LOGINS": {
        "threshold": 5,
        "window_minutes": 5,
        "severity": "MEDIUM"
    },

    "BRUTE_FORCE": {
        "threshold": 10,
        "window_minutes": 2,
        "severity": "HIGH"
    },

    "MULTIPLE_IP_LOGIN": {
        "threshold": 3,
        "window_minutes": 2,
        "severity": "HIGH"
    },

    "BUSINESS_HOURS_LOGIN": {
        "start_hour": 9,
        "end_hour": 18,
        "severity": "LOW"
    },

    "CONCURRENT_LOGIN": {
        "window_minutes": 1,
        "severity": "HIGH"
    },

    "DISABLED_USER_LOGIN": {
        "severity": "CRITICAL"
    },

    "SERVICE_ACCOUNT_LOGIN": {
        "severity": "HIGH"
    },

    "MULTIPLE_PROVIDER_LOGIN": {
        "threshold": 2,
        "window_minutes": 5,
        "severity": "HIGH"
    }
}