"""
Shortlisting logic for contractor applications.
Evaluates candidates based on experience, compensation, and location criteria.
"""

import json
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional, Tuple
from pyairtable import Api

from config import (
    AIRTABLE_API_KEY,
    AIRTABLE_BASE_ID,
    TABLE_APPLICANTS,
    TABLE_SHORTLISTED_LEADS,
    TIER_1_COMPANIES,
    SHORTLIST_CRITERIA,
    normalize_company_name,
    normalize_location,
    validate_config,
)


class ShortlistEvaluator:
    """Evaluates applicants against shortlisting criteria."""

    def __init__(self):
        """Initialize the evaluator with Airtable connection."""
        validate_config()
        self.api = Api(AIRTABLE_API_KEY)
        self.base = self.api.base(AIRTABLE_BASE_ID)
        self.applicants_table = self.base.table(TABLE_APPLICANTS)
        self.shortlisted_table = self.base.table(TABLE_SHORTLISTED_LEADS)

    def calculate_years_of_experience(self, experience_list: List[Dict]) -> float:
        """
        Calculate total years of experience from work history.

        Args:
            experience_list: List of work experience dictionaries

        Returns:
            Total years of experience (rounded to 1 decimal)
        """
        total_months = 0

        for exp in experience_list:
            start_date = exp.get('start') or exp.get('Start')
            end_date = exp.get('end') or exp.get('End') or datetime.now().strftime('%Y-%m-%d')

            if not start_date:
                continue

            try:
                start = parser.parse(start_date)
                end = parser.parse(end_date) if end_date else datetime.now()

                # Calculate months between dates
                delta = relativedelta(end, start)
                months = delta.years * 12 + delta.months

                total_months += months
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not parse dates for experience: {e}")
                continue

        return round(total_months / 12, 1)

    def has_tier1_experience(self, experience_list: List[Dict]) -> Tuple[bool, Optional[str]]:
        """
        Check if candidate has worked at a tier-1 company.

        Args:
            experience_list: List of work experience dictionaries

        Returns:
            Tuple of (has_tier1, company_name)
        """
        for exp in experience_list:
            company = exp.get('company') or exp.get('Company')
            if company:
                normalized = normalize_company_name(company)
                if normalized in TIER_1_COMPANIES:
                    return True, normalized

        return False, None

    def evaluate_experience(self, json_data: Dict) -> Tuple[bool, str]:
        """
        Evaluate experience criteria.

        Args:
            json_data: Compressed JSON data

        Returns:
            Tuple of (meets_criteria, reason)
        """
        experience_list = json_data.get('experience', [])

        # Calculate years of experience
        years_exp = self.calculate_years_of_experience(experience_list)

        # Check for tier-1 company experience
        has_tier1, tier1_company = self.has_tier1_experience(experience_list)

        # Meets criteria if >= 4 years OR worked at tier-1 company
        if years_exp >= SHORTLIST_CRITERIA['min_years_experience']:
            return True, f"{years_exp} years of experience (>= {SHORTLIST_CRITERIA['min_years_experience']} required)"
        elif has_tier1:
            return True, f"Worked at tier-1 company: {tier1_company}"
        else:
            return False, f"Only {years_exp} years of experience and no tier-1 company background"

    def evaluate_compensation(self, json_data: Dict) -> Tuple[bool, str]:
        """
        Evaluate compensation criteria.

        Args:
            json_data: Compressed JSON data

        Returns:
            Tuple of (meets_criteria, reason)
        """
        salary = json_data.get('salary', {})

        preferred_rate = salary.get('rate') or salary.get('Preferred Rate')
        availability = salary.get('availability') or salary.get('Availability (hrs/wk)')
        currency = salary.get('currency') or salary.get('Currency', 'USD')

        # Validate data
        if preferred_rate is None:
            return False, "Missing preferred rate information"

        if availability is None:
            return False, "Missing availability information"

        try:
            preferred_rate = float(preferred_rate)
            availability = float(availability)
        except (ValueError, TypeError):
            return False, "Invalid rate or availability format"

        # Normalize to USD if needed (simplified - in production, use real exchange rates)
        if currency.upper() != 'USD':
            # For this exercise, we'll accept non-USD with a warning
            rate_check = f"${preferred_rate} {currency}/hour"
        else:
            rate_check = f"${preferred_rate}/hour"

        # Check criteria: rate <= $100 AND availability >= 20 hrs/week
        rate_ok = preferred_rate <= SHORTLIST_CRITERIA['max_hourly_rate_usd'] if currency.upper() == 'USD' else True
        hours_ok = availability >= SHORTLIST_CRITERIA['min_weekly_hours']

        if rate_ok and hours_ok:
            return True, f"{rate_check} with {availability} hrs/week availability"
        elif not rate_ok:
            return False, f"Rate {rate_check} exceeds ${SHORTLIST_CRITERIA['max_hourly_rate_usd']}/hour limit"
        else:
            return False, f"Availability {availability} hrs/week below {SHORTLIST_CRITERIA['min_weekly_hours']} hrs minimum"

    def evaluate_location(self, json_data: Dict) -> Tuple[bool, str]:
        """
        Evaluate location criteria.

        Args:
            json_data: Compressed JSON data

        Returns:
            Tuple of (meets_criteria, reason)
        """
        personal = json_data.get('personal', {})
        location = personal.get('location') or personal.get('Location')

        if not location:
            return False, "Missing location information"

        normalized = normalize_location(location)

        # Check if location is in valid set
        valid_locations = SHORTLIST_CRITERIA['valid_locations']

        # Check if any valid location appears in the normalized location string
        for valid_loc in valid_locations:
            if valid_loc.lower() in normalized.lower():
                return True, f"Located in {normalized}"

        return False, f"Location '{normalized}' not in approved regions"

    def evaluate_applicant(self, applicant_id: str, json_data: Dict) -> Tuple[bool, Dict[str, any]]:
        """
        Evaluate an applicant against all shortlisting criteria.

        Args:
            applicant_id: Airtable record ID
            json_data: Compressed JSON data

        Returns:
            Tuple of (should_shortlist, evaluation_details)
        """
        # Evaluate each criterion
        exp_pass, exp_reason = self.evaluate_experience(json_data)
        comp_pass, comp_reason = self.evaluate_compensation(json_data)
        loc_pass, loc_reason = self.evaluate_location(json_data)

        # All criteria must pass
        should_shortlist = exp_pass and comp_pass and loc_pass

        evaluation = {
            'should_shortlist': should_shortlist,
            'experience': {'pass': exp_pass, 'reason': exp_reason},
            'compensation': {'pass': comp_pass, 'reason': comp_reason},
            'location': {'pass': loc_pass, 'reason': loc_reason},
        }

        return should_shortlist, evaluation

    def create_shortlist_record(self, applicant_id: str, json_data: Dict, evaluation: Dict) -> str:
        """
        Create a record in the Shortlisted Leads table.

        Args:
            applicant_id: Airtable record ID for the applicant
            json_data: Compressed JSON data
            evaluation: Evaluation details

        Returns:
            Record ID of the created shortlist entry
        """
        # Build human-readable score reason
        score_reason = "Candidate meets all shortlisting criteria:\n"
        score_reason += f"- Experience: {evaluation['experience']['reason']}\n"
        score_reason += f"- Compensation: {evaluation['compensation']['reason']}\n"
        score_reason += f"- Location: {evaluation['location']['reason']}"

        # Create the record
        record = self.shortlisted_table.create({
            'Applicant': [applicant_id],  # Link to Applicants table
            'Compressed JSON': json.dumps(json_data, indent=2),
            'Score Reason': score_reason,
            'Created At': datetime.now().isoformat(),
        })

        return record['id']

    def update_applicant_shortlist_status(self, applicant_id: str, status: str):
        """
        Update the shortlist status field in the Applicants table.

        Args:
            applicant_id: Airtable record ID
            status: Shortlist status (e.g., "Shortlisted", "Not Shortlisted")
        """
        self.applicants_table.update(applicant_id, {
            'Shortlist Status': status
        })

    def process_applicant(self, applicant_id: str, json_data: Dict) -> Dict:
        """
        Process a single applicant through the shortlisting pipeline.

        Args:
            applicant_id: Airtable record ID
            json_data: Compressed JSON data

        Returns:
            Dictionary with processing results
        """
        should_shortlist, evaluation = self.evaluate_applicant(applicant_id, json_data)

        result = {
            'applicant_id': applicant_id,
            'shortlisted': should_shortlist,
            'evaluation': evaluation,
        }

        if should_shortlist:
            # Create shortlist record
            shortlist_id = self.create_shortlist_record(applicant_id, json_data, evaluation)
            self.update_applicant_shortlist_status(applicant_id, 'Shortlisted')
            result['shortlist_record_id'] = shortlist_id
            print(f"✓ Applicant {applicant_id} shortlisted (record: {shortlist_id})")
        else:
            self.update_applicant_shortlist_status(applicant_id, 'Not Shortlisted')
            print(f"✗ Applicant {applicant_id} not shortlisted")
            print(f"  Reasons:")
            if not evaluation['experience']['pass']:
                print(f"  - Experience: {evaluation['experience']['reason']}")
            if not evaluation['compensation']['pass']:
                print(f"  - Compensation: {evaluation['compensation']['reason']}")
            if not evaluation['location']['pass']:
                print(f"  - Location: {evaluation['location']['reason']}")

        return result


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python shortlist.py <applicant_id>")
        sys.exit(1)

    applicant_id = sys.argv[1]

    # For testing, load from Applicants table
    evaluator = ShortlistEvaluator()
    record = evaluator.applicants_table.get(applicant_id)

    compressed_json = record['fields'].get('Compressed JSON')
    if not compressed_json:
        print(f"Error: No compressed JSON found for applicant {applicant_id}")
        sys.exit(1)

    json_data = json.loads(compressed_json)
    result = evaluator.process_applicant(applicant_id, json_data)

    print(f"\nShortlisting Result:")
    print(json.dumps(result, indent=2))
