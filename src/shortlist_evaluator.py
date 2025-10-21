"""
Candidate shortlist evaluator for Airtable Contractor Application System.
Evaluates candidates based on multi-factor rules defined in the PRD.
"""

import json
import logging
from typing import Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Tier-1 companies as defined in PRD
TIER_1_COMPANIES = {
    "Google", "Meta", "OpenAI", "Microsoft", "Amazon", "Apple", 
    "Netflix", "Tesla", "SpaceX", "Uber", "Airbnb", "Stripe",
    "Facebook",  # Include both Meta and Facebook for historical data
}

# Allowed locations
ALLOWED_LOCATIONS = {"US", "USA", "United States", "Canada", "UK", "United Kingdom", "Germany", "India"}


def normalize_company_name(company: str) -> str:
    """
    Normalize company name for comparison.
    
    Args:
        company: Company name
        
    Returns:
        Normalized company name
    """
    return company.strip().lower()


def is_tier_1_company(company: str) -> bool:
    """
    Check if company is a tier-1 company.
    
    Args:
        company: Company name
        
    Returns:
        True if tier-1 company, False otherwise
    """
    normalized = normalize_company_name(company)
    return any(normalize_company_name(tier1) == normalized for tier1 in TIER_1_COMPANIES)


def normalize_location(location: str) -> str:
    """
    Normalize location string for comparison.
    
    Args:
        location: Location string
        
    Returns:
        Normalized location
    """
    return location.strip()


def is_allowed_location(location: str) -> bool:
    """
    Check if location is in the allowed list.
    
    Args:
        location: Location string
        
    Returns:
        True if allowed location, False otherwise
    """
    normalized = normalize_location(location)
    
    # Check exact matches
    for allowed in ALLOWED_LOCATIONS:
        if allowed.lower() in normalized.lower():
            return True
    
    return False


def calculate_years_of_experience(experiences: list) -> float:
    """
    Calculate total years of experience from work experience records.
    
    Args:
        experiences: List of experience dictionaries
        
    Returns:
        Total years of experience (float)
    """
    total_days = 0
    
    for exp in experiences:
        start_str = exp.get("start", "")
        end_str = exp.get("end", "")
        
        if not start_str:
            continue
        
        try:
            # Parse dates (handle various formats)
            if "T" in start_str:
                start_date = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            else:
                start_date = datetime.strptime(start_str, "%Y-%m-%d")
            
            if end_str:
                if "T" in end_str:
                    end_date = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                else:
                    end_date = datetime.strptime(end_str, "%Y-%m-%d")
            else:
                # If no end date, assume current position
                end_date = datetime.now()
            
            # Calculate days
            days = (end_date - start_date).days
            if days > 0:
                total_days += days
                
        except (ValueError, AttributeError) as e:
            logger.warning(f"Could not parse dates for experience entry: {e}")
            continue
    
    # Convert to years (approximate)
    years = total_days / 365.25
    return round(years, 2)


