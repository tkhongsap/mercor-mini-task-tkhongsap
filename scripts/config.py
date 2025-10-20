"""
Configuration management for the Mercor Airtable application.
Loads environment variables and defines constants used across the system.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Airtable Configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')

# Anthropic API Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))

# Airtable Table Names
TABLE_APPLICANTS = 'Applicants'
TABLE_PERSONAL_DETAILS = 'Personal Details'
TABLE_WORK_EXPERIENCE = 'Work Experience'
TABLE_SALARY_PREFERENCES = 'Salary Preferences'
TABLE_SHORTLISTED_LEADS = 'Shortlisted Leads'

# Tier-1 Companies for Experience Evaluation
TIER_1_COMPANIES = {
    'Google',
    'Meta',
    'Facebook',  # Include both Meta and Facebook for backward compatibility
    'OpenAI',
    'Microsoft',
    'Amazon',
    'Apple',
    'Netflix',
    'Tesla',
    'SpaceX',
    'Anthropic',
    'DeepMind',
    'Stripe',
    'Airbnb',
    'Uber',
    'LinkedIn',
    'Twitter',
    'X',  # Twitter's new name
    'Salesforce',
    'Oracle',
    'IBM',
    'Intel',
    'NVIDIA',
    'Adobe',
    'Snap',
    'Pinterest',
    'Reddit',
    'Dropbox',
    'Atlassian',
    'Palantir',
    'Databricks',
    'Snowflake',
}

# Shortlisting Criteria
SHORTLIST_CRITERIA = {
    'min_years_experience': 4,
    'max_hourly_rate_usd': 100,
    'min_weekly_hours': 20,
    'valid_locations': {'US', 'USA', 'United States', 'Canada', 'UK', 'United Kingdom', 'Germany', 'India'},
}

# LLM Configuration
LLM_RETRY_ATTEMPTS = 3
LLM_RETRY_DELAY = 1  # Initial delay in seconds for exponential backoff
LLM_SUMMARY_MAX_WORDS = 75

# LLM Prompt Template
LLM_PROMPT_TEMPLATE = """You are a recruiting analyst. Given this JSON applicant profile, do four things:
1. Provide a concise {max_words}-word summary.
2. Rate overall candidate quality from 1-10 (higher is better).
3. List any data gaps or inconsistencies you notice.
4. Suggest up to three follow-up questions to clarify gaps.

Applicant Profile JSON:
{json_data}

Return exactly in this format:
Summary: <text>
Score: <integer>
Issues: <comma-separated list or 'None'>
Follow-Ups: <bullet list>"""


def validate_config():
    """
    Validates that all required configuration variables are set.
    Raises ValueError if any required variables are missing.
    """
    errors = []

    if not AIRTABLE_API_KEY:
        errors.append("AIRTABLE_API_KEY is not set")

    if not AIRTABLE_BASE_ID:
        errors.append("AIRTABLE_BASE_ID is not set")

    if not ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY is not set")

    if errors:
        raise ValueError(
            "Configuration validation failed:\n" +
            "\n".join(f"  - {error}" for error in errors) +
            "\n\nPlease ensure your .env file is properly configured."
        )


def normalize_company_name(company: str) -> str:
    """
    Normalizes company names for comparison with tier-1 list.

    Args:
        company: Raw company name from user input

    Returns:
        Normalized company name
    """
    if not company:
        return ""

    # Convert to title case and strip whitespace
    normalized = company.strip().title()

    # Handle common variations
    variations = {
        'Facebook': 'Meta',
        'Twitter': 'X',
    }

    return variations.get(normalized, normalized)


def normalize_location(location: str) -> str:
    """
    Normalizes location names for comparison with valid locations.

    Args:
        location: Raw location from user input

    Returns:
        Normalized location
    """
    if not location:
        return ""

    # Convert to title case and strip whitespace
    normalized = location.strip().title()

    # Handle common abbreviations and variations
    variations = {
        'Usa': 'US',
        'U.S.': 'US',
        'U.S.A.': 'US',
        'United States Of America': 'United States',
        'Uk': 'UK',
        'U.K.': 'UK',
        'Great Britain': 'United Kingdom',
        'Deutschland': 'Germany',
    }

    return variations.get(normalized, normalized)


if __name__ == '__main__':
    # Test configuration validation
    try:
        validate_config()
        print("Configuration validated successfully!")
        print(f"Base ID: {AIRTABLE_BASE_ID}")
        print(f"Claude Model: {CLAUDE_MODEL}")
        print(f"Max Tokens: {MAX_TOKENS}")
    except ValueError as e:
        print(f"Configuration Error: {e}")
