"""
JSON compression module for Airtable Contractor Application System.
Gathers data from multiple linked tables and compresses into a single JSON object.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def compress_applicant_data(airtable_client, applicant_id: int) -> Optional[str]:
    """
    Compress applicant data from multiple tables into a single JSON object.
    
    Args:
        airtable_client: AirtableClient instance
        applicant_id: Applicant ID number
        
    Returns:
        JSON string or None if applicant not found
    """
    try:
        # Get applicant record
        applicant_record = airtable_client.get_applicant(applicant_id)
        if not applicant_record:
            logger.warning(f"Applicant {applicant_id} not found")
            return None
        
        applicant_record_id = applicant_record["id"]
        
        # Get linked data
        personal_details = airtable_client.get_personal_details(applicant_record_id)
        work_experiences = airtable_client.get_work_experiences(applicant_record_id)
        salary_preferences = airtable_client.get_salary_preferences(applicant_record_id)
        
        # Build compressed JSON structure
        compressed_data = {}
        
        # Personal section
        if personal_details:
            fields = personal_details.get("fields", {})
            compressed_data["personal"] = {
                "name": fields.get("Full Name", ""),
                "email": fields.get("Email", ""),
                "location": fields.get("Location", ""),
                "linkedin": fields.get("LinkedIn", "")
            }
        else:
            compressed_data["personal"] = {}
            logger.warning(f"No personal details found for applicant {applicant_id}")
        
        # Experience section (array)
        compressed_data["experience"] = []
        for exp in work_experiences:
            fields = exp.get("fields", {})
            experience_entry = {
                "company": fields.get("Company", ""),
                "title": fields.get("Title", ""),
                "start": fields.get("Start", ""),
                "end": fields.get("End", ""),
                "technologies": fields.get("Technologies", "")
            }
            compressed_data["experience"].append(experience_entry)
        
        if not work_experiences:
            logger.warning(f"No work experience found for applicant {applicant_id}")
        
        # Salary section
        if salary_preferences:
            fields = salary_preferences.get("fields", {})
            compressed_data["salary"] = {
                "preferred_rate": fields.get("Preferred Rate", 0),
                "minimum_rate": fields.get("Minimum Rate", 0),
                "currency": fields.get("Currency", "USD"),
                "availability": fields.get("Availability (hrs/wk)", 0)
            }
        else:
            compressed_data["salary"] = {}
            logger.warning(f"No salary preferences found for applicant {applicant_id}")
        
        # Convert to JSON string
        json_string = json.dumps(compressed_data, indent=2)
        
        logger.info(f"Successfully compressed data for applicant {applicant_id}")
        return json_string
        
    except Exception as e:
        logger.error(f"Error compressing data for applicant {applicant_id}: {e}")
        raise


def save_compressed_json(airtable_client, applicant_id: int, compressed_json: str) -> Dict[str, Any]:
    """
    Save compressed JSON to the Applicants table.
    
    Args:
        airtable_client: AirtableClient instance
        applicant_id: Applicant ID number
        compressed_json: Compressed JSON string
        
    Returns:
        Updated applicant record
    """
    try:
        applicant_record = airtable_client.get_applicant(applicant_id)
        if not applicant_record:
            raise ValueError(f"Applicant {applicant_id} not found")
        
        # Update the Compressed JSON field
        updated_record = airtable_client.update_record(
            "Applicants",
            applicant_record["id"],
            {"Compressed JSON": compressed_json}
        )
        
        logger.info(f"Saved compressed JSON for applicant {applicant_id}")
        return updated_record
        
    except Exception as e:
        logger.error(f"Error saving compressed JSON for applicant {applicant_id}: {e}")
        raise


def compress_and_save(airtable_client, applicant_id: int) -> Dict[str, Any]:
    """
    Compress applicant data and save to Airtable.
    
    Args:
        airtable_client: AirtableClient instance
        applicant_id: Applicant ID number
        
    Returns:
        Updated applicant record with compressed JSON
    """
    compressed_json = compress_applicant_data(airtable_client, applicant_id)
    if not compressed_json:
        raise ValueError(f"Failed to compress data for applicant {applicant_id}")
    
    return save_compressed_json(airtable_client, applicant_id, compressed_json)


def calculate_years_of_experience(work_experiences: list) -> float:
    """
    Calculate total years of experience from work experience records.
    
    Args:
        work_experiences: List of work experience entries
        
    Returns:
        Total years of experience (float)
    """
    total_days = 0
    
    for exp in work_experiences:
        start_str = exp.get("start", "")
        end_str = exp.get("end", "")
        
        if not start_str:
            continue
        
        try:
            # Parse dates (handle various formats)
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            
            if end_str:
                end_date = datetime.strptime(end_str, "%Y-%m-%d")
            else:
                # If no end date, assume current position
                end_date = datetime.now()
            
            # Calculate days
            days = (end_date - start_date).days
            if days > 0:
                total_days += days
                
        except ValueError as e:
            logger.warning(f"Could not parse dates for experience entry: {e}")
            continue
    
    # Convert to years (approximate)
    years = total_days / 365.25
    return round(years, 2)

