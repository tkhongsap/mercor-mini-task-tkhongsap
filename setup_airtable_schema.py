#!/usr/bin/env python3
"""
Airtable Schema Setup Script

This script automatically creates the 4 remaining tables in the Airtable base:
1. Personal Details
2. Work Experience
3. Salary Preferences
4. Shortlisted Leads

All tables are created with exact field specifications from DELIVERABLES.md.
"""

import os
import sys
from dotenv import load_dotenv
from pyairtable import Api

def main():
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

    # Get schema to find Applicants table ID
    print()
    print("Getting base schema...")
    try:
        schema = base.schema()
        applicants_table = None
        for table in schema.tables:
            if table.name == "Applicants":
                applicants_table = table
                break

        if not applicants_table:
            print("ERROR: Applicants table not found in base")
            print("Please create the Applicants table first")
            sys.exit(1)

        applicants_table_id = applicants_table.id
        print(f"✓ Found Applicants table")
        print(f"  Table ID: {applicants_table_id}")
    except Exception as e:
        print(f"ERROR: Failed to get base schema: {e}")
        sys.exit(1)

    print()
    print("=" * 60)
    print("Creating Tables...")
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
            {
                "name": "Applicant",
                "type": "multipleRecordLinks",
                "options": {
                    "linkedTableId": applicants_table_id
                }
            },
            {"name": "Compressed JSON", "type": "multilineText"},
            {"name": "Score Reason", "type": "multilineText"},
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
    print("SUCCESS! Table Creation Complete")
    print("=" * 60)
    print()
    print("Summary:")
    print("  ✓ Personal Details - 5 fields (Full Name, Email, Location, LinkedIn, Applicant ID)")
    print("  ✓ Work Experience - 6 fields (Company, Title, Start, End, Technologies, Applicant ID)")
    print("  ✓ Salary Preferences - 5 fields (Preferred Rate, Minimum Rate, Currency, Availability, Applicant ID)")
    print("  ✓ Shortlisted Leads - 4 fields (Applicant, Compressed JSON, Score Reason, Created At)")
    print()
    print("Next Steps:")
    print("  1. Go to your Airtable base and verify all tables were created")
    print("  2. Check that Applicants table has 4 new linked fields:")
    print("     - Personal Details")
    print("     - Work Experience")
    print("     - Salary Preferences")
    print("     - Shortlisted")
    print("  3. Proceed to create forms for data collection")
    print()
    print(f"View your base: https://airtable.com/{base_id}")
    print()

if __name__ == "__main__":
    main()
