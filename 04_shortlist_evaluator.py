#!/usr/bin/env python3
"""
Shortlist Evaluator - Airtable Contractor Application System

Evaluates applicants against qualification criteria and creates Shortlisted Leads
records for candidates who meet ALL requirements.

Qualification Criteria (ALL must pass):
1. Experience: >=4 years total OR worked at tier-1 company
2. Compensation: Preferred rate <=$100/hr AND Availability >=20 hrs/wk
3. Location: In US, Canada, UK, Germany, or India

Usage:
    python shortlist_evaluator.py              # Evaluate all applicants
    python shortlist_evaluator.py --id <id>    # Evaluate single applicant
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
from dateutil.parser import parse as parse_date
from dotenv import load_dotenv
from pyairtable import Api

# Tier-1 companies per PRD
TIER1_COMPANIES = [
    'google', 'meta', 'openai', 'microsoft', 'amazon', 'apple',
    'netflix', 'tesla', 'spacex', 'uber', 'airbnb', 'stripe'
]

# Approved locations per PRD with country codes and major cities
APPROVED_LOCATIONS = {
    # United States
    'united states', 'usa', 'us ', ' us', 'america', 'american',
    'new york', 'nyc', 'san francisco', 'sf', 'los angeles', 'la',
    'seattle', 'wa', 'austin', 'tx', 'boston', 'ma', 'chicago', 'il',

    # Canada
    'canada', 'canadian', 'ca ',
    'toronto', 'on', 'vancouver', 'bc', 'montreal', 'qc',

    # United Kingdom
    'united kingdom', 'uk ', ' uk', 'britain', 'british', 'england', 'scotland', 'wales',
    'london', 'manchester', 'birmingham', 'edinburgh',

    # Germany
    'germany', 'deutschland', 'german', 'de ',
    'berlin', 'munich', 'hamburg', 'frankfurt', 'cologne',

    # India
    'india', 'indian', 'in ',
    'bangalore', 'bengaluru', 'mumbai', 'delhi', 'new delhi', 'hyderabad', 'chennai', 'pune'
}

# Country codes for exact matching
APPROVED_COUNTRY_CODES = {'us', 'usa', 'can', 'ca', 'uk', 'gb', 'de', 'deu', 'in', 'ind'}

def calculate_years_of_experience(experience_list: List[Dict[str, Any]]) -> float:
    """
    Calculate total years of experience from work history.
    Handles various date formats, "present/current/ongoing" jobs, and validation.

    Args:
        experience_list: List of experience dicts with start and end dates

    Returns:
        float: Total years of experience
    """
    total_days = 0

    for job in experience_list:
        try:
            start_str = job.get('start', '').strip()
            end_str = job.get('end', '').strip()

            if not start_str:
                print(f"    Warning: No start date for {job.get('company', 'Unknown')}, skipping")
                continue

            # Parse start date
            start = parse_date(start_str)

            # Handle "present", "current", "ongoing", or empty end dates
            if not end_str or end_str.lower() in ['present', 'current', 'ongoing', 'now']:
                end = datetime.now()
            else:
                end = parse_date(end_str)

            # Validation: check for impossible dates
            if start > datetime.now():
                print(f"    Warning: Future start date for {job.get('company', 'Unknown')}, skipping")
                continue

            if end < start:
                print(f"    Warning: End date before start date for {job.get('company', 'Unknown')}, skipping")
                continue

            days = (end - start).days

            # Sanity check: avoid counting ridiculously long tenures (>50 years)
            if days > 365.25 * 50:
                print(f"    Warning: Unusually long tenure ({days/365.25:.1f} years) for {job.get('company', 'Unknown')}, capping at 50 years")
                days = 365.25 * 50

            total_days += days

        except ValueError as e:
            print(f"    Warning: Invalid date format for {job.get('company', 'Unknown')}: {e}")
            continue
        except Exception as e:
            print(f"    Warning: Could not parse dates for {job.get('company', 'Unknown')}: {e}")
            continue

    return total_days / 365.25  # Account for leap years

def check_tier1_company(experience_list: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    """
    Check if candidate worked at any tier-1 company.

    Args:
        experience_list: List of experience dicts

    Returns:
        tuple: (bool, str) - (has_tier1, company_name)
    """
    for job in experience_list:
        company = job.get('company', '').lower()
        for tier1 in TIER1_COMPANIES:
            if tier1 in company:
                return True, job.get('company', '')

    return False, None

def check_location(location_str: str) -> bool:
    """
    Check if location is in approved regions.
    Uses improved word boundary matching and country code detection.
    Prevents false matches like "India" matching "Indiana".

    Args:
        location_str: Location string from applicant

    Returns:
        bool: True if in approved region
    """
    if not location_str:
        return False

    location_lower = location_str.lower().strip()

    # Blacklist patterns that should NOT match (avoid false positives)
    blacklist = ['australia', 'austria', 'indonesia', 'indiana']
    for blacklisted in blacklist:
        if blacklisted in location_lower:
            return False

    # Check for exact country code matches (US, CA, UK, DE, IN)
    location_words = location_lower.replace(',', ' ').replace('.', ' ').split()
    for word in location_words:
        cleaned_word = word.strip()
        if cleaned_word in APPROVED_COUNTRY_CODES:
            return True

    # Check for approved location phrases
    for approved in APPROVED_LOCATIONS:
        # Use word boundaries to avoid substring matches
        # e.g., " india " in " new delhi, india " but not " indiana "
        padded_location = f" {location_lower} "
        padded_approved = f" {approved} "

        if padded_approved in padded_location:
            return True

        # Also check if approved term is a complete word
        if f" {approved}," in padded_location or f",{approved} " in padded_location:
            return True

    return False

def evaluate_applicant(applicant_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Dict[str, Any]]]:
    """
    Evaluate if applicant meets all qualification criteria.

    Args:
        applicant_data: Dict with parsed JSON data

    Returns:
        tuple: (qualifies, reasons_dict)
    """
    reasons = {
        'experience': {'passes': False, 'reason': ''},
        'compensation': {'passes': False, 'reason': ''},
        'location': {'passes': False, 'reason': ''}
    }

    # Criterion 1: Experience
    experience_list = applicant_data.get('experience', [])
    years = calculate_years_of_experience(experience_list)
    has_tier1, tier1_company = check_tier1_company(experience_list)

    if years >= 4:
        reasons['experience']['passes'] = True
        reasons['experience']['reason'] = f"{years:.1f} years total experience (>=4 required)"
    elif has_tier1:
        reasons['experience']['passes'] = True
        reasons['experience']['reason'] = f"Worked at {tier1_company} (tier-1 company)"
    else:
        reasons['experience']['reason'] = f"Only {years:.1f} years and no tier-1 company"

    # Criterion 2: Compensation
    salary = applicant_data.get('salary', {})
    preferred_rate = salary.get('preferred_rate', 999)
    availability = salary.get('availability', 0)

    if preferred_rate <= 100 and availability >= 20:
        reasons['compensation']['passes'] = True
        reasons['compensation']['reason'] = f"${preferred_rate}/hr (<=$100), {availability} hrs/wk (>=20)"
    else:
        fail_parts = []
        if preferred_rate > 100:
            fail_parts.append(f"rate ${preferred_rate}/hr >$100")
        if availability < 20:
            fail_parts.append(f"availability {availability} hrs/wk <20")
        reasons['compensation']['reason'] = ', '.join(fail_parts)

    # Criterion 3: Location
    personal = applicant_data.get('personal', {})
    location = personal.get('location', '')

    if check_location(location):
        reasons['location']['passes'] = True
        reasons['location']['reason'] = f"{location} (approved region)"
    else:
        reasons['location']['reason'] = f"{location} (not in approved regions)"

    # Check if all criteria pass
    all_pass = all([
        reasons['experience']['passes'],
        reasons['compensation']['passes'],
        reasons['location']['passes']
    ])

    return all_pass, reasons

def generate_score_reason(
    qualifies: bool,
    reasons: Dict[str, Dict[str, Any]],
    applicant_data: Dict[str, Any]
) -> str:
    """
    Generate human-readable score reason.

    Args:
        qualifies: bool - Whether applicant qualifies
        reasons: dict - Detailed reasons for each criterion
        applicant_data: dict - Applicant data

    Returns:
        str: Formatted score reason
    """
    personal = applicant_data.get('personal', {})
    name = personal.get('name', 'Unknown')

    if qualifies:
        return f"""Candidate qualifies for shortlist:
