"""
Configuration management for Airtable Contractor Application System.
Loads and validates environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class that loads and validates environment variables."""
    
    def __init__(self):
        """Initialize configuration and validate required environment variables."""
        self.airtable_pat = self._get_required_env("AIRTABLE_PAT")
        self.airtable_base_id = self._get_required_env("AIRTABLE_BASE_ID")
        self.openai_api_key = self._get_required_env("OPENAI_API_KEY")
        
        # Table names (with defaults)
        self.applicants_table = os.getenv("APPLICANTS_TABLE", "Applicants")
        self.personal_details_table = os.getenv("PERSONAL_DETAILS_TABLE", "Personal Details")
        self.work_experience_table = os.getenv("WORK_EXPERIENCE_TABLE", "Work Experience")
        self.salary_preferences_table = os.getenv("SALARY_PREFERENCES_TABLE", "Salary Preferences")
        self.shortlisted_leads_table = os.getenv("SHORTLISTED_LEADS_TABLE", "Shortlisted Leads")
        
        self._validate_config()
    
    def _get_required_env(self, key):
        """
        Get required environment variable or raise error.
        
        Args:
            key: Environment variable name
            
        Returns:
            str: Environment variable value
            
        Raises:
            ValueError: If environment variable is not set
        """
        value = os.getenv(key)
        if not value:
            raise ValueError(
                f"Required environment variable '{key}' is not set. "
                f"Please create a .env file with this variable. "
                f"See env.template for template."
            )
        return value
    
    def _validate_config(self):
        """Validate configuration values."""
        # Validate Airtable Base ID format
        if not self.airtable_base_id.startswith("app"):
            raise ValueError(
                f"Invalid AIRTABLE_BASE_ID format: {self.airtable_base_id}. "
                f"Base ID should start with 'app'"
            )
        
        # Validate Personal Access Token format (basic check)
        if len(self.airtable_pat) < 20:
            raise ValueError(
                "Invalid AIRTABLE_PAT format. "
                "Personal Access Token should be a long string."
            )
        
        # Validate OpenAI API Key format
        if not self.openai_api_key.startswith("sk-"):
            raise ValueError(
                f"Invalid OPENAI_API_KEY format. "
                f"API key should start with 'sk-'"
            )
    
    def __repr__(self):
        """Return string representation (without exposing secrets)."""
        return (
            f"Config("
            f"base_id={self.airtable_base_id}, "
            f"applicants_table={self.applicants_table}, "
            f"personal_details_table={self.personal_details_table}, "
            f"work_experience_table={self.work_experience_table}, "
            f"salary_preferences_table={self.salary_preferences_table}, "
            f"shortlisted_leads_table={self.shortlisted_leads_table}"
            f")"
        )


# Global config instance
config = None


def get_config():
    """
    Get or create global configuration instance.
    
    Returns:
        Config: Configuration instance
    """
    global config
    if config is None:
        config = Config()
    return config

