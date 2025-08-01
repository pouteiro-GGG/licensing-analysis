"""
Configuration settings for the licensing analysis system.
"""

import os
from typing import Dict, Any

# Claude Opus 4 Configuration
CLAUDE_OPUS_4_CONFIG = {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 4000,
    "temperature": 0.1,
    "top_p": 0.9,
    "system_prompt": """You are an expert IT licensing analyst specializing in cost optimization and vendor management. 
    Analyze the provided data and provide actionable insights for cost savings and efficiency improvements."""
}

# Cache Configuration
CACHE_CONFIG = {
    "enabled": True,
    "directory": "data/cache",
    "expiration_hours": 24,
    "max_size_mb": 100
}

# Licensing Categories
LICENSING_CATEGORIES = {
    "microsoft": ["Office 365", "Azure", "Windows", "SQL Server", "SharePoint"],
    "adobe": ["Creative Suite", "Acrobat", "Photoshop", "Illustrator"],
    "vmware": ["vSphere", "vCenter", "ESXi", "Workstation"],
    "aws": ["EC2", "S3", "RDS", "Lambda", "CloudFormation"],
    "azure": ["Virtual Machines", "Storage", "App Service", "Functions"],
    "other": ["Custom Software", "Third-party Tools", "Legacy Systems"]
}

# Industry Standards and Benchmarks
INDUSTRY_STANDARDS = {
    "microsoft": {
        "office_365_business": 6.0,
        "office_365_enterprise": 22.0,
        "azure_vm_basic": 0.05,
        "azure_storage": 0.02
    },
    "adobe": {
        "creative_suite": 52.99,
        "acrobat_pro": 14.99,
        "photoshop": 20.99,
        "illustrator": 20.99
    },
    "vmware": {
        "vsphere_per_cpu": 1000.0,
        "vcenter": 5000.0,
        "esxi": 200.0
    },
    "aws": {
        "ec2_t3_micro": 0.0084,
        "ec2_t3_small": 0.0208,
        "s3_standard": 0.023,
        "rds_mysql": 0.017
    },
    "azure": {
        "compute_per_hour": 0.05,
        "storage_per_gb_monthly": 0.02,
        "bandwidth_per_gb": 0.087
    },
    "aws": {
        "ec2_per_hour": 0.04,
        "s3_per_gb_monthly": 0.023,
        "bandwidth_per_gb": 0.09
    },
    "adobe": {
        "creative_suite_per_user_monthly": 52.99,
        "acrobat_pro_per_user_monthly": 14.99
    },
    "vmware": {
        "vsphere_per_cpu": 1000.0,
        "vcenter_per_instance": 5000.0
    }
}

# Analysis Thresholds
ANALYSIS_THRESHOLDS = {
    "cost_variance_warning": 0.15,  # 15% above standard triggers warning
    "cost_variance_critical": 0.30,  # 30% above standard triggers critical alert
    "usage_efficiency_warning": 0.70,  # Below 70% usage efficiency triggers warning
    "license_utilization_warning": 0.80,  # Below 80% license utilization triggers warning
    "renewal_reminder_days": 90,  # Days before renewal to send reminder
    "cost_trend_analysis_months": 12  # Months to analyze for cost trends
}

# Output Configuration
OUTPUT_CONFIG = {
    "reports_dir": "reports",
    "charts_dir": "charts",
    "excel_dir": "excel",
    "pdf_dir": "pdf",
    "cache_dir": "cache",
    "log_dir": "logs"
}

# API Configuration
API_CONFIG = {
    "rate_limit_delay_seconds": 2,  # Reduced for efficiency
    "max_retries": 1,  # Only 1 retry to minimize costs
    "timeout_seconds": 60,  # Reduced timeout
    "batch_size": 5,  # Smaller batch size to avoid JSON parsing issues
    "requests_per_minute": 30,  # Increased since we're using smaller batches
    "max_concurrent_requests": 1  # Process one at a time to avoid rate limits
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
    "file": "licensing_analysis.log",
    "max_file_size_mb": 10,
    "backup_count": 5
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration dictionary."""
    return {
        "claude_opus_4": CLAUDE_OPUS_4_CONFIG,
        "cache": CACHE_CONFIG,
        "categories": LICENSING_CATEGORIES,
        "standards": INDUSTRY_STANDARDS,
        "thresholds": ANALYSIS_THRESHOLDS,
        "output": OUTPUT_CONFIG,
        "api": API_CONFIG,
        "logging": LOGGING_CONFIG
    }

def get_api_key() -> str:
    """Get API key from environment variable or use default."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    # If environment variable is set to placeholder, ignore it
    if api_key == "your_api_key_here":
        api_key = None
    
    if not api_key:
        # Use placeholder - users should set their own API key
        api_key = "your_anthropic_api_key_here"
    return api_key

def create_directories():
    """Create necessary directories for the project."""
    directories = [
        OUTPUT_CONFIG["reports_dir"],
        OUTPUT_CONFIG["charts_dir"],
        OUTPUT_CONFIG["excel_dir"],
        OUTPUT_CONFIG["pdf_dir"],
        OUTPUT_CONFIG["cache_dir"],
        OUTPUT_CONFIG["log_dir"]
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True) 