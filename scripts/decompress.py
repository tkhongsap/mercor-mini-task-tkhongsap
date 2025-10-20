"""
Decompress JSON data back to normalized Airtable tables.
Upserts records in child tables to match the compressed JSON state.
"""

import json
import argparse
from typing import Dict, List, Optional
from pyairtable import Api

from config import (
    AIRTABLE_API_KEY,
    AIRTABLE_BASE_ID,
    TABLE_APPLICANTS,
    TABLE_PERSONAL_DETAILS,
    TABLE_WORK_EXPERIENCE,
    TABLE_SALARY_PREFERENCES,
    validate_config,
)


class DataDecompressor:
    """Decompresses JSON data back to normalized Airtable tables."""

    def __init__(self):
        """Initialize the decompressor with Airtable connection."""
        validate_config()
        self.api = Api(AIRTABLE_API_KEY)
        self.base = self.api.base(AIRTABLE_BASE_ID)

        # Initialize table connections
        self.applicants_table = self.base.table(TABLE_APPLICANTS)
        self.personal_table = self.base.table(TABLE_PERSONAL_DETAILS)
        self.experience_table = self.base.table(TABLE_WORK_EXPERIENCE)
        self.salary_table = self.base.table(TABLE_SALARY_PREFERENCES)

    def get_existing_linked_records(self, table, link_field: str, applicant_id: str) -> List[Dict]:
        """
        Get existing records linked to an applicant.

        Args:
            table: Airtable table object
            link_field: Name of the field linking to Applicants
            applicant_id: Airtable record ID

        Returns:
            List of record dictionaries with id and fields
        """
        formula = f"SEARCH('{applicant_id}', ARRAYJOIN({{{link_field}}})) > 0"

        try:
            records = table.all(formula=formula)
            return records
        except Exception as e:
            print(f"Warning: Error fetching linked records: {e}")
            return []

    def upsert_personal_details(self, applicant_id: str, personal_data: Dict) -> Optional[str]:
        """
        Upsert personal details for an applicant.

        Args:
            applicant_id: Airtable record ID
            personal_data: Personal details dictionary from JSON

        Returns:
            Record ID of the upserted record
        """
        if not personal_data:
            print("  No personal details to upsert")
            return None

        # Check if record exists
        existing_records = self.get_existing_linked_records(
            self.personal_table,
            'Applicant ID',
            applicant_id
        )

        # Prepare fields
        fields = {
            'Applicant ID': [applicant_id],
            'Full Name': personal_data.get('name', ''),
            'Email': personal_data.get('email', ''),
            'Location': personal_data.get('location', ''),
            'LinkedIn': personal_data.get('linkedin', ''),
        }

        if existing_records:
            # Update existing record
            record_id = existing_records[0]['id']
            self.personal_table.update(record_id, fields)
            print(f"  ✓ Updated Personal Details record {record_id}")
            return record_id
        else:
            # Create new record
            record = self.personal_table.create(fields)
            print(f"  ✓ Created Personal Details record {record['id']}")
            return record['id']

    def upsert_work_experience(self, applicant_id: str, experience_list: List[Dict]) -> List[str]:
        """
        Upsert work experience records for an applicant.

        Args:
            applicant_id: Airtable record ID
            experience_list: List of experience dictionaries from JSON

        Returns:
            List of record IDs
        """
        if not experience_list:
            print("  No work experience to upsert")
            return []

        # Get existing records
        existing_records = self.get_existing_linked_records(
            self.experience_table,
            'Applicant ID',
            applicant_id
        )

        # Delete all existing records (simplest approach for one-to-many)
        for record in existing_records:
            self.experience_table.delete(record['id'])
            print(f"  ✓ Deleted old Work Experience record {record['id']}")

        # Create new records from JSON
        created_ids = []
        for exp in experience_list:
            fields = {
                'Applicant ID': [applicant_id],
                'Company': exp.get('company', ''),
                'Title': exp.get('title', ''),
                'Start': exp.get('start', ''),
                'End': exp.get('end', ''),
                'Technologies': exp.get('technologies', ''),
            }

            record = self.experience_table.create(fields)
            created_ids.append(record['id'])
            print(f"  ✓ Created Work Experience record {record['id']} for {exp.get('company')}")

        return created_ids

    def upsert_salary_preferences(self, applicant_id: str, salary_data: Dict) -> Optional[str]:
        """
        Upsert salary preferences for an applicant.

        Args:
            applicant_id: Airtable record ID
            salary_data: Salary preferences dictionary from JSON

        Returns:
            Record ID of the upserted record
        """
        if not salary_data:
            print("  No salary preferences to upsert")
            return None

        # Check if record exists
        existing_records = self.get_existing_linked_records(
            self.salary_table,
            'Applicant ID',
            applicant_id
        )

        # Prepare fields
        fields = {
            'Applicant ID': [applicant_id],
            'Preferred Rate': salary_data.get('rate'),
            'Minimum Rate': salary_data.get('minimum_rate'),
            'Currency': salary_data.get('currency', 'USD'),
            'Availability (hrs/wk)': salary_data.get('availability'),
        }

        if existing_records:
            # Update existing record
            record_id = existing_records[0]['id']
            self.salary_table.update(record_id, fields)
            print(f"  ✓ Updated Salary Preferences record {record_id}")
            return record_id
        else:
            # Create new record
            record = self.salary_table.create(fields)
            print(f"  ✓ Created Salary Preferences record {record['id']}")
            return record['id']

    def decompress_applicant_data(self, applicant_id: str, json_data: Dict) -> Dict:
        """
        Decompress JSON data and upsert to child tables.

        Args:
            applicant_id: Airtable record ID
            json_data: Compressed JSON dictionary

        Returns:
            Dictionary with decompression results
        """
        print(f"Decompressing data for applicant {applicant_id}...")

        results = {
            'applicant_id': applicant_id,
            'personal_details_id': None,
            'work_experience_ids': [],
            'salary_preferences_id': None,
        }

        # Upsert to each child table
        print("\nUpserting Personal Details...")
        results['personal_details_id'] = self.upsert_personal_details(
            applicant_id,
            json_data.get('personal', {})
        )

        print("\nUpserting Work Experience...")
        results['work_experience_ids'] = self.upsert_work_experience(
            applicant_id,
            json_data.get('experience', [])
        )

        print("\nUpserting Salary Preferences...")
        results['salary_preferences_id'] = self.upsert_salary_preferences(
            applicant_id,
            json_data.get('salary', {})
        )

        return results

    def process_applicant(self, applicant_id: str, json_data: Optional[Dict] = None) -> Dict:
        """
        Process a single applicant through decompression.

        Args:
            applicant_id: Airtable record ID
            json_data: Optional JSON data (if None, reads from Applicants table)

        Returns:
            Dictionary with processing results
        """
        try:
            # If no JSON provided, fetch from Applicants table
            if json_data is None:
                record = self.applicants_table.get(applicant_id)
                compressed_json = record['fields'].get('Compressed JSON')

                if not compressed_json:
                    return {
                        'applicant_id': applicant_id,
                        'status': 'error',
                        'error': 'No Compressed JSON found in Applicants table'
                    }

                json_data = json.loads(compressed_json)

            # Decompress
            results = self.decompress_applicant_data(applicant_id, json_data)
            results['status'] = 'success'

            print(f"\n✓ Successfully decompressed applicant {applicant_id}")

            return results

        except Exception as e:
            print(f"Error processing applicant {applicant_id}: {e}")
            return {
                'applicant_id': applicant_id,
                'status': 'error',
                'error': str(e)
            }

    def process_all_applicants(self):
        """
        Process all applicants with compressed JSON.
        """
        print("Fetching all applicants with Compressed JSON...")

        # Filter for records with Compressed JSON
        formula = "{Compressed JSON} != ''"
        applicants = self.applicants_table.all(formula=formula)

        print(f"Found {len(applicants)} applicants with compressed JSON")

        results = []
        for record in applicants:
            applicant_id = record['id']
            print(f"\n{'='*60}")
            print(f"Processing applicant {applicant_id}")
            print(f"{'='*60}")

            compressed_json = record['fields'].get('Compressed JSON')
            json_data = json.loads(compressed_json)

            result = self.process_applicant(applicant_id, json_data)
            results.append(result)

        print(f"\n{'='*60}")
        print(f"Completed processing {len(results)} applicants")
        print(f"{'='*60}")

        return results


def main():
    """Main entry point for the decompression script."""
    parser = argparse.ArgumentParser(
        description='Decompress JSON data back to normalized Airtable tables'
    )

    parser.add_argument(
        '--applicant-id',
        type=str,
        help='Specific applicant ID to process (processes all if not specified)'
    )

    parser.add_argument(
        '--json-file',
        type=str,
        help='Path to JSON file to use instead of reading from Airtable'
    )

    args = parser.parse_args()

    # Initialize decompressor
    decompressor = DataDecompressor()

    # Load JSON from file if specified
    json_data = None
    if args.json_file:
        with open(args.json_file, 'r') as f:
            json_data = json.load(f)

    # Process applicant(s)
    if args.applicant_id:
        # Process single applicant
        result = decompressor.process_applicant(args.applicant_id, json_data)
        print(f"\nFinal Result:")
        print(json.dumps(result, indent=2, default=str))
    else:
        # Process all applicants
        if json_data:
            print("Error: --json-file requires --applicant-id")
            return

        results = decompressor.process_all_applicants()
        print(f"\nProcessed {len(results)} applicants")


if __name__ == '__main__':
    main()
