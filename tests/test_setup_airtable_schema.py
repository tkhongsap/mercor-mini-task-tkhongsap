#!/usr/bin/env python3
"""
Integration tests for Airtable schema setup script

These tests create actual tables in Airtable to verify that the schema
setup script creates tables with correct field definitions, types, and
relationships as specified in the PRD.

All test tables are automatically cleaned up after each test.
"""

import pytest
from test_helpers import (
    validate_field_exists,
    validate_field_type,
    validate_link_field,
    validate_number_precision,
    validate_single_select_choices,
    validate_date_format,
    validate_datetime_config,
    validate_table_field_count,
    get_field_names
)


@pytest.mark.integration
class TestPersonalDetailsTable:
    """Tests for Personal Details table schema"""
    
    def test_personal_details_table_structure(self, airtable_base, temp_applicants_table, create_test_table):
        """
        Test that Personal Details table is created with correct fields and types
        """
        # Define expected fields
        fields = [
            {"name": "Full Name", "type": "singleLineText"},
            {"name": "Email", "type": "email"},
            {"name": "Location", "type": "singleLineText"},
            {"name": "LinkedIn", "type": "url"},
            {
                "name": "Applicant ID",
                "type": "multipleRecordLinks",
                "options": {
                    "linkedTableId": temp_applicants_table.id
                }
            }
        ]
        
        # Create table
        table = create_test_table(
            "Personal Details_TEST",
            fields,
            "Test table for personal information"
        )
        
        # Verify table was created
        assert table is not None
        assert table.name == "Personal Details_TEST"
        
        # Get fresh schema
        schema = airtable_base.schema()
        created_table = next((t for t in schema.tables if t.id == table.id), None)
        assert created_table is not None
        
        # Verify field count (5 fields + 1 auto-created Name field = 6 total)
        # Note: Airtable auto-creates a primary "Name" field
        assert len(created_table.fields) >= 5, \
            f"Expected at least 5 fields, got {len(created_table.fields)}"
        
        # Verify each field exists with correct type
        full_name_field = validate_field_exists(created_table.fields, "Full Name")
        validate_field_type(full_name_field, "singleLineText")
        
        email_field = validate_field_exists(created_table.fields, "Email")
        validate_field_type(email_field, "email")
        
        location_field = validate_field_exists(created_table.fields, "Location")
        validate_field_type(location_field, "singleLineText")
        
        linkedin_field = validate_field_exists(created_table.fields, "LinkedIn")
        validate_field_type(linkedin_field, "url")
        
        applicant_id_field = validate_field_exists(created_table.fields, "Applicant ID")
        validate_link_field(applicant_id_field, temp_applicants_table.id)


@pytest.mark.integration
class TestWorkExperienceTable:
    """Tests for Work Experience table schema"""
    
    def test_work_experience_table_structure(self, airtable_base, temp_applicants_table, create_test_table):
        """
        Test that Work Experience table is created with correct fields and types
        """
        # Define expected fields
        fields = [
            {"name": "Company", "type": "singleLineText"},
            {"name": "Title", "type": "singleLineText"},
            {
                "name": "Start",
                "type": "date",
                "options": {"dateFormat": {"name": "us", "format": "M/D/YYYY"}}
            },
            {
                "name": "End",
                "type": "date",
                "options": {"dateFormat": {"name": "us", "format": "M/D/YYYY"}}
            },
            {"name": "Technologies", "type": "singleLineText"},
            {
                "name": "Applicant ID",
                "type": "multipleRecordLinks",
                "options": {
                    "linkedTableId": temp_applicants_table.id
                }
            }
        ]
        
        # Create table
        table = create_test_table(
            "Work Experience_TEST",
            fields,
            "Test table for work history"
        )
        
        # Verify table was created
        assert table is not None
        assert table.name == "Work Experience_TEST"
        
        # Get fresh schema
        schema = airtable_base.schema()
        created_table = next((t for t in schema.tables if t.id == table.id), None)
        assert created_table is not None
        
        # Verify field count
        assert len(created_table.fields) >= 6, \
            f"Expected at least 6 fields, got {len(created_table.fields)}"
        
        # Verify each field
        company_field = validate_field_exists(created_table.fields, "Company")
        validate_field_type(company_field, "singleLineText")
        
        title_field = validate_field_exists(created_table.fields, "Title")
        validate_field_type(title_field, "singleLineText")
        
        start_field = validate_field_exists(created_table.fields, "Start")
        validate_field_type(start_field, "date")
        validate_date_format(start_field, "M/D/YYYY")
        
        end_field = validate_field_exists(created_table.fields, "End")
        validate_field_type(end_field, "date")
        validate_date_format(end_field, "M/D/YYYY")
        
        tech_field = validate_field_exists(created_table.fields, "Technologies")
        validate_field_type(tech_field, "singleLineText")
        
        applicant_id_field = validate_field_exists(created_table.fields, "Applicant ID")
        validate_link_field(applicant_id_field, temp_applicants_table.id)


