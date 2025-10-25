#!/usr/bin/env python3
"""
Create only the Shortlisted Leads table
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

def main():
    print("Creating Shortlisted Leads table...")
    print()

    load_dotenv()
    pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID')

    api = Api(pat)
    base = api.base(base_id)

    # Get Applicants table ID
    schema = base.schema()
    applicants_table_id = None
    for table in schema.tables:
        if table.name == "Applicants":
            applicants_table_id = table.id
            break

    print(f"Applicants table ID: {applicants_table_id}")
    print()

    # Create Shortlisted Leads table
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
        print(f"SUCCESS! Shortlisted Leads table created (ID: {shortlisted_leads_table.id})")
    except Exception as e:
        print(f"ERROR: Failed to create Shortlisted Leads table")
        print(f"Details: {e}")

if __name__ == "__main__":
    main()
