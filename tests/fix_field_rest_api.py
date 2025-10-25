#!/usr/bin/env python3
"""
Fix the Applicants table field capitalization using direct REST API
Rename "LLM Follow-ups" to "LLM Follow-Ups"
"""

import os
import requests
from dotenv import load_dotenv
from pyairtable import Api

def main():
    print("=" * 60)
    print("Fixing Applicants Table Field Capitalization")
    print("=" * 60)
    print()

    load_dotenv()
    pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID')

    # First, get the schema to find the field ID
    api = Api(pat)
    base = api.base(base_id)

    print("Fetching base schema...")
    schema = base.schema()

    # Find Applicants table
    applicants_table = None
    for table in schema.tables:
        if table.name == "Applicants":
            applicants_table = table
            break

    if not applicants_table:
        print("ERROR: Applicants table not found!")
        return

    print(f"Found Applicants table (ID: {applicants_table.id})")
    print()

    # Find the field that needs renaming
    field_to_rename = None
    for field in applicants_table.fields:
        if field.name == "LLM Follow-ups":
            field_to_rename = field
            break

    if not field_to_rename:
        print("Field 'LLM Follow-ups' not found. Checking if already correct...")
        # Check if it's already correct
        for field in applicants_table.fields:
            if field.name == "LLM Follow-Ups":
                print("SUCCESS! Field already has correct capitalization!")
                return
        print("ERROR: Could not find field to rename")
        return

    print(f"Found field: '{field_to_rename.name}' (ID: {field_to_rename.id})")
    print(f"Field type: {field_to_rename.type}")
    print()

    # Use REST API to update the field
    print("Renaming to: 'LLM Follow-Ups' using REST API...")

    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{applicants_table.id}/fields/{field_to_rename.id}"

    headers = {
        "Authorization": f"Bearer {pat}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": "LLM Follow-Ups"
    }

    try:
        response = requests.patch(url, json=payload, headers=headers)
        response.raise_for_status()
        print("SUCCESS! Field renamed")
        print(f"Response: {response.json()}")
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: Failed to rename field: {e}")
        print(f"Response: {response.text}")
        return
    except Exception as e:
        print(f"ERROR: {e}")
        return

    print()
    print("=" * 60)
    print("Verification")
    print("=" * 60)
    print()

    # Re-fetch schema to verify
    print("Re-fetching schema to verify change...")
    updated_schema = base.schema()
    updated_applicants = None
    for table in updated_schema.tables:
        if table.name == "Applicants":
            updated_applicants = table
            break

    if updated_applicants:
        print("Applicants table fields with 'Follow' in name:")
        for field in updated_applicants.fields:
            if "Follow" in field.name:
                print(f"  -> {field.name}")

    print()
    print("=" * 60)
    print("COMPLETE! Run verify_prd_schema.py to confirm all tables match PRD")
    print("=" * 60)

if __name__ == "__main__":
    main()