def evaluate_experience_criteria(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Evaluate experience criteria: ≥4 years OR tier-1 company.
    
    Args:
        data: Compressed applicant data
        
    Returns:
        Tuple of (meets_criteria, reason)
    """
    experiences = data.get("experience", [])
    
    if not experiences:
        return False, "No work experience provided"
    
    # Calculate total years
    years = calculate_years_of_experience(experiences)
    
    # Check for tier-1 companies
    tier_1_companies_worked = [
        exp.get("company", "") for exp in experiences 
        if is_tier_1_company(exp.get("company", ""))
    ]
    
    if years >= 4:
        return True, f"{years} years of experience (≥4 years required)"
    elif tier_1_companies_worked:
        companies_str = ", ".join(tier_1_companies_worked)
        return True, f"Worked at tier-1 company: {companies_str}"
    else:
        return False, f"Only {years} years of experience and no tier-1 company"


def evaluate_compensation_criteria(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Evaluate compensation criteria: Preferred Rate ≤$100 USD/hour AND Availability ≥20 hrs/week.
    
    Args:
        data: Compressed applicant data
        
    Returns:
        Tuple of (meets_criteria, reason)
    """
    salary = data.get("salary", {})
    
    if not salary:
        return False, "No salary preferences provided"
    
    preferred_rate = salary.get("preferred_rate", 0)
    currency = salary.get("currency", "USD")
    availability = salary.get("availability", 0)
    
    # Convert to USD if needed (simplified - in production, use exchange rates)
    # For now, we'll only accept USD for accurate comparison
    if currency != "USD":
        return False, f"Currency is {currency}, not USD (cannot compare rates)"
    
    rate_meets_criteria = preferred_rate <= 100
    availability_meets_criteria = availability >= 20
    
    if rate_meets_criteria and availability_meets_criteria:
        return True, f"${preferred_rate}/hr (≤$100) and {availability} hrs/week (≥20)"
    elif not rate_meets_criteria:
        return False, f"Preferred rate ${preferred_rate}/hr exceeds $100/hr"
    else:
        return False, f"Availability {availability} hrs/week is less than 20 hrs/week"


def evaluate_location_criteria(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Evaluate location criteria: In US, Canada, UK, Germany, or India.
    
    Args:
        data: Compressed applicant data
        
    Returns:
        Tuple of (meets_criteria, reason)
    """
    personal = data.get("personal", {})
    
    if not personal:
        return False, "No personal details provided"
    
    location = personal.get("location", "")
    
    if not location:
        return False, "No location provided"
    
    if is_allowed_location(location):
        return True, f"Location: {location}"
    else:
        return False, f"Location '{location}' not in allowed regions"


def evaluate_for_shortlist(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Evaluate if candidate meets all shortlist criteria.
    
    Criteria:
    1. Experience: ≥4 years OR tier-1 company
    2. Compensation: Preferred Rate ≤$100/hr AND Availability ≥20 hrs/week
    3. Location: US, Canada, UK, Germany, or India
    
    Args:
        data: Compressed applicant data (as dictionary)
        
    Returns:
        Tuple of (is_qualified, detailed_reason)
    """
    reasons = []
    all_criteria_met = True
    
    # Evaluate experience
    exp_meets, exp_reason = evaluate_experience_criteria(data)
    reasons.append(f"Experience: {exp_reason}")
    if not exp_meets:
        all_criteria_met = False
    
    # Evaluate compensation
    comp_meets, comp_reason = evaluate_compensation_criteria(data)
    reasons.append(f"Compensation: {comp_reason}")
    if not comp_meets:
        all_criteria_met = False
    
    # Evaluate location
    loc_meets, loc_reason = evaluate_location_criteria(data)
    reasons.append(f"Location: {loc_reason}")
    if not loc_meets:
        all_criteria_met = False
    
    detailed_reason = "\n".join(reasons)
    
    if all_criteria_met:
        detailed_reason = "SHORTLISTED\n" + detailed_reason
    else:
        detailed_reason = "NOT SHORTLISTED\n" + detailed_reason
    
    return all_criteria_met, detailed_reason


def process_shortlist(airtable_client, applicant_id: int) -> Dict[str, Any]:
    """
    Process shortlist evaluation for an applicant.
    Updates Shortlist Status and creates Shortlisted Lead if qualified.
    
    Args:
        airtable_client: AirtableClient instance
        applicant_id: Applicant ID number
        
    Returns:
        Dictionary with evaluation results
    """
    try:
        # Get applicant record
        applicant_record = airtable_client.get_applicant(applicant_id)
        if not applicant_record:
            raise ValueError(f"Applicant {applicant_id} not found")
        
        applicant_record_id = applicant_record["id"]
        
        # Get compressed JSON
        compressed_json = applicant_record.get("fields", {}).get("Compressed JSON", "")
        if not compressed_json:
            raise ValueError(f"No compressed JSON found for applicant {applicant_id}. Run compression first.")
        
        # Parse JSON
        try:
            data = json.loads(compressed_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format for applicant {applicant_id}: {e}")
        
        # Evaluate for shortlist
        is_qualified, reason = evaluate_for_shortlist(data)
        
        # Update Shortlist Status
        airtable_client.update_record(
            "Applicants",
            applicant_record_id,
            {"Shortlist Status": is_qualified}
        )
        
        result = {
            "applicant_id": applicant_id,
            "is_qualified": is_qualified,
            "reason": reason,
            "shortlisted_lead_created": False
        }
        
        # Create Shortlisted Lead if qualified
        if is_qualified:
            shortlisted_lead = airtable_client.create_shortlisted_lead(
                applicant_record_id,
                compressed_json,
                reason
            )
            result["shortlisted_lead_created"] = True
            result["shortlisted_lead_id"] = shortlisted_lead["id"]
            logger.info(f"Created shortlisted lead for applicant {applicant_id}")
        
        logger.info(f"Processed shortlist evaluation for applicant {applicant_id}: {'QUALIFIED' if is_qualified else 'NOT QUALIFIED'}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing shortlist for applicant {applicant_id}: {e}")
        raise

