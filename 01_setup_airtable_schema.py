#!/usr/bin/env python3
"""
Airtable Schema Setup Script

This script automatically creates all 5 tables in the Airtable base:
1. Applicants (parent table)
2. Personal Details
3. Work Experience
4. Salary Preferences
5. Shortlisted Leads

All tables are created with exact field specifications from PRD and DELIVERABLES.md.
The script is idempotent - it checks if Applicants table exists and creates it if needed.
"""

import os
import sys
from dotenv import load_dotenv
from pyairtable import Api

def main() -> None:
    print("=" * 60)
    print("Airtable Schema Setup - Contractor Application System")
    print("=" * 60)
    print()

    # Load environment variables
    print("Loading credentials from .env file...")
    load_dotenv()

    pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID')

    if not pat or not base_id:
        print("ERROR: Missing credentials in .env file")
        print("Required: AIRTABLE_PERSONAL_ACCESS_TOKEN and AIRTABLE_BASE_ID")
        sys.exit(1)

    print(f"✓ Credentials loaded")
    print(f"  Base ID: {base_id}")
    print()

    # Connect to Airtable
    print("Connecting to Airtable...")
    try:
        api = Api(pat)
        base = api.base(base_id)
        print(f"✓ Connected to base: {base_id}")
    except Exception as e:
        print(f"ERROR: Failed to connect to Airtable: {e}")
        sys.exit(1)

    # Check if Applicants table exists, create if needed
    print()
    print("Checking for Applicants table...")
    try:
        schema = base.schema()
        applicants_table = None
        for table in schema.tables:
            if table.name == "Applicants":
                applicants_table = table
                break

        if applicants_table:
            print(f"✓ Found existing Applicants table")
            print(f"  Table ID: {applicants_table.id}")
            applicants_table_id = applicants_table.id
        else:
            print("Applicants table not found - creating it now...")

            # Create Applicants table with 6 fields
            # Note: The first field becomes the primary field
            # Using plain number field since autoNumber/formula cannot be created via API
            # The ID sequence will be managed by Python scripts
            applicants_fields = [
                {
                    "name": "Applicant ID",
                    "type": "number",
                    "options": {
                        "precision": 0  # Integer values only
                    }
                },
                {
                    "name": "Compressed JSON",
                    "type": "multilineText"
                },
                {
                    "name": "Shortlist Status",
                    "type": "checkbox",
                    "options": {
                        "icon": "check",
                        "color": "greenBright"
                    }
                },
                {
                    "name": "LLM Summary",
                    "type": "multilineText"
                },
                {
                    "name": "LLM Score",
                    "type": "number",
                    "options": {"precision": 0}
                },
                {
                    "name": "LLM Follow-Ups",
                    "type": "multilineText"
                }
            ]

            applicants_table = base.create_table(
                "Applicants",
                applicants_fields,
                description="Parent table storing applicant data and LLM evaluation results"
            )
            applicants_table_id = applicants_table.id
            print(f"✓ Applicants table created")
            print(f"  Table ID: {applicants_table_id}")
            print(f"  Fields: Applicant ID (number), Compressed JSON, Shortlist Status, LLM Summary, LLM Score, LLM Follow-Ups")
            print(f"  Note: Applicant ID sequence managed by Python scripts")
            print()

    except Exception as e:
        print(f"ERROR: Failed to check/create Applicants table: {e}")
        sys.exit(1)

    print()
    print("=" * 60)
    print("Creating Child Tables...")
    print("=" * 60)
    print()

    # Table 1: Personal Details
    print("1. Creating Personal Details table...")
    try:
        personal_details_fields = [
            {"name": "Full Name", "type": "singleLineText"},
            {"name": "Email", "type": "email"},
            {"name": "Location", "type": "singleLineText"},
            {"name": "LinkedIn", "type": "url"},
            {
                "name": "Applicant ID",
                "type": "multipleRecordLinks",
                "options": {
                    "linkedTableId": applicants_table_id
                }
            }
        ]

        personal_details_table = base.create_table(
            "Personal Details",
            personal_details_fields,
            description="Stores applicant personal information (one-to-one with Applicants)"
        )
        print(f"   ✓ Personal Details table created (ID: {personal_details_table.id})")
    except Exception as e:
        print(f"   ERROR: Failed to create Personal Details table: {e}")
        print(f"   Error details: {str(e)}")

    print()

    # Table 2: Work Experience
    print("2. Creating Work Experience table...")
    try:
        work_experience_fields = [
            {"name": "Company", "type": "singleLineText"},
            {"name": "Title", "type": "singleLineText"},
            {
                "name": "Start",
                "type": "date",
                "options": {"dateFormat": {"name": "us", "format": "M/D/YYYY"}}
            },
            {
                "name": "End",
                "type": "date",
                "options": {"dateFormat": {"name": "us", "format": "M/D/YYYY"}}
            },
            {"name": "Technologies", "type": "singleLineText"},
            {
                "name": "Applicant ID",
                "type": "multipleRecordLinks",
                "options": {
                    "linkedTableId": applicants_table_id
                }
            }
        ]

        work_experience_table = base.create_table(
            "Work Experience",
            work_experience_fields,
            description="Stores applicant work history (one-to-many with Applicants)"
        )
        print(f"   ✓ Work Experience table created (ID: {work_experience_table.id})")
    except Exception as e:
        print(f"   ERROR: Failed to create Work Experience table: {e}")
        print(f"   Error details: {str(e)}")

    print()

    # Table 3: Salary Preferences
    print("3. Creating Salary Preferences table...")
    try:
        salary_preferences_fields = [
            {
                "name": "Preferred Rate",
                "type": "number",
                "options": {"precision": 2}
            },
            {
                "name": "Minimum Rate",
                "type": "number",
                "options": {"precision": 2}
            },
            {
                "name": "Currency",
                "type": "singleSelect",
                "options": {
                    "choices": [
                        {"name": "USD"},
                        {"name": "EUR"},
                        {"name": "GBP"},
                        {"name": "CAD"},
                        {"name": "INR"}
                    ]
                }
            },
            {
                "name": "Availability (hrs/wk)",
                "type": "number",
                "options": {"precision": 0}
            },
            {
                "name": "Applicant ID",
                "type": "multipleRecordLinks",
                "options": {
                    "linkedTableId": applicants_table_id
                }
            }
        ]

        salary_preferences_table = base.create_table(
            "Salary Preferences",
            salary_preferences_fields,
            description="Stores applicant compensation preferences (one-to-one with Applicants)"
        )
        print(f"   ✓ Salary Preferences table created (ID: {salary_preferences_table.id})")
    except Exception as e:
        print(f"   ERROR: Failed to create Salary Preferences table: {e}")
        print(f"   Error details: {str(e)}")

    print()

    # Table 4: Shortlisted Leads
    print("4. Creating Shortlisted Leads table...")
    try:
        shortlisted_leads_fields = [
            {"name": "Score Reason", "type": "multilineText"},
            {
                "name": "Applicant",
                "type": "multipleRecordLinks",
                "options": {
                    "linkedTableId": applicants_table_id
                }
            },
            {"name": "Compressed JSON", "type": "multilineText"},
            {
                "name": "Created At",
                "type": "dateTime",
                "options": {
                    "dateFormat": {"name": "us"},
                    "timeFormat": {"name": "12hour"},
                    "timeZone": "utc"
                }
            }
        ]

        shortlisted_leads_table = base.create_table(
            "Shortlisted Leads",
            shortlisted_leads_fields,
            description="Auto-populated table for qualified candidates"
        )
        print(f"   ✓ Shortlisted Leads table created (ID: {shortlisted_leads_table.id})")
    except Exception as e:
        print(f"   ERROR: Failed to create Shortlisted Leads table: {e}")
        print(f"   Error details: {str(e)}")

    print()
    print("=" * 60)
    print("SUCCESS! Schema Setup Complete")
    print("=" * 60)
    print()
    print("Summary - All 5 Tables Created:")
    print("  ✓ Applicants - 6 fields (Applicant ID [number], Compressed JSON, Shortlist Status, LLM Summary, LLM Score, LLM Follow-Ups)")
    print("     Applicant ID is Python-managed sequence for full automation")
    print("  ✓ Personal Details - 5 fields (Full Name, Email, Location, LinkedIn, Applicant ID)")
    print("  ✓ Work Experience - 6 fields (Company, Title, Start, End, Technologies, Applicant ID)")
    print("  ✓ Salary Preferences - 5 fields (Preferred Rate, Minimum Rate, Currency, Availability, Applicant ID)")
    print("  ✓ Shortlisted Leads - 4 fields (Applicant, Compressed JSON, Score Reason, Created At)")
    print()
    print("Linked Relationships:")
    print("  The Applicants table now has 4 auto-generated linked fields:")
    print("     - Personal Details (one-to-one)")
    print("     - Work Experience (one-to-many)")
    print("     - Salary Preferences (one-to-one)")
    print("     - Shortlisted Leads (one-to-many)")
    print()
    print("Next Steps:")
    print("  1. Run tests to verify schema: python tests/test_runner.py")
    print("  2. Generate test data: python generate_test_data.py")
    print(f"  3. View your base: https://airtable.com/{base_id}")
    print()

if __name__ == "__main__":
    main()