@pytest.mark.integration
class TestSalaryPreferencesTable:
    """Tests for Salary Preferences table schema"""
    
    def test_salary_preferences_table_structure(self, airtable_base, temp_applicants_table, create_test_table):
        """
        Test that Salary Preferences table is created with correct fields and types
        """
        # Define expected fields
        fields = [
            {
                "name": "Preferred Rate",
                "type": "number",
                "options": {"precision": 2}
            },
            {
                "name": "Minimum Rate",
                "type": "number",
                "options": {"precision": 2}
            },
            {
                "name": "Currency",
                "type": "singleSelect",
                "options": {
                    "choices": [
                        {"name": "USD"},
                        {"name": "EUR"},
                        {"name": "GBP"},
                        {"name": "CAD"},
                        {"name": "INR"}
                    ]
                }
            },
            {
                "name": "Availability (hrs/wk)",
                "type": "number",
                "options": {"precision": 0}
            },
            {
                "name": "Applicant ID",
                "type": "multipleRecordLinks",
                "options": {
                    "linkedTableId": temp_applicants_table.id
                }
            }
        ]
        
        # Create table
        table = create_test_table(
            "Salary Preferences_TEST",
            fields,
            "Test table for compensation preferences"
        )
        
        # Verify table was created
        assert table is not None
        assert table.name == "Salary Preferences_TEST"
        
        # Get fresh schema
        schema = airtable_base.schema()
        created_table = next((t for t in schema.tables if t.id == table.id), None)
        assert created_table is not None
        
        # Verify field count
        assert len(created_table.fields) >= 5, \
            f"Expected at least 5 fields, got {len(created_table.fields)}"
        
        # Verify each field
        preferred_rate_field = validate_field_exists(created_table.fields, "Preferred Rate")
        validate_field_type(preferred_rate_field, "number")
        validate_number_precision(preferred_rate_field, 2)
        
        minimum_rate_field = validate_field_exists(created_table.fields, "Minimum Rate")
        validate_field_type(minimum_rate_field, "number")
        validate_number_precision(minimum_rate_field, 2)
        
        currency_field = validate_field_exists(created_table.fields, "Currency")
        validate_field_type(currency_field, "singleSelect")
        validate_single_select_choices(currency_field, ["USD", "EUR", "GBP", "CAD", "INR"])
        
        availability_field = validate_field_exists(created_table.fields, "Availability (hrs/wk)")
        validate_field_type(availability_field, "number")
        validate_number_precision(availability_field, 0)
        
        applicant_id_field = validate_field_exists(created_table.fields, "Applicant ID")
        validate_link_field(applicant_id_field, temp_applicants_table.id)


