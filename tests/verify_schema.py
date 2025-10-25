#!/usr/bin/env python3
"""
Verify that all tables were created with correct schema and relationships
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

def main():
    print("=" * 60)
    print("Airtable Schema Verification")
    print("=" * 60)
    print()

    load_dotenv()
    pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID')

    api = Api(pat)
    base = api.base(base_id)

    print("Fetching base schema...")
    schema = base.schema()
    print(f"Found {len(schema.tables)} tables")
    print()

    expected_tables = {
        "Applicants": ["Email", "Application Status", "Resume Link", "Phone", "Preferred Role", "Compressed JSON"],
        "Personal Details": ["Full Name", "Email", "Location", "LinkedIn", "Applicant ID"],
        "Work Experience": ["Company", "Title", "Start", "End", "Technologies", "Applicant ID"],
        "Salary Preferences": ["Preferred Rate", "Minimum Rate", "Currency", "Availability (hrs/wk)", "Applicant ID"],
        "Shortlisted Leads": ["Score Reason", "Applicant", "Compressed JSON", "Created At"]
    }

    print("=" * 60)
    print("Table Verification")
    print("=" * 60)
    print()

    all_correct = True

    for table in schema.tables:
        if table.name in expected_tables:
            print(f"Table: {table.name}")
            print(f"  ID: {table.id}")
            print(f"  Fields ({len(table.fields)}):")

            expected_fields = expected_tables[table.name]
            actual_field_names = [f.name for f in table.fields]

            for i, field in enumerate(table.fields, 1):
                field_type = field.type
                if hasattr(field, 'options') and field.options:
                    if hasattr(field.options, 'linkedTableId'):
                        field_type += f" -> {field.options.linkedTableId}"

                status = "✓" if field.name in expected_fields else "✗"
                print(f"    {status} {i}. {field.name} ({field_type})")

            # Check for missing fields
            missing = set(expected_fields) - set(actual_field_names)
            if missing:
                print(f"  MISSING FIELDS: {missing}")
                all_correct = False

            print()

    print("=" * 60)
    print("Linked Relationships Check")
    print("=" * 60)
    print()

    # Find Applicants table
    applicants_table = None
    for table in schema.tables:
        if table.name == "Applicants":
            applicants_table = table
            break

    if applicants_table:
        print("Checking Applicants table for linked record fields...")
        linked_fields = [f for f in applicants_table.fields if f.type == "multipleRecordLinks"]

        print(f"Found {len(linked_fields)} linked record fields:")
        for field in linked_fields:
            print(f"  ✓ {field.name}")

        expected_links = ["Personal Details", "Work Experience", "Salary Preferences", "Shortlisted Leads"]
        actual_links = [f.name for f in linked_fields]

        missing_links = set(expected_links) - set(actual_links)
        if missing_links:
            print(f"\nMISSING LINKS: {missing_links}")
            all_correct = False
        else:
            print("\nAll expected linked fields are present!")

    print()
    print("=" * 60)
    if all_correct:
        print("SUCCESS! Schema verification complete - all tables correct")
    else:
        print("ERRORS FOUND - Please review missing fields/links above")
    print("=" * 60)
    print()
    print(f"View your base: https://airtable.com/{base_id}")

if __name__ == "__main__":
    main()
