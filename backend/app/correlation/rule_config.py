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
    },

    # ==========================================================
    # IAM RULES
    # ==========================================================
    "IAM_PRIVILEGE_ESCALATION": {
        "severity": "CRITICAL"
    },
    
    "NEW_ADMIN_USER": {
        "severity": "HIGH"
    },
    
    "ROOT_ACCOUNT_USAGE": {
        "severity": "CRITICAL"
    },
    "MFA_DISABLED": {
        "severity": "HIGH"
    },
    "IAM_POLICY_CHANGED": {
        "severity": "MEDIUM"
    },
    "ACCESS_KEY_CREATED": {
        "severity": "MEDIUM"
    },
    "ACCESS_KEY_REACTIVATED": {
        "inactive_days": 90,
        "severity": "HIGH"
    },
    "MULTIPLE_IAM_CHANGES": {
        "threshold": 4,
        "window_minutes": 10,
        "severity": "CRITICAL"
    },


    # ============================================================
    # RESOURCE RULES
    # ============================================================
    "PUBLIC_BUCKET": {
        "severity": "CRITICAL"
    },
    "SECURITY_GROUP_OPEN": {
        "severity": "CRITICAL"
    },
    "INSTANCE_CREATED": {
        "severity": "MEDIUM"
    },
    "INSTANCE_TERMINATED": {
        "severity": "MEDIUM"
    },
    "UNUSUAL_REGION_RESOURCE": {
        "severity": "HIGH",
        "allowed_regions": [
            "us-east-1",
            "ap-south-1"
        ]
    },
    "LOAD_BALANCER_DELETED": {
        "severity": "HIGH"
    },
    "PUBLIC_SNAPSHOT": {
        "severity": "HIGH"
    },
    "MULTIPLE_RESOURCE_DELETIONS": {
        "severity": "CRITICAL",
        "threshold": 4,
        "window_minutes": 10
    },



    # ============================================================
    # DATA RULES
    # ============================================================
    "DATA_DOWNLOAD": {
        "severity": "HIGH",
        "threshold_mb": 500
    },
    "SENSITIVE_FILE_ACCESS": {
        "severity": "HIGH"
    },
    "MULTIPLE_STORAGE_READS": {
        "severity": "MEDIUM",
        "threshold": 20,
        "window_minutes": 5
    },
    "DATA_EXFILTRATION": {
        "severity": "CRITICAL",
        "threshold_mb": 1000
    },
    "PUBLIC_DATABASE_SNAPSHOT": {
        "severity": "CRITICAL"
    },
    "MASS_OBJECT_DELETION": {
        "severity": "HIGH",
        "threshold": 25,
        "window_minutes": 10
    },
    "CROSS_REGION_COPY": {
        "severity": "HIGH"
    },
    "MULTIPLE_DATA_EVENTS": {
        "severity": "CRITICAL",
        "threshold": 4,
        "window_minutes": 10
    },


    # ============================================================
    # CONFIGURATION RULES
    # ============================================================
    "AUDIT_LOGGING_DISABLED": {
        "severity": "CRITICAL"
    },
    "ENCRYPTION_DISABLED": {
        "severity": "CRITICAL"
    },
    "MFA_ENFORCEMENT_DISABLED": {
        "severity": "HIGH"
    },
    "WEAK_PASSWORD_POLICY": {
        "severity": "HIGH",
        "minimum_length": 12
    },
    "SECURITY_SERVICE_DISABLED": {
        "severity": "HIGH"
    },
    "BACKUP_DISABLED": {
        "severity": "HIGH"
    },
    "RETENTION_POLICY_CHANGED": {
        "severity": "MEDIUM"
    },
    "MULTIPLE_CONFIGURATION_CHANGES": {
        "severity": "CRITICAL",
        "threshold": 4,
        "window_minutes": 10
    }

}