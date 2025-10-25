#!/usr/bin/env python3
"""
Verify that all tables match the exact PRD requirements from prd.md
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

def main():
    print("=" * 70)
    print("PRD Schema Verification - Checking Against prd.md Requirements")
    print("=" * 70)
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

    # PRD Requirements from prd.md line 13-21
    prd_requirements = {
        "Applicants": {
            "required_fields": [
                "Applicant ID",
                "Compressed JSON",
                "Shortlist Status",
                "LLM Summary",
                "LLM Score",
                "LLM Follow-Ups"
            ],
            "notes": "Parent table - stores one row per applicant"
        },
        "Personal Details": {
            "required_fields": [
                "Full Name",
                "Email",
                "Location",
                "LinkedIn",
                "Applicant ID"  # Link field
            ],
            "notes": "One-to-one with Applicants"
        },
        "Work Experience": {
            "required_fields": [
                "Company",
                "Title",
                "Start",
                "End",
                "Technologies",
                "Applicant ID"  # Link field
            ],
            "notes": "One-to-many with Applicants"
        },
        "Salary Preferences": {
            "required_fields": [
                "Preferred Rate",
                "Minimum Rate",
                "Currency",
                "Availability (hrs/wk)",
                "Applicant ID"  # Link field
            ],
            "notes": "One-to-one with Applicants"
        },
        "Shortlisted Leads": {
            "required_fields": [
                "Applicant",
                "Compressed JSON",
                "Score Reason",
                "Created At"
            ],
            "notes": "Auto-populated when rules are met"
        }
    }

    print("=" * 70)
    print("Checking Each Table Against PRD Requirements")
    print("=" * 70)
    print()

    all_tables_valid = True
    tables_by_name = {table.name: table for table in schema.tables}

    for table_name, requirements in prd_requirements.items():
        print(f"Table: {table_name}")
        print(f"  PRD Note: {requirements['notes']}")

        if table_name not in tables_by_name:
            print(f"  STATUS: MISSING - Table does not exist!")
            all_tables_valid = False
            print()
            continue

        table = tables_by_name[table_name]
        actual_field_names = [f.name for f in table.fields]
        required_fields = requirements['required_fields']

        print(f"  Table ID: {table.id}")
        print(f"  Required Fields ({len(required_fields)}):")

        all_fields_present = True
        for field_name in required_fields:
            if field_name in actual_field_names:
                # Find the field to get its type
                field_obj = next((f for f in table.fields if f.name == field_name), None)
                field_type = field_obj.type if field_obj else "unknown"
                print(f"    ✓ {field_name} ({field_type})")
            else:
                print(f"    ✗ {field_name} - MISSING!")
                all_fields_present = False
                all_tables_valid = False

        # Check for extra fields (not necessarily a problem, just informational)
        extra_fields = set(actual_field_names) - set(required_fields)
        if extra_fields:
            print(f"  Additional Fields (not in PRD): {', '.join(extra_fields)}")

        if all_fields_present:
            print(f"  STATUS: VALID - All required fields present")
        else:
            print(f"  STATUS: INVALID - Missing required fields")

        print()

    print("=" * 70)
    print("Linked Relationships Verification")
    print("=" * 70)
    print()

    if "Applicants" in tables_by_name:
        applicants = tables_by_name["Applicants"]
        linked_fields = [f for f in applicants.fields if f.type == "multipleRecordLinks"]

        print("Applicants table should have links to:")
        expected_links = ["Personal Details", "Work Experience", "Salary Preferences", "Shortlisted Leads"]

        for expected_link in expected_links:
            matching_field = next((f for f in linked_fields if f.name == expected_link), None)
            if matching_field:
                print(f"  ✓ {expected_link}")
            else:
                print(f"  ✗ {expected_link} - MISSING!")
                all_tables_valid = False

    print()
    print("=" * 70)
    if all_tables_valid:
        print("SUCCESS! All 5 tables match PRD requirements exactly")
        print("=" * 70)
        print()
        print("Schema is ready for:")
        print("  1. Creating Airtable forms for data collection")
        print("  2. Building Python compression/decompression scripts")
        print("  3. Building shortlist evaluator")
        print("  4. Building LLM evaluator")
    else:
        print("VALIDATION FAILED - Schema does not match PRD")
        print("=" * 70)
        print()
        print("Please fix the issues above before proceeding")

    print()
    print(f"View your base: https://airtable.com/{base_id}")
    print()

if __name__ == "__main__":
    main()
