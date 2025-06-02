# utils/__init__.py
"""
Utility modules for Employee Management System
"""

# utils/config.py
"""
Configuration management for Employee Management System
"""

import os
import json
from pathlib import Path


class Config:
    """Application configuration manager"""

    DEFAULT_CONFIG = {
        "app_name": "Employee Management System",
        "version": "1.0.0",
        "database_name": "employee_management.db",
        "log_file": "employee_management.log",
        "date_format": "%Y-%m-%d",
        "datetime_format": "%Y-%m-%d %H:%M:%S",
        "annual_leave_days_default": 26,
        "notification_check_interval": 3600,  # seconds
        "contract_expiry_warning_days": 30,
        "medical_exam_warning_days": 30,
        "safety_training_warning_days": 30,
        "document_templates_dir": "templates",
        "generated_documents_dir": "documents",
        "export_dir": "exports"
    }

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.ensure_directories()

    def load_config(self) -> dict:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(user_config)
                    return config
            except Exception as e:
                print(f"Error loading config: {e}")

        # Return default config
        return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key: str, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()

    def ensure_directories(self):
        """Ensure required directories exist"""
        dirs = [
            self.get('document_templates_dir'),
            self.get('generated_documents_dir'),
            self.get('export_dir')
        ]

        for dir_name in dirs:
            if dir_name:
                Path(dir_name).mkdir(exist_ok=True)