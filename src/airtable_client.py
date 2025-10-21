"""
Airtable API client wrapper for Contractor Application System.
Provides methods for interacting with Airtable tables.
"""

from pyairtable import Api
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AirtableClient:
    """Wrapper class for Airtable API operations."""
    
    def __init__(self, personal_access_token: str, base_id: str):
        """
        Initialize Airtable client.
        
        Args:
            personal_access_token: Airtable Personal Access Token
            base_id: Airtable Base ID
        """
        self.api = Api(personal_access_token)
        self.base = self.api.base(base_id)
        self.base_id = base_id
        
        logger.info(f"Initialized Airtable client for base: {base_id}")
    
    def get_table(self, table_name: str):
        """
        Get a table object.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Table object
        """
        return self.base.table(table_name)
    
    def get_all_records(self, table_name: str, formula: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all records from a table.
        
        Args:
            table_name: Name of the table
            formula: Optional Airtable formula to filter records
            
        Returns:
            List of record dictionaries
        """
        try:
            table = self.get_table(table_name)
            if formula:
                records = table.all(formula=formula)
            else:
                records = table.all()
            logger.info(f"Retrieved {len(records)} records from {table_name}")
            return records
        except Exception as e:
            logger.error(f"Error retrieving records from {table_name}: {e}")
            raise
    
    def get_record(self, table_name: str, record_id: str) -> Dict[str, Any]:
        """
        Get a single record by ID.
        
        Args:
            table_name: Name of the table
            record_id: Record ID
            
        Returns:
            Record dictionary
        """
        try:
            table = self.get_table(table_name)
            record = table.get(record_id)
            logger.info(f"Retrieved record {record_id} from {table_name}")
            return record
        except Exception as e:
            logger.error(f"Error retrieving record {record_id} from {table_name}: {e}")
            raise
    
    def get_applicant(self, applicant_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an applicant record by Applicant ID.
        
        Args:
            applicant_id: Applicant ID number
            
        Returns:
            Applicant record or None if not found
        """
        try:
            formula = f"{{Applicant ID}} = {applicant_id}"
            records = self.get_all_records("Applicants", formula=formula)
            if records:
                return records[0]
            return None
        except Exception as e:
            logger.error(f"Error retrieving applicant {applicant_id}: {e}")
            raise
    
    def get_personal_details(self, applicant_record_id: str) -> Optional[Dict[str, Any]]:
        """
        Get personal details linked to an applicant.
        
        Args:
            applicant_record_id: Airtable record ID of the applicant
            
        Returns:
            Personal details record or None if not found
        """
        try:
            formula = f"FIND('{applicant_record_id}', ARRAYJOIN({{Applicant ID}})) > 0"
            records = self.get_all_records("Personal Details", formula=formula)
            if records:
                return records[0]
            return None
        except Exception as e:
            logger.error(f"Error retrieving personal details for applicant {applicant_record_id}: {e}")
            raise
    
    def get_work_experiences(self, applicant_record_id: str) -> List[Dict[str, Any]]:
        """
        Get all work experience records linked to an applicant.
        
        Args:
            applicant_record_id: Airtable record ID of the applicant
            
        Returns:
            List of work experience records
        """
        try:
            formula = f"FIND('{applicant_record_id}', ARRAYJOIN({{Applicant ID}})) > 0"
            records = self.get_all_records("Work Experience", formula=formula)
            return records
        except Exception as e:
            logger.error(f"Error retrieving work experiences for applicant {applicant_record_id}: {e}")
            raise
    
    def get_salary_preferences(self, applicant_record_id: str) -> Optional[Dict[str, Any]]:
        """
        Get salary preferences linked to an applicant.
        
        Args:
            applicant_record_id: Airtable record ID of the applicant
            
        Returns:
            Salary preferences record or None if not found
        """
        try:
            formula = f"FIND('{applicant_record_id}', ARRAYJOIN({{Applicant ID}})) > 0"
            records = self.get_all_records("Salary Preferences", formula=formula)
            if records:
                return records[0]
            return None
        except Exception as e:
            logger.error(f"Error retrieving salary preferences for applicant {applicant_record_id}: {e}")
            raise
    
    def update_record(self, table_name: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a record in a table.
        
        Args:
            table_name: Name of the table
            record_id: Record ID
            fields: Dictionary of fields to update
            
        Returns:
            Updated record
        """
        try:
            table = self.get_table(table_name)
            updated_record = table.update(record_id, fields)
            logger.info(f"Updated record {record_id} in {table_name}")
            return updated_record
        except Exception as e:
            logger.error(f"Error updating record {record_id} in {table_name}: {e}")
            raise
    
    def create_record(self, table_name: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record in a table.
        
        Args:
            table_name: Name of the table
            fields: Dictionary of fields for the new record
            
        Returns:
            Created record
        """
        try:
            table = self.get_table(table_name)
            created_record = table.create(fields)
            logger.info(f"Created record in {table_name}")
            return created_record
        except Exception as e:
            logger.error(f"Error creating record in {table_name}: {e}")
            raise
    
    def delete_record(self, table_name: str, record_id: str) -> Dict[str, Any]:
        """
        Delete a record from a table.
        
        Args:
            table_name: Name of the table
            record_id: Record ID
            
        Returns:
            Deleted record information
        """
        try:
            table = self.get_table(table_name)
            deleted_record = table.delete(record_id)
            logger.info(f"Deleted record {record_id} from {table_name}")
            return deleted_record
        except Exception as e:
            logger.error(f"Error deleting record {record_id} from {table_name}: {e}")
            raise
    
    def upsert_personal_details(self, applicant_record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update personal details for an applicant.
        
        Args:
            applicant_record_id: Airtable record ID of the applicant
            fields: Dictionary of fields (must not include Applicant ID link)
            
        Returns:
            Created or updated record
        """
        existing = self.get_personal_details(applicant_record_id)
        
        # Add the applicant link
        fields["Applicant ID"] = [applicant_record_id]
        
        if existing:
            return self.update_record("Personal Details", existing["id"], fields)
        else:
            return self.create_record("Personal Details", fields)
    
    def upsert_salary_preferences(self, applicant_record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update salary preferences for an applicant.
        
        Args:
            applicant_record_id: Airtable record ID of the applicant
            fields: Dictionary of fields (must not include Applicant ID link)
            
        Returns:
            Created or updated record
        """
        existing = self.get_salary_preferences(applicant_record_id)
        
        # Add the applicant link
        fields["Applicant ID"] = [applicant_record_id]
        
        if existing:
            return self.update_record("Salary Preferences", existing["id"], fields)
        else:
            return self.create_record("Salary Preferences", fields)
    
    def upsert_work_experiences(self, applicant_record_id: str, experiences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Replace all work experience records for an applicant.
        Deletes existing records and creates new ones.
        
        Args:
            applicant_record_id: Airtable record ID of the applicant
            experiences: List of work experience dictionaries
            
        Returns:
            List of created records
        """
        # Delete existing work experiences
        existing_experiences = self.get_work_experiences(applicant_record_id)
        for exp in existing_experiences:
            self.delete_record("Work Experience", exp["id"])
        
        # Create new work experiences
        created_records = []
        for exp_fields in experiences:
            # Add the applicant link
            exp_fields["Applicant ID"] = [applicant_record_id]
            created_record = self.create_record("Work Experience", exp_fields)
            created_records.append(created_record)
        
        logger.info(f"Upserted {len(created_records)} work experiences for applicant {applicant_record_id}")
        return created_records
    
    def create_shortlisted_lead(self, applicant_record_id: str, compressed_json: str, score_reason: str) -> Dict[str, Any]:
        """
        Create a shortlisted lead record.
        
        Args:
            applicant_record_id: Airtable record ID of the applicant
            compressed_json: Compressed JSON string
            score_reason: Reason for shortlisting
            
        Returns:
            Created shortlisted lead record
        """
        fields = {
            "Applicant": [applicant_record_id],
            "Compressed JSON": compressed_json,
            "Score Reason": score_reason
        }
        return self.create_record("Shortlisted Leads", fields)

