"""
TI-PULS Configuration Settings
"""

import os
from pathlib import Path

# System Configuration
SYSTEM_CONFIG = {
    "name": "TI-PULS-BD-KING-R7",
    "version": "1.0.0",
    "description": "Technology Intelligence - Proactive Unified Learning System",
    "max_workers": 10,
    "processing_interval": 1,  # seconds
    "log_retention_days": 30,
    "backup_enabled": True,
    "auto_update": True
}

# AI Model Configuration
AI_CONFIG = {
    "neural_network": {
        "layers": [128, 64, 32],
        "activation": "relu",
        "learning_rate": 0.001,
        "training_epochs": 100
    },
    "machine_learning": {
        "algorithms": ["random_forest", "svm", "neural_network"],
        "cross_validation_folds": 5,
        "feature_scaling": True
    },
    "deep_learning": {
        "model_type": "transformer",
        "attention_heads": 8,
        "hidden_size": 512
    }
}

# Security Configuration
SECURITY_CONFIG = {
    "encryption": {
        "algorithm": "AES-256-GCM",
        "key_rotation_days": 30
    },
    "authentication": {
        "jwt_expiry_hours": 24,
        "max_login_attempts": 5
    },
    "network": {
        "allowed_ips": ["127.0.0.1", "192.168.1.0/24"],
        "port_scan_protection": True
    }
}

# Data Processing Configuration
DATA_CONFIG = {
    "sources": [
        {
            "name": "bd_king_database",
            "type": "sqlite",
            "path": "/data/bd_king.db",
            "tables": ["transactions", "inventory", "customers"]
        },
        {
            "name": "system_logs",
            "type": "file",
            "path": "/var/log/bd-king",
            "format": "json"
        }
    ],
    "processing": {
        "batch_size": 1000,
        "real_time_processing": True,
        "data_validation": True
    }
}

# Monitoring Configuration
MONITORING_CONFIG = {
    "health_checks": {
        "interval_seconds": 60,
        "cpu_threshold": 80,
        "memory_threshold": 85,
        "disk_threshold": 90
    },
    "alerts": {
        "email_enabled": True,
        "sms_enabled": False,
        "webhook_url": None
    },
    "metrics": {
        "retention_days": 7,
        "collection_interval": 30
    }
}

def get_config():
    """Get complete configuration"""
    return {
        "system": SYSTEM_CONFIG,
        "ai": AI_CONFIG,
        "security": SECURITY_CONFIG,
        "data": DATA_CONFIG,
        "monitoring": MONITORING_CONFIG
    }