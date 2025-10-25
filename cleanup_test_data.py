#!/usr/bin/env python3
"""
Cleanup Test Data - Delete all records from all tables

This script clears all test data to allow for clean regeneration.
"""

import os
import sys
from dotenv import load_dotenv
from pyairtable import Api

def main() -> None:
    print("=" * 70)
    print("CLEANUP TEST DATA - Delete All Records")
    print("=" * 70)
    print()
    print("WARNING: This will delete ALL records from:")
    print("  - Applicants")
    print("  - Personal Details")
    print("  - Work Experience")
    print("  - Salary Preferences")
    print("  - Shortlisted Leads")
    print()

    confirm = input("Are you sure? Type 'YES' to continue: ")
    if confirm != 'YES':
        print("Cancelled.")
        sys.exit(0)

    print()

    # Load credentials
    load_dotenv()
    pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID')

    if not pat or not base_id:
        print("ERROR: Missing credentials")
        sys.exit(1)

    # Connect
    api = Api(pat)
    base = api.base(base_id)

    tables = [
        "Shortlisted Leads",
        "Salary Preferences",
        "Work Experience",
        "Personal Details",
        "Applicants"
    ]

    for table_name in tables:
        print(f"Deleting all records from {table_name}...")
        table = base.table(table_name)
        records = table.all()

        if records:
            record_ids = [r['id'] for r in records]
            # Airtable allows batch delete of up to 10 records at a time
            for i in range(0, len(record_ids), 10):
                batch = record_ids[i:i+10]
                for record_id in batch:
                    table.delete(record_id)
            print(f"  ✓ Deleted {len(record_ids)} records")
        else:
            print(f"  - No records to delete")

    print()
    print("=" * 70)
    print("CLEANUP COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Run: python generate_test_data.py")
    print("  2. Run: python compress_data.py")
    print("  3. Run: python shortlist_evaluator.py")
    print()

if __name__ == "__main__":
    main()
