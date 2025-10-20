"""
Compress applicant data from multiple Airtable tables into a single JSON object.
Optionally triggers shortlisting and LLM evaluation.
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

from shortlist import ShortlistEvaluator
from llm_evaluator import LLMEvaluator


class DataCompressor:
    """Compresses applicant data from child tables into JSON."""

    def __init__(self):
        """Initialize the compressor with Airtable connection."""
        validate_config()
        self.api = Api(AIRTABLE_API_KEY)
        self.base = self.api.base(AIRTABLE_BASE_ID)

        # Initialize table connections
        self.applicants_table = self.base.table(TABLE_APPLICANTS)
        self.personal_table = self.base.table(TABLE_PERSONAL_DETAILS)
        self.experience_table = self.base.table(TABLE_WORK_EXPERIENCE)
        self.salary_table = self.base.table(TABLE_SALARY_PREFERENCES)

    def get_linked_records(self, table, link_field: str, applicant_id: str) -> List[Dict]:
        """
        Get all records from a table linked to a specific applicant.

        Args:
            table: Airtable table object
            link_field: Name of the field linking to Applicants
            applicant_id: Airtable record ID of the applicant

        Returns:
            List of linked record fields
        """
        # Use formula to filter by linked applicant
        formula = f"SEARCH('{applicant_id}', ARRAYJOIN({{{link_field}}})) > 0"

        try:
            records = table.all(formula=formula)
            return [record['fields'] for record in records]
        except Exception as e:
            print(f"Warning: Error fetching linked records: {e}")
            return []

    def extract_personal_details(self, applicant_id: str) -> Optional[Dict]:
        """
        Extract personal details for an applicant.

        Args:
            applicant_id: Airtable record ID

        Returns:
            Personal details dictionary or None
        """
        records = self.get_linked_records(
            self.personal_table,
            'Applicant ID',
            applicant_id
        )

        if not records:
            return None

        # Should be one-to-one relationship, take the first record
        details = records[0]

        return {
            'name': details.get('Full Name'),
            'email': details.get('Email'),
            'location': details.get('Location'),
            'linkedin': details.get('LinkedIn'),
        }

    def extract_work_experience(self, applicant_id: str) -> List[Dict]:
        """
        Extract work experience for an applicant.

        Args:
            applicant_id: Airtable record ID

        Returns:
            List of work experience dictionaries
        """
        records = self.get_linked_records(
            self.experience_table,
            'Applicant ID',
            applicant_id
        )

        experiences = []
        for record in records:
            experiences.append({
                'company': record.get('Company'),
                'title': record.get('Title'),
                'start': record.get('Start'),
                'end': record.get('End'),
                'technologies': record.get('Technologies'),
            })

        return experiences

    def extract_salary_preferences(self, applicant_id: str) -> Optional[Dict]:
        """
        Extract salary preferences for an applicant.

        Args:
            applicant_id: Airtable record ID

        Returns:
            Salary preferences dictionary or None
        """
        records = self.get_linked_records(
            self.salary_table,
            'Applicant ID',
            applicant_id
        )

        if not records:
            return None

        # Should be one-to-one relationship, take the first record
        prefs = records[0]

        return {
            'rate': prefs.get('Preferred Rate'),
            'minimum_rate': prefs.get('Minimum Rate'),
            'currency': prefs.get('Currency'),
            'availability': prefs.get('Availability (hrs/wk)'),
        }

    def compress_applicant_data(self, applicant_id: str) -> Dict:
        """
        Compress all data for an applicant into a single JSON structure.

        Args:
            applicant_id: Airtable record ID

        Returns:
            Compressed JSON dictionary
        """
        print(f"Compressing data for applicant {applicant_id}...")

        # Extract data from all child tables
        personal = self.extract_personal_details(applicant_id)
        experience = self.extract_work_experience(applicant_id)
        salary = self.extract_salary_preferences(applicant_id)

        # Build compressed JSON
        compressed = {
            'personal': personal or {},
            'experience': experience or [],
            'salary': salary or {},
        }

        return compressed

    def update_compressed_json(self, applicant_id: str, compressed_data: Dict):
        """
        Update the Compressed JSON field in the Applicants table.

        Args:
            applicant_id: Airtable record ID
            compressed_data: Compressed JSON dictionary
        """
        json_string = json.dumps(compressed_data, indent=2)

        self.applicants_table.update(applicant_id, {
            'Compressed JSON': json_string
        })

        print(f"✓ Updated Compressed JSON for applicant {applicant_id}")

    def process_applicant(
        self,
        applicant_id: str,
        run_shortlist: bool = True,
        run_llm: bool = True
    ) -> Dict:
        """
        Process a single applicant through the compression pipeline.

        Args:
            applicant_id: Airtable record ID
            run_shortlist: Whether to run shortlisting after compression
            run_llm: Whether to run LLM evaluation after compression

        Returns:
            Dictionary with processing results
        """
        results = {
            'applicant_id': applicant_id,
            'compression': None,
            'shortlist': None,
            'llm': None,
        }

        try:
            # Step 1: Compress data
            compressed_data = self.compress_applicant_data(applicant_id)
            self.update_compressed_json(applicant_id, compressed_data)
            results['compression'] = {'status': 'success', 'data': compressed_data}

            # Step 2: Run shortlisting (if enabled)
            if run_shortlist:
                print("\nRunning shortlist evaluation...")
                evaluator = ShortlistEvaluator()
                shortlist_result = evaluator.process_applicant(applicant_id, compressed_data)
                results['shortlist'] = shortlist_result

            # Step 3: Run LLM evaluation (if enabled)
            if run_llm:
                print("\nRunning LLM evaluation...")
                llm_evaluator = LLMEvaluator()
                llm_result = llm_evaluator.process_applicant(applicant_id, compressed_data)
                results['llm'] = llm_result

            return results

        except Exception as e:
            print(f"Error processing applicant {applicant_id}: {e}")
            results['error'] = str(e)
            return results

    def process_all_applicants(self, run_shortlist: bool = True, run_llm: bool = True):
        """
        Process all applicants in the Applicants table.

        Args:
            run_shortlist: Whether to run shortlisting
            run_llm: Whether to run LLM evaluation
        """
        print("Fetching all applicants...")
        all_applicants = self.applicants_table.all()

        print(f"Found {len(all_applicants)} applicants")

        results = []
        for record in all_applicants:
            applicant_id = record['id']
            print(f"\n{'='*60}")
            print(f"Processing applicant {applicant_id}")
            print(f"{'='*60}")

            result = self.process_applicant(applicant_id, run_shortlist, run_llm)
            results.append(result)

        print(f"\n{'='*60}")
        print(f"Completed processing {len(results)} applicants")
        print(f"{'='*60}")

        return results


def main():
    """Main entry point for the compression script."""
    parser = argparse.ArgumentParser(
        description='Compress applicant data from Airtable into JSON format'
    )

    parser.add_argument(
        '--applicant-id',
        type=str,
        help='Specific applicant ID to process (processes all if not specified)'
    )

    parser.add_argument(
        '--no-shortlist',
        action='store_true',
        help='Skip shortlisting evaluation'
    )

    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Skip LLM evaluation'
    )

    parser.add_argument(
        '--evaluate',
        action='store_true',
        help='Run both shortlisting and LLM evaluation (default behavior)'
    )

    args = parser.parse_args()

    # Initialize compressor
    compressor = DataCompressor()

    # Determine what to run
    run_shortlist = not args.no_shortlist
    run_llm = not args.no_llm

    # Process applicant(s)
    if args.applicant_id:
        # Process single applicant
        result = compressor.process_applicant(
            args.applicant_id,
            run_shortlist=run_shortlist,
            run_llm=run_llm
        )
        print(f"\nFinal Result:")
        print(json.dumps(result, indent=2, default=str))
    else:
        # Process all applicants
        results = compressor.process_all_applicants(
            run_shortlist=run_shortlist,
            run_llm=run_llm
        )
        print(f"\nProcessed {len(results)} applicants")


if __name__ == '__main__':
    main()