- Experience: {reasons['experience']['reason']}
- Compensation: {reasons['compensation']['reason']}
- Location: {reasons['location']['reason']}"""
    else:
        failed_criteria = []
        for criterion, data in reasons.items():
            if not data['passes']:
                failed_criteria.append(f"{criterion.capitalize()}: {data['reason']}")

        return f"""Candidate does NOT qualify:
{chr(10).join(['- ' + c for c in failed_criteria])}"""

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate applicants and create Shortlisted Leads records"
    )
    parser.add_argument('--id', type=str, help='Specific applicant record ID')
    args = parser.parse_args()

    print("=" * 70)
    print("Shortlist Evaluator - Contractor Application System")
    print("=" * 70)
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
        shortlisted_leads_table = base.table("Shortlisted Leads")
    except Exception as e:
        print(f"ERROR: Failed to connect: {e}")
        sys.exit(1)

    # Get applicants to process
    if args.id:
        print(f"Evaluating single applicant: {args.id}")
        applicants = [applicants_table.get(args.id)]
    else:
        print("Evaluating all applicants...")
        applicants = applicants_table.all()

    print()
    print("=" * 70)
    print("Evaluation Results")
    print("=" * 70)
    print()

    qualified_count = 0
    not_qualified_count = 0
    error_count = 0

    for idx, applicant in enumerate(applicants, 1):
        applicant_id = applicant['id']
        fields = applicant['fields']

        # Get compressed JSON
        compressed_json_str = fields.get('Compressed JSON', '')
        if not compressed_json_str:
            print(f"[{idx}/{len(applicants)}] {applicant_id}: Skipped (no compressed JSON)")
            error_count += 1
            continue

        try:
            applicant_data = json.loads(compressed_json_str)
            name = applicant_data.get('personal', {}).get('name', 'Unknown')

            print(f"[{idx}/{len(applicants)}] {name} ({applicant_id}):")

            # Evaluate criteria
            qualifies, reasons = evaluate_applicant(applicant_data)

            # Generate score reason
            score_reason = generate_score_reason(qualifies, reasons, applicant_data)

            if qualifies:
                print(f"  ✓ QUALIFIES")
                print(f"    - Experience: {reasons['experience']['reason']}")
                print(f"    - Compensation: {reasons['compensation']['reason']}")
                print(f"    - Location: {reasons['location']['reason']}")

                # Update Shortlist Status
                applicants_table.update(applicant_id, {
                    'Shortlist Status': True
                })

                # Create Shortlisted Leads record
                shortlisted_leads_table.create({
                    'Applicant': [applicant_id],
                    'Compressed JSON': compressed_json_str,
                    'Score Reason': score_reason
                })

                qualified_count += 1
            else:
                print(f"  ✗ Does NOT qualify")
                for criterion, data in reasons.items():
                    if not data['passes']:
                        print(f"    - {criterion.capitalize()}: {data['reason']}")

                # Reset Shortlist Status to False
                applicants_table.update(applicant_id, {
                    'Shortlist Status': False
                })

                not_qualified_count += 1

            print()

        except Exception as e:
            print(f"  ERROR: {e}")
            error_count += 1
            print()

    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total evaluated: {len(applicants)}")
    print(f"✓ Qualified: {qualified_count}")
    print(f"✗ Not qualified: {not_qualified_count}")
    print(f"Errors: {error_count}")
    print()
    print(f"Shortlisted Leads table now has {qualified_count} record(s)")
    print()
    print("Next steps:")
    print("  1. View Shortlisted Leads: https://airtable.com/{base_id}")
    print("  2. Run llm_evaluator.py to enrich with LLM analysis")
    print()

if __name__ == "__main__":
    main()
