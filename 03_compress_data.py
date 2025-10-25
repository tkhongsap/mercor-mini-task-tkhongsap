#!/usr/bin/env python3
"""
JSON Compression Script - Airtable Contractor Application System

Reads data from 3 child tables (Personal Details, Work Experience, Salary Preferences),
builds a single JSON object, and writes it to the Compressed JSON field in Applicants table.

Usage:
    python compress_data.py                 # Process all applicants
    python compress_data.py --id <record_id> # Process single applicant
    python compress_data.py --help           # Show help
"""

import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv
from pyairtable import Api

def compress_applicant_data(api, base_id, applicant_record):
    """
    Compress data from child tables into JSON for a single applicant.

    Args:
        api: Pyairtable API instance
        base_id: Airtable base ID
        applicant_record: Applicants table record dict

    Returns:
        dict: Compressed JSON data or None if missing required data
    """
    base = api.base(base_id)
    applicant_id = applicant_record['id']
    applicant_fields = applicant_record['fields']

    # Get table references
    personal_details_table = base.table("Personal Details")
    work_experience_table = base.table("Work Experience")
    salary_preferences_table = base.table("Salary Preferences")

    try:
        # Get Personal Details (one-to-one relationship)
        # Get all records and filter in Python (more reliable than formulas)
        all_personal = personal_details_table.all()
        personal_records = [r for r in all_personal if applicant_id in r['fields'].get('Applicant ID', [])]

        if not personal_records:
            print(f"  Warning: No Personal Details found for applicant {applicant_id}")
            return None

        personal_data = personal_records[0]['fields']

        # Get Work Experience (one-to-many relationship)
        all_work = work_experience_table.all()
        work_records = [r for r in all_work if applicant_id in r['fields'].get('Applicant ID', [])]

        if not work_records:
            print(f"  Warning: No Work Experience found for applicant {applicant_id}")
            return None

        # Get Salary Preferences (one-to-one relationship)
        all_salary = salary_preferences_table.all()
        salary_records = [r for r in all_salary if applicant_id in r['fields'].get('Applicant ID', [])]

        if not salary_records:
            print(f"  Warning: No Salary Preferences found for applicant {applicant_id}")
            return None

        salary_data = salary_records[0]['fields']

        # Build JSON structure per PRD specification
        compressed_json = {
            "personal": {
                "name": personal_data.get("Full Name", ""),
                "email": personal_data.get("Email", ""),
                "location": personal_data.get("Location", ""),
                "linkedin": personal_data.get("LinkedIn", "")
            },
            "experience": [
                {
                    "company": work['fields'].get("Company", ""),
                    "title": work['fields'].get("Title", ""),
                    "start": work['fields'].get("Start", ""),
                    "end": work['fields'].get("End", ""),
                    "technologies": work['fields'].get("Technologies", "")
                }
                for work in work_records
            ],
            "salary": {
                "preferred_rate": salary_data.get("Preferred Rate", 0),
                "minimum_rate": salary_data.get("Minimum Rate", 0),
                "currency": salary_data.get("Currency", "USD"),
                "availability": salary_data.get("Availability (hrs/wk)", 0)
            }
        }

        return compressed_json

    except Exception as e:
        print(f"  ERROR: Failed to compress data for applicant {applicant_id}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description="Compress applicant data from child tables into JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compress_data.py              Process all applicants
  python compress_data.py --id rec123  Process single applicant
        """
    )
    parser.add_argument(
        '--id',
        type=str,
        help='Specific applicant record ID to process (e.g., rec123...)'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("JSON Compression - Contractor Application System")
    print("=" * 70)
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
        applicants_table = base.table("Applicants")
        print(f"✓ Connected to base")
        print()
    except Exception as e:
        print(f"ERROR: Failed to connect to Airtable: {e}")
        sys.exit(1)

    # Get applicants to process
    if args.id:
        print(f"Processing single applicant: {args.id}")
        print()
        try:
            applicant_record = applicants_table.get(args.id)
            applicants_to_process = [applicant_record]
        except Exception as e:
            print(f"ERROR: Failed to get applicant {args.id}: {e}")
            sys.exit(1)
    else:
        print("Processing all applicants...")
        print()
        try:
            applicants_to_process = applicants_table.all()
        except Exception as e:
            print(f"ERROR: Failed to get applicants: {e}")
            sys.exit(1)

    print("=" * 70)
    print("Compressing Applicant Data")
    print("=" * 70)
    print()

    success_count = 0
    skip_count = 0
    error_count = 0

    for idx, applicant_record in enumerate(applicants_to_process, 1):
        applicant_id = applicant_record['id']
        applicant_fields = applicant_record['fields']

        # Get applicant name from linked Personal Details if available
        applicant_name = applicant_fields.get('Personal Details', ['Unknown'])[0] if 'Personal Details' in applicant_fields else 'Unknown'

        print(f"[{idx}/{len(applicants_to_process)}] Processing applicant {applicant_id}...")

        # Compress data
        compressed_json = compress_applicant_data(api, base_id, applicant_record)

        if compressed_json is None:
            print(f"  ✗ Skipped (missing required data)")
            skip_count += 1
            print()
            continue

        # Write compressed JSON to Applicants table
        try:
            json_string = json.dumps(compressed_json, indent=2)
            applicants_table.update(applicant_id, {
                "Compressed JSON": json_string
            })
            print(f"  ✓ Compressed JSON written ({len(json_string)} characters)")
            print(f"  ✓ Personal: {compressed_json['personal']['name']}")
            print(f"  ✓ Experience: {len(compressed_json['experience'])} job(s)")
            print(f"  ✓ Salary: ${compressed_json['salary']['preferred_rate']}/hr, {compressed_json['salary']['availability']} hrs/wk")
            success_count += 1
        except Exception as e:
            print(f"  ERROR: Failed to write JSON: {e}")
            error_count += 1

        print()

    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total applicants processed: {len(applicants_to_process)}")
    print(f"Successfully compressed: {success_count}")
    print(f"Skipped (missing data): {skip_count}")
    print(f"Errors: {error_count}")
    print()

    if success_count > 0:
        print("Next steps:")
        print("  1. View compressed JSON in Airtable: https://airtable.com/{base_id}")
        print("  2. Run shortlist_evaluator.py to evaluate candidates")
        print("  3. Run llm_evaluator.py to enrich with LLM analysis")
        print()

if __name__ == "__main__":
    main()
