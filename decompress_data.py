#!/usr/bin/env python3
"""
JSON Decompression Script - Airtable Contractor Application System

Reads Compressed JSON from Applicants table and decompresses it back into
the normalized child tables (Personal Details, Work Experience, Salary Preferences).

This enables bulk editing via JSON followed by syncing changes back to Airtable.

Usage:
    python decompress_data.py                  # Decompress all applicants
    python decompress_data.py --id <id>        # Decompress single applicant
    python decompress_data.py --dry-run        # Preview changes without applying
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pyairtable import Api


def find_existing_record(table, applicant_id: str, field_name: str = "Applicant ID") -> Optional[str]:
    """
    Find existing record linked to this applicant.

    Args:
        table: Airtable table instance
        applicant_id: Applicant record ID
        field_name: Name of the link field

    Returns:
        Record ID if found, None otherwise
    """
    try:
        all_records = table.all()
        for record in all_records:
            linked_ids = record['fields'].get(field_name, [])
            if applicant_id in linked_ids:
                return record['id']
    except Exception as e:
        print(f"      Warning: Error finding existing record: {e}")

    return None


def decompress_personal_details(
    table,
    applicant_id: str,
    personal_data: Dict,
    dry_run: bool = False
) -> bool:
    """
    Upsert Personal Details record (one-to-one relationship).

    Args:
        table: Personal Details table
        applicant_id: Applicant record ID
        personal_data: Personal data from JSON
        dry_run: If True, preview without applying

    Returns:
        True if successful, False otherwise
    """
    try:
        fields = {
            "Full Name": personal_data.get("name", ""),
            "Email": personal_data.get("email", ""),
            "Location": personal_data.get("location", ""),
            "LinkedIn": personal_data.get("linkedin", ""),
            "Applicant ID": [applicant_id]
        }

        # Check if record exists
        existing_id = find_existing_record(table, applicant_id)

        if dry_run:
            if existing_id:
                print(f"      [DRY RUN] Would UPDATE Personal Details record {existing_id}")
            else:
                print(f"      [DRY RUN] Would CREATE new Personal Details record")
            print(f"        Fields: {json.dumps(fields, indent=10)}")
            return True

        if existing_id:
            # Update existing record
            table.update(existing_id, fields)
            print(f"      ✓ Updated Personal Details ({existing_id})")
        else:
            # Create new record
            new_record = table.create(fields)
            print(f"      ✓ Created Personal Details ({new_record['id']})")

        return True

    except Exception as e:
        print(f"      ✗ Error with Personal Details: {e}")
        return False


def decompress_work_experience(
    table,
    applicant_id: str,
    experience_data: List[Dict],
    dry_run: bool = False
) -> bool:
    """
    Replace Work Experience records (one-to-many relationship).
    Deletes all existing records, then creates new ones from JSON.

    Args:
        table: Work Experience table
        applicant_id: Applicant record ID
        experience_data: List of work experience entries from JSON
        dry_run: If True, preview without applying

    Returns:
        True if successful, False otherwise
    """
    try:
        # Find all existing Work Experience records for this applicant
        all_records = table.all()
        existing_records = [
            r for r in all_records
            if applicant_id in r['fields'].get('Applicant ID', [])
        ]

        if dry_run:
            print(f"      [DRY RUN] Would DELETE {len(existing_records)} existing Work Experience record(s)")
            print(f"      [DRY RUN] Would CREATE {len(experience_data)} new Work Experience record(s)")
            for exp in experience_data:
                print(f"        - {exp.get('company')} ({exp.get('title')})")
            return True

        # Delete existing records
        for record in existing_records:
            table.delete(record['id'])
        print(f"      ✓ Deleted {len(existing_records)} existing Work Experience record(s)")

        # Create new records from JSON
        created_count = 0
        for exp in experience_data:
            fields = {
                "Company": exp.get("company", ""),
                "Title": exp.get("title", ""),
                "Start": exp.get("start", ""),
                "End": exp.get("end", ""),
                "Technologies": exp.get("technologies", ""),
                "Applicant ID": [applicant_id]
            }
            table.create(fields)
            created_count += 1

        print(f"      ✓ Created {created_count} new Work Experience record(s)")
        return True

    except Exception as e:
        print(f"      ✗ Error with Work Experience: {e}")
        return False


def decompress_salary_preferences(
    table,
    applicant_id: str,
    salary_data: Dict,
    dry_run: bool = False
) -> bool:
    """
    Upsert Salary Preferences record (one-to-one relationship).

    Args:
        table: Salary Preferences table
        applicant_id: Applicant record ID
        salary_data: Salary data from JSON
        dry_run: If True, preview without applying

    Returns:
        True if successful, False otherwise
    """
    try:
        fields = {
            "Preferred Rate": salary_data.get("preferred_rate", 0),
            "Minimum Rate": salary_data.get("minimum_rate", 0),
            "Currency": salary_data.get("currency", "USD"),
            "Availability (hrs/wk)": salary_data.get("availability", 0),
            "Applicant ID": [applicant_id]
        }

        # Check if record exists
        existing_id = find_existing_record(table, applicant_id)

        if dry_run:
            if existing_id:
                print(f"      [DRY RUN] Would UPDATE Salary Preferences record {existing_id}")
            else:
                print(f"      [DRY RUN] Would CREATE new Salary Preferences record")
            print(f"        Fields: {json.dumps(fields, indent=10)}")
            return True

        if existing_id:
            # Update existing record
            table.update(existing_id, fields)
            print(f"      ✓ Updated Salary Preferences ({existing_id})")
        else:
            # Create new record
            new_record = table.create(fields)
            print(f"      ✓ Created Salary Preferences ({new_record['id']})")

        return True

    except Exception as e:
        print(f"      ✗ Error with Salary Preferences: {e}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Decompress JSON back to normalized Airtable tables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python decompress_data.py              Decompress all applicants
  python decompress_data.py --id rec123  Decompress single applicant
  python decompress_data.py --dry-run    Preview changes without applying
        """
    )
    parser.add_argument(
        '--id',
        type=str,
        help='Specific applicant record ID to process'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("JSON Decompression - Contractor Application System")
    print("=" * 70)
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
    print()

    # Load environment variables
    print("Loading credentials...")
    load_dotenv()

    pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID')

    if not pat or not base_id:
        print("ERROR: Missing credentials in .env file")
        sys.exit(1)

    print(f"✓ Connected to base: {base_id}")
    print()

    # Connect to Airtable
    try:
        api = Api(pat)
        base = api.base(base_id)
        applicants_table = base.table("Applicants")
        personal_details_table = base.table("Personal Details")
        work_experience_table = base.table("Work Experience")
        salary_preferences_table = base.table("Salary Preferences")
    except Exception as e:
        print(f"ERROR: Failed to connect: {e}")
        sys.exit(1)

    # Get applicants to process
    if args.id:
        print(f"Processing single applicant: {args.id}")
        print()
        try:
            applicant = applicants_table.get(args.id)
            applicants = [applicant]
        except Exception as e:
            print(f"ERROR: Failed to get applicant {args.id}: {e}")
            sys.exit(1)
    else:
        print("Processing all applicants...")
        print()
        try:
            applicants = applicants_table.all()
        except Exception as e:
            print(f"ERROR: Failed to get applicants: {e}")
            sys.exit(1)

    print("=" * 70)
    print("Decompression Results")
    print("=" * 70)
    print()

    success_count = 0
    skip_count = 0
    error_count = 0

    for idx, applicant in enumerate(applicants, 1):
        applicant_id = applicant['id']
        fields = applicant['fields']

        # Get compressed JSON
        compressed_json_str = fields.get('Compressed JSON', '')
        if not compressed_json_str:
            print(f"[{idx}/{len(applicants)}] {applicant_id}: Skipped (no compressed JSON)")
            skip_count += 1
            print()
            continue

        try:
            # Parse JSON
            applicant_data = json.loads(compressed_json_str)
            name = applicant_data.get('personal', {}).get('name', 'Unknown')

            print(f"[{idx}/{len(applicants)}] {name} ({applicant_id}):")

            # Decompress to child tables
            personal_success = decompress_personal_details(
                personal_details_table,
                applicant_id,
                applicant_data.get('personal', {}),
                args.dry_run
            )

            work_success = decompress_work_experience(
                work_experience_table,
                applicant_id,
                applicant_data.get('experience', []),
                args.dry_run
            )

            salary_success = decompress_salary_preferences(
                salary_preferences_table,
                applicant_id,
                applicant_data.get('salary', {}),
                args.dry_run
            )

            if personal_success and work_success and salary_success:
                print(f"  ✓ Decompression complete")
                success_count += 1
            else:
                print(f"  ⚠ Partial success (some operations failed)")
                error_count += 1

        except json.JSONDecodeError as e:
            print(f"  ERROR: Invalid JSON: {e}")
            error_count += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            error_count += 1

        print()

    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total applicants processed: {len(applicants)}")
    print(f"✓ Successfully decompressed: {success_count}")
    print(f"→ Skipped (no JSON): {skip_count}")
    print(f"✗ Errors: {error_count}")
    print()

    if args.dry_run:
        print("NOTE: This was a dry run. No actual changes were made.")
        print("Run without --dry-run to apply changes.")
    elif success_count > 0:
        print("Next steps:")
        print("  1. Verify data in Airtable: https://airtable.com/{base_id}")
        print("  2. Check Personal Details, Work Experience, and Salary Preferences tables")
        print("  3. Run compress_data.py to regenerate JSON if needed")
    print()


if __name__ == "__main__":
    main()
