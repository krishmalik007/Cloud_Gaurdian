"""
Correlation Rule Configuration

Every detection rule has its own threshold,
severity and time window.

Keeping rule parameters here allows easy
tuning without modifying rule logic.
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
        "window_minutes": 10,
        "severity": "HIGH"
    },

    "BUSINESS_HOURS_LOGIN": {
        "start_hour": 9,
        "end_hour": 18,
        "severity": "MEDIUM"
    },

    "CONCURRENT_LOGIN": {
        "window_minutes": 1,
        "severity": "HIGH"
    },

    "DISABLED_USER_LOGIN": {
        "expected_status": "DISABLED",
        "severity": "CRITICAL"
    },

    "SERVICE_ACCOUNT_LOGIN": {
        "account_type": "SERVICE",
        "severity": "HIGH"
    },

    "MULTIPLE_PROVIDER_LOGIN": {
        "threshold": 2,
        "window_minutes": 5,
        "severity": "HIGH"
    }

}