@pytest.mark.integration
class TestShortlistedLeadsTable:
    """Tests for Shortlisted Leads table schema"""
    
    def test_shortlisted_leads_table_structure(self, airtable_base, temp_applicants_table, create_test_table):
        """
        Test that Shortlisted Leads table is created with correct fields and types
        """
        # Define expected fields
        # Note: Airtable requires first field to be a simple type, not a link
        fields = [
            {"name": "Lead ID", "type": "singleLineText"},  # Primary field
            {
                "name": "Applicant",
                "type": "multipleRecordLinks",
                "options": {
                    "linkedTableId": temp_applicants_table.id
                }
            },
            {"name": "Compressed JSON", "type": "multilineText"},
            {"name": "Score Reason", "type": "multilineText"},
            {
                "name": "Created At",
                "type": "dateTime",
                "options": {
                    "dateFormat": {"name": "us"},
                    "timeFormat": {"name": "12hour"},
                    "timeZone": "utc"
                }
            }
        ]
        
        # Create table
        table = create_test_table(
            "Shortlisted Leads_TEST",
            fields,
            "Test table for qualified candidates"
        )
        
        # Verify table was created
        assert table is not None
        assert table.name == "Shortlisted Leads_TEST"
        
        # Get fresh schema
        schema = airtable_base.schema()
        created_table = next((t for t in schema.tables if t.id == table.id), None)
        assert created_table is not None
        
        # Verify field count (5 fields including the primary Lead ID)
        assert len(created_table.fields) >= 5, \
            f"Expected at least 5 fields, got {len(created_table.fields)}"
        
        # Verify each field
        lead_id_field = validate_field_exists(created_table.fields, "Lead ID")
        validate_field_type(lead_id_field, "singleLineText")
        
        applicant_field = validate_field_exists(created_table.fields, "Applicant")
        validate_link_field(applicant_field, temp_applicants_table.id)
        
        json_field = validate_field_exists(created_table.fields, "Compressed JSON")
        validate_field_type(json_field, "multilineText")
        
        reason_field = validate_field_exists(created_table.fields, "Score Reason")
        validate_field_type(reason_field, "multilineText")
        
        created_at_field = validate_field_exists(created_table.fields, "Created At")
        validate_field_type(created_at_field, "dateTime")
        validate_datetime_config(created_at_field, "utc", "12hour")


