"""
JSON decompression module for Airtable Contractor Application System.
Reads compressed JSON and upserts data back to normalized tables.
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def decompress_applicant_data(airtable_client, applicant_id: int) -> Dict[str, Any]:
    """
    Read compressed JSON and upsert data back to child tables.
    
    Args:
        airtable_client: AirtableClient instance
        applicant_id: Applicant ID number
        
    Returns:
        Dictionary with results of upsert operations
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
            raise ValueError(f"No compressed JSON found for applicant {applicant_id}")
        
        # Parse JSON
        try:
            data = json.loads(compressed_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format for applicant {applicant_id}: {e}")
        
        results = {}
        
        # Upsert Personal Details
        if "personal" in data and data["personal"]:
            personal_fields = {
                "Full Name": data["personal"].get("name", ""),
                "Email": data["personal"].get("email", ""),
                "Location": data["personal"].get("location", ""),
                "LinkedIn": data["personal"].get("linkedin", "")
            }
            results["personal_details"] = airtable_client.upsert_personal_details(
                applicant_record_id, personal_fields
            )
            logger.info(f"Upserted personal details for applicant {applicant_id}")
        
        # Upsert Work Experience
        if "experience" in data and isinstance(data["experience"], list):
            experience_records = []
            for exp in data["experience"]:
                exp_fields = {
                    "Company": exp.get("company", ""),
                    "Title": exp.get("title", ""),
                    "Start": exp.get("start", ""),
                    "End": exp.get("end", ""),
                    "Technologies": exp.get("technologies", "")
                }
                experience_records.append(exp_fields)
            
            if experience_records:
                results["work_experiences"] = airtable_client.upsert_work_experiences(
                    applicant_record_id, experience_records
                )
                logger.info(f"Upserted {len(experience_records)} work experiences for applicant {applicant_id}")
        
        # Upsert Salary Preferences
        if "salary" in data and data["salary"]:
            salary_fields = {
                "Preferred Rate": data["salary"].get("preferred_rate", 0),
                "Minimum Rate": data["salary"].get("minimum_rate", 0),
                "Currency": data["salary"].get("currency", "USD"),
                "Availability (hrs/wk)": data["salary"].get("availability", 0)
            }
            results["salary_preferences"] = airtable_client.upsert_salary_preferences(
                applicant_record_id, salary_fields
            )
            logger.info(f"Upserted salary preferences for applicant {applicant_id}")
        
        logger.info(f"Successfully decompressed and upserted data for applicant {applicant_id}")
        return results
        
    except Exception as e:
        logger.error(f"Error decompressing data for applicant {applicant_id}: {e}")
        raise


def decompress_from_json_string(airtable_client, applicant_id: int, json_string: str) -> Dict[str, Any]:
    """
    Decompress data from a provided JSON string (instead of reading from Airtable).
    
    Args:
        airtable_client: AirtableClient instance
        applicant_id: Applicant ID number
        json_string: JSON string to decompress
        
    Returns:
        Dictionary with results of upsert operations
    """
    try:
        # Get applicant record
        applicant_record = airtable_client.get_applicant(applicant_id)
        if not applicant_record:
            raise ValueError(f"Applicant {applicant_id} not found")
        
        applicant_record_id = applicant_record["id"]
        
        # Parse JSON
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        
        # First, save the JSON to the applicant record
        airtable_client.update_record(
            "Applicants",
            applicant_record_id,
            {"Compressed JSON": json_string}
        )
        
        results = {}
        
        # Upsert Personal Details
        if "personal" in data and data["personal"]:
            personal_fields = {
                "Full Name": data["personal"].get("name", ""),
                "Email": data["personal"].get("email", ""),
                "Location": data["personal"].get("location", ""),
                "LinkedIn": data["personal"].get("linkedin", "")
            }
            results["personal_details"] = airtable_client.upsert_personal_details(
                applicant_record_id, personal_fields
            )
        
        # Upsert Work Experience
        if "experience" in data and isinstance(data["experience"], list):
            experience_records = []
            for exp in data["experience"]:
                exp_fields = {
                    "Company": exp.get("company", ""),
                    "Title": exp.get("title", ""),
                    "Start": exp.get("start", ""),
                    "End": exp.get("end", ""),
                    "Technologies": exp.get("technologies", "")
                }
                experience_records.append(exp_fields)
            
            if experience_records:
                results["work_experiences"] = airtable_client.upsert_work_experiences(
                    applicant_record_id, experience_records
                )
        
        # Upsert Salary Preferences
        if "salary" in data and data["salary"]:
            salary_fields = {
                "Preferred Rate": data["salary"].get("preferred_rate", 0),
                "Minimum Rate": data["salary"].get("minimum_rate", 0),
                "Currency": data["salary"].get("currency", "USD"),
                "Availability (hrs/wk)": data["salary"].get("availability", 0)
            }
            results["salary_preferences"] = airtable_client.upsert_salary_preferences(
                applicant_record_id, salary_fields
            )
        
        logger.info(f"Successfully decompressed and upserted data from JSON string for applicant {applicant_id}")
        return results
        
    except Exception as e:
        logger.error(f"Error decompressing from JSON string for applicant {applicant_id}: {e}")
        raise