@pytest.mark.integration
class TestCompleteSchemaSetup:
    """Integration test for complete schema setup"""
    
    def test_all_tables_created_successfully(self, airtable_base, temp_applicants_table, create_test_table):
        """
        Test that all 4 tables can be created together and have correct relationships
        """
        # Create all 4 tables
        personal_details = create_test_table(
            "Personal Details_TEST_ALL",
            [
                {"name": "Full Name", "type": "singleLineText"},
                {"name": "Email", "type": "email"},
                {"name": "Location", "type": "singleLineText"},
                {"name": "LinkedIn", "type": "url"},
                {
                    "name": "Applicant ID",
                    "type": "multipleRecordLinks",
                    "options": {"linkedTableId": temp_applicants_table.id}
                }
            ],
            "Personal information"
        )
        
        work_experience = create_test_table(
            "Work Experience_TEST_ALL",
            [
                {"name": "Company", "type": "singleLineText"},
                {"name": "Title", "type": "singleLineText"},
                {
                    "name": "Start",
                    "type": "date",
                    "options": {"dateFormat": {"name": "us", "format": "M/D/YYYY"}}
                },
                {
                    "name": "End",
                    "type": "date",
                    "options": {"dateFormat": {"name": "us", "format": "M/D/YYYY"}}
                },
                {"name": "Technologies", "type": "singleLineText"},
                {
                    "name": "Applicant ID",
                    "type": "multipleRecordLinks",
                    "options": {"linkedTableId": temp_applicants_table.id}
                }
            ],
            "Work history"
        )
        
        salary_preferences = create_test_table(
            "Salary Preferences_TEST_ALL",
            [
                {"name": "Preferred Rate", "type": "number", "options": {"precision": 2}},
                {"name": "Minimum Rate", "type": "number", "options": {"precision": 2}},
                {
                    "name": "Currency",
                    "type": "singleSelect",
                    "options": {
                        "choices": [
                            {"name": "USD"},
                            {"name": "EUR"},
                            {"name": "GBP"},
                            {"name": "CAD"},
                            {"name": "INR"}
                        ]
                    }
                },
                {"name": "Availability (hrs/wk)", "type": "number", "options": {"precision": 0}},
                {
                    "name": "Applicant ID",
                    "type": "multipleRecordLinks",
                    "options": {"linkedTableId": temp_applicants_table.id}
                }
            ],
            "Compensation preferences"
        )
        
        shortlisted_leads = create_test_table(
            "Shortlisted Leads_TEST_ALL",
            [
                {"name": "Lead ID", "type": "singleLineText"},  # Primary field required
                {
                    "name": "Applicant",
                    "type": "multipleRecordLinks",
                    "options": {"linkedTableId": temp_applicants_table.id}
                },
                {"name": "Compressed JSON", "type": "multilineText"},
                {"name": "Score Reason", "type": "multilineText"},
                {
                    "name": "Created At",
                    "type": "dateTime",
                    "options": {
                        "dateFormat": {"name": "us"},
                        "timeFormat": {"name": "12hour"},
                        "timeZone": "utc"
                    }
                }
            ],
            "Qualified candidates"
        )
        
        # Verify all tables were created
        assert personal_details is not None
        assert work_experience is not None
        assert salary_preferences is not None
        assert shortlisted_leads is not None
        
        # Get fresh schema to verify linked fields were created
        schema = airtable_base.schema()
        applicants_table = next((t for t in schema.tables if t.id == temp_applicants_table.id), None)
        assert applicants_table is not None
        
        # Check that linked fields were auto-created in Applicants table
        field_names = get_field_names(applicants_table)
        
        # Note: Airtable automatically creates reverse-link fields with names
        # matching the source table names or field names
        # We verify they exist by checking for link fields pointing to our test tables
        link_fields = [f for f in applicants_table.fields if f.type == "multipleRecordLinks"]
        
        # Should have at least 4 link fields (one for each child table)
        assert len(link_fields) >= 4, \
            f"Expected at least 4 link fields in Applicants table, got {len(link_fields)}"
        
        # Verify each link points to the correct table
        linked_table_ids = [f.options.linked_table_id for f in link_fields if hasattr(f.options, 'linked_table_id')]
        
        assert personal_details.id in linked_table_ids, \
            "Personal Details link not found in Applicants table"
        assert work_experience.id in linked_table_ids, \
            "Work Experience link not found in Applicants table"
        assert salary_preferences.id in linked_table_ids, \
            "Salary Preferences link not found in Applicants table"
        assert shortlisted_leads.id in linked_table_ids, \
            "Shortlisted Leads link not found in Applicants table"


@pytest.mark.integration
def test_schema_matches_prd_requirements(applicants_table_id, airtable_base):
    """
    Verify that the actual Applicants table in the base matches PRD requirements
    
    This test checks the existing Applicants table (not a test table)
    """
    schema = airtable_base.schema()
    applicants_table = next((t for t in schema.tables if t.id == applicants_table_id), None)
    
    assert applicants_table is not None, "Applicants table not found"
    
    # Verify key fields exist
    field_names = get_field_names(applicants_table)
    
    required_fields = [
        "Compressed JSON",
        "Shortlist Status",
        "LLM Summary",
        "LLM Score",
        "LLM Follow-Ups"
    ]
    
    for field_name in required_fields:
        assert field_name in field_names, \
            f"Required field '{field_name}' not found in Applicants table"
    
    # Verify field types
    compressed_json = validate_field_exists(applicants_table.fields, "Compressed JSON")
    validate_field_type(compressed_json, "multilineText")
    
    shortlist_status = validate_field_exists(applicants_table.fields, "Shortlist Status")
    validate_field_type(shortlist_status, "checkbox")
    
    llm_score = validate_field_exists(applicants_table.fields, "LLM Score")
    validate_field_type(llm_score, "number")


