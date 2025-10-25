#!/usr/bin/env python3
"""
Unit Tests for Airtable Schema Setup

Tests the setup_airtable_schema.py script and validates the actual Airtable
schema against PRD requirements.

Usage:
    python -m unittest tests.test_schema_setup
    python tests/test_schema_setup.py
"""

import os
import unittest
from dotenv import load_dotenv
from pyairtable import Api


class TestAirtableSchemaSetup(unittest.TestCase):
    """Test suite for Airtable schema setup and validation"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures - runs once before all tests"""
        load_dotenv()
        cls.pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
        cls.base_id = os.getenv('AIRTABLE_BASE_ID')

        if not cls.pat or not cls.base_id:
            raise ValueError("Missing AIRTABLE_PERSONAL_ACCESS_TOKEN or AIRTABLE_BASE_ID in .env")

        cls.api = Api(cls.pat)
        cls.base = cls.api.base(cls.base_id)
        cls.schema = cls.base.schema()

        # Index tables by name for easy access
        cls.tables = {table.name: table for table in cls.schema.tables}

    def test_environment_variables_loaded(self):
        """Test that required environment variables are present"""
        self.assertIsNotNone(self.pat, "AIRTABLE_PERSONAL_ACCESS_TOKEN not loaded")
        self.assertIsNotNone(self.base_id, "AIRTABLE_BASE_ID not loaded")
        self.assertTrue(self.pat.startswith('pat'), "PAT should start with 'pat'")
        self.assertTrue(self.base_id.startswith('app'), "Base ID should start with 'app'")

    def test_airtable_connection(self):
        """Test that we can connect to Airtable and fetch schema"""
        self.assertIsNotNone(self.schema, "Failed to fetch schema from Airtable")
        self.assertGreater(len(self.schema.tables), 0, "No tables found in base")

    def test_all_required_tables_exist(self):
        """Test that all 5 required tables exist"""
        required_tables = [
            "Applicants",
            "Personal Details",
            "Work Experience",
            "Salary Preferences",
            "Shortlisted Leads"
        ]

        for table_name in required_tables:
            self.assertIn(table_name, self.tables,
                         f"Required table '{table_name}' not found in base")

    def test_table_count(self):
        """Test that we have exactly 5 tables (no extras)"""
        self.assertEqual(len(self.tables), 5,
                        f"Expected 5 tables, found {len(self.tables)}")


class TestApplicantsTable(unittest.TestCase):
    """Test suite for Applicants table schema"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        load_dotenv()
        pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
        base_id = os.getenv('AIRTABLE_BASE_ID')
        api = Api(pat)
        base = api.base(base_id)
        schema = base.schema()

        cls.applicants = None
        for table in schema.tables:
            if table.name == "Applicants":
                cls.applicants = table
                break

        cls.fields = {field.name: field for field in cls.applicants.fields}

    def test_applicants_table_exists(self):
        """Test Applicants table exists"""
        self.assertIsNotNone(self.applicants, "Applicants table not found")

    def test_applicants_required_fields(self):
        """Test Applicants table has all required fields"""
        required_fields = [
            "Applicant ID",
            "Compressed JSON",
            "Shortlist Status",
            "LLM Summary",
            "LLM Score",
            "LLM Follow-Ups"
        ]

        for field_name in required_fields:
            self.assertIn(field_name, self.fields,
                         f"Required field '{field_name}' missing from Applicants table")

    def test_applicant_id_field_type(self):
        """Test Applicant ID is auto number type"""
        field = self.fields.get("Applicant ID")
        self.assertIsNotNone(field)
        self.assertEqual(field.type, "autoNumber",
                        "Applicant ID should be autoNumber type")

    def test_compressed_json_field_type(self):
        """Test Compressed JSON is multiline text"""
        field = self.fields.get("Compressed JSON")
        self.assertIsNotNone(field)
        self.assertEqual(field.type, "multilineText",
                        "Compressed JSON should be multilineText type")

    def test_shortlist_status_field_type(self):
        """Test Shortlist Status is checkbox"""
        field = self.fields.get("Shortlist Status")
        self.assertIsNotNone(field)
        self.assertEqual(field.type, "checkbox",
                        "Shortlist Status should be checkbox type")

    def test_llm_summary_field_type(self):
        """Test LLM Summary is rich text"""
        field = self.fields.get("LLM Summary")
        self.assertIsNotNone(field)
        self.assertIn(field.type, ["richText", "multilineText"],
                     "LLM Summary should be richText or multilineText")

    def test_llm_score_field_type(self):
        """Test LLM Score is number"""
        field = self.fields.get("LLM Score")
        self.assertIsNotNone(field)
        self.assertEqual(field.type, "number",
                        "LLM Score should be number type")

    def test_llm_followups_field_type(self):
        """Test LLM Follow-Ups is rich text"""
        field = self.fields.get("LLM Follow-Ups")
        self.assertIsNotNone(field)
        self.assertIn(field.type, ["richText", "multilineText"],
                     "LLM Follow-Ups should be richText or multilineText")

    def test_applicants_has_linked_fields(self):
        """Test Applicants table has linked record fields to child tables"""
        expected_links = [
            "Personal Details",
            "Work Experience",
            "Salary Preferences",
            "Shortlisted Leads"
        ]

        for link_name in expected_links:
            self.assertIn(link_name, self.fields,
                         f"Applicants should have linked field '{link_name}'")
            field = self.fields[link_name]
            self.assertEqual(field.type, "multipleRecordLinks",
                           f"'{link_name}' should be multipleRecordLinks type")


class TestPersonalDetailsTable(unittest.TestCase):
    """Test suite for Personal Details table schema"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        load_dotenv()
        pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
        base_id = os.getenv('AIRTABLE_BASE_ID')
        api = Api(pat)
        base = api.base(base_id)
        schema = base.schema()

        cls.table = None
        for table in schema.tables:
            if table.name == "Personal Details":
                cls.table = table
                break

        cls.fields = {field.name: field for field in cls.table.fields}

    def test_personal_details_required_fields(self):
        """Test Personal Details has all required fields"""
        required_fields = ["Full Name", "Email", "Location", "LinkedIn", "Applicant ID"]

        for field_name in required_fields:
            self.assertIn(field_name, self.fields,
                         f"Required field '{field_name}' missing from Personal Details")

    def test_field_count(self):
        """Test Personal Details has exactly 5 fields"""
        self.assertEqual(len(self.fields), 5,
                        f"Personal Details should have 5 fields, found {len(self.fields)}")

    def test_full_name_type(self):
        """Test Full Name is single line text"""
        field = self.fields.get("Full Name")
        self.assertEqual(field.type, "singleLineText")

    def test_email_type(self):
        """Test Email is email type"""
        field = self.fields.get("Email")
        self.assertEqual(field.type, "email")

    def test_location_type(self):
        """Test Location is single line text"""
        field = self.fields.get("Location")
        self.assertEqual(field.type, "singleLineText")

    def test_linkedin_type(self):
        """Test LinkedIn is URL type"""
        field = self.fields.get("LinkedIn")
        self.assertEqual(field.type, "url")

    def test_applicant_id_link(self):
        """Test Applicant ID is linked to Applicants table"""
        field = self.fields.get("Applicant ID")
        self.assertEqual(field.type, "multipleRecordLinks")


class TestWorkExperienceTable(unittest.TestCase):
    """Test suite for Work Experience table schema"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        load_dotenv()
        pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
        base_id = os.getenv('AIRTABLE_BASE_ID')
        api = Api(pat)
        base = api.base(base_id)
        schema = base.schema()

        cls.table = None
        for table in schema.tables:
            if table.name == "Work Experience":
                cls.table = table
                break

        cls.fields = {field.name: field for field in cls.table.fields}

    def test_work_experience_required_fields(self):
        """Test Work Experience has all required fields"""
        required_fields = [
            "Company", "Title", "Start", "End", "Technologies", "Applicant ID"
        ]

        for field_name in required_fields:
            self.assertIn(field_name, self.fields,
                         f"Required field '{field_name}' missing from Work Experience")

    def test_field_count(self):
        """Test Work Experience has exactly 6 fields"""
        self.assertEqual(len(self.fields), 6,
                        f"Work Experience should have 6 fields, found {len(self.fields)}")

    def test_company_type(self):
        """Test Company is single line text"""
        field = self.fields.get("Company")
        self.assertEqual(field.type, "singleLineText")

    def test_title_type(self):
        """Test Title is single line text"""
        field = self.fields.get("Title")
        self.assertEqual(field.type, "singleLineText")

    def test_start_type(self):
        """Test Start is date type"""
        field = self.fields.get("Start")
        self.assertEqual(field.type, "date")

    def test_end_type(self):
        """Test End is date type"""
        field = self.fields.get("End")
        self.assertEqual(field.type, "date")

    def test_technologies_type(self):
        """Test Technologies is single line text"""
        field = self.fields.get("Technologies")
        self.assertEqual(field.type, "singleLineText")

    def test_applicant_id_link(self):
        """Test Applicant ID is linked to Applicants table"""
        field = self.fields.get("Applicant ID")
        self.assertEqual(field.type, "multipleRecordLinks")


class TestSalaryPreferencesTable(unittest.TestCase):
    """Test suite for Salary Preferences table schema"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        load_dotenv()
        pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
        base_id = os.getenv('AIRTABLE_BASE_ID')
        api = Api(pat)
        base = api.base(base_id)
        schema = base.schema()

        cls.table = None
        for table in schema.tables:
            if table.name == "Salary Preferences":
                cls.table = table
                break

        cls.fields = {field.name: field for field in cls.table.fields}

    def test_salary_preferences_required_fields(self):
        """Test Salary Preferences has all required fields"""
        required_fields = [
            "Preferred Rate", "Minimum Rate", "Currency",
            "Availability (hrs/wk)", "Applicant ID"
        ]

        for field_name in required_fields:
            self.assertIn(field_name, self.fields,
                         f"Required field '{field_name}' missing from Salary Preferences")

    def test_field_count(self):
        """Test Salary Preferences has exactly 5 fields"""
        self.assertEqual(len(self.fields), 5,
                        f"Salary Preferences should have 5 fields, found {len(self.fields)}")

    def test_preferred_rate_type(self):
        """Test Preferred Rate is number with precision 2"""
        field = self.fields.get("Preferred Rate")
        self.assertEqual(field.type, "number")
        if hasattr(field.options, 'precision'):
            self.assertEqual(field.options.precision, 2)

    def test_minimum_rate_type(self):
        """Test Minimum Rate is number with precision 2"""
        field = self.fields.get("Minimum Rate")
        self.assertEqual(field.type, "number")
        if hasattr(field.options, 'precision'):
            self.assertEqual(field.options.precision, 2)

    def test_currency_type(self):
        """Test Currency is single select"""
        field = self.fields.get("Currency")
        self.assertEqual(field.type, "singleSelect")

    def test_currency_choices(self):
        """Test Currency has correct choices"""
        field = self.fields.get("Currency")
        if hasattr(field.options, 'choices'):
            choice_names = [choice.name for choice in field.options.choices]
            expected_currencies = ["USD", "EUR", "GBP", "CAD", "INR"]
            for currency in expected_currencies:
                self.assertIn(currency, choice_names,
                            f"Currency '{currency}' should be in choices")

    def test_availability_type(self):
        """Test Availability is number with precision 0"""
        field = self.fields.get("Availability (hrs/wk)")
        self.assertEqual(field.type, "number")
        if hasattr(field.options, 'precision'):
            self.assertEqual(field.options.precision, 0)

    def test_applicant_id_link(self):
        """Test Applicant ID is linked to Applicants table"""
        field = self.fields.get("Applicant ID")
        self.assertEqual(field.type, "multipleRecordLinks")


class TestShortlistedLeadsTable(unittest.TestCase):
    """Test suite for Shortlisted Leads table schema"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        load_dotenv()
        pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
        base_id = os.getenv('AIRTABLE_BASE_ID')
        api = Api(pat)
        base = api.base(base_id)
        schema = base.schema()

        cls.table = None
        for table in schema.tables:
            if table.name == "Shortlisted Leads":
                cls.table = table
                break

        cls.fields = {field.name: field for field in cls.table.fields}

    def test_shortlisted_leads_required_fields(self):
        """Test Shortlisted Leads has all required fields"""
        required_fields = ["Applicant", "Compressed JSON", "Score Reason", "Created At"]

        for field_name in required_fields:
            self.assertIn(field_name, self.fields,
                         f"Required field '{field_name}' missing from Shortlisted Leads")

    def test_field_count(self):
        """Test Shortlisted Leads has exactly 4 fields"""
        self.assertEqual(len(self.fields), 4,
                        f"Shortlisted Leads should have 4 fields, found {len(self.fields)}")

    def test_applicant_link_type(self):
        """Test Applicant is linked to Applicants table"""
        field = self.fields.get("Applicant")
        self.assertEqual(field.type, "multipleRecordLinks")

    def test_compressed_json_type(self):
        """Test Compressed JSON is multiline text"""
        field = self.fields.get("Compressed JSON")
        self.assertEqual(field.type, "multilineText")

    def test_score_reason_type(self):
        """Test Score Reason is multiline text"""
        field = self.fields.get("Score Reason")
        self.assertEqual(field.type, "multilineText")

    def test_created_at_type(self):
        """Test Created At is dateTime"""
        field = self.fields.get("Created At")
        self.assertEqual(field.type, "dateTime")


class TestLinkedRelationships(unittest.TestCase):
    """Test suite for bidirectional linked relationships"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        load_dotenv()
        pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
        base_id = os.getenv('AIRTABLE_BASE_ID')
        api = Api(pat)
        base = api.base(base_id)
        cls.schema = base.schema()
        cls.tables = {table.name: table for table in cls.schema.tables}

    def test_applicants_has_all_child_links(self):
        """Test Applicants table has linked fields to all child tables"""
        applicants = self.tables["Applicants"]
        field_names = [f.name for f in applicants.fields]

        expected_links = [
            "Personal Details",
            "Work Experience",
            "Salary Preferences",
            "Shortlisted Leads"
        ]

        for link in expected_links:
            self.assertIn(link, field_names,
                         f"Applicants should have link to '{link}'")

    def test_personal_details_links_to_applicants(self):
        """Test Personal Details has Applicant ID link"""
        table = self.tables["Personal Details"]
        field_names = [f.name for f in table.fields]
        self.assertIn("Applicant ID", field_names)

    def test_work_experience_links_to_applicants(self):
        """Test Work Experience has Applicant ID link"""
        table = self.tables["Work Experience"]
        field_names = [f.name for f in table.fields]
        self.assertIn("Applicant ID", field_names)

    def test_salary_preferences_links_to_applicants(self):
        """Test Salary Preferences has Applicant ID link"""
        table = self.tables["Salary Preferences"]
        field_names = [f.name for f in table.fields]
        self.assertIn("Applicant ID", field_names)

    def test_shortlisted_leads_links_to_applicants(self):
        """Test Shortlisted Leads has Applicant link"""
        table = self.tables["Shortlisted Leads"]
        field_names = [f.name for f in table.fields]
        self.assertIn("Applicant", field_names)


class TestPRDCompliance(unittest.TestCase):
    """Test suite for overall PRD compliance"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        load_dotenv()
        pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
        base_id = os.getenv('AIRTABLE_BASE_ID')
        api = Api(pat)
        base = api.base(base_id)
        cls.schema = base.schema()
        cls.tables = {table.name: table for table in cls.schema.tables}

    def test_prd_table_count(self):
        """Test we have exactly 5 tables as per PRD"""
        self.assertEqual(len(self.tables), 5,
                        "PRD requires exactly 5 tables")

    def test_prd_applicants_compliance(self):
        """Test Applicants table matches PRD specification"""
        applicants = self.tables["Applicants"]
        field_names = [f.name for f in applicants.fields]

        required = [
            "Applicant ID", "Compressed JSON", "Shortlist Status",
            "LLM Summary", "LLM Score", "LLM Follow-Ups"
        ]

        for field in required:
            self.assertIn(field, field_names,
                         f"PRD requires '{field}' in Applicants table")

    def test_prd_personal_details_compliance(self):
        """Test Personal Details matches PRD specification"""
        table = self.tables["Personal Details"]
        field_names = [f.name for f in table.fields]

        required = ["Full Name", "Email", "Location", "LinkedIn", "Applicant ID"]

        for field in required:
            self.assertIn(field, field_names,
                         f"PRD requires '{field}' in Personal Details table")

    def test_prd_work_experience_compliance(self):
        """Test Work Experience matches PRD specification"""
        table = self.tables["Work Experience"]
        field_names = [f.name for f in table.fields]

        required = ["Company", "Title", "Start", "End", "Technologies", "Applicant ID"]

        for field in required:
            self.assertIn(field, field_names,
                         f"PRD requires '{field}' in Work Experience table")

    def test_prd_salary_preferences_compliance(self):
        """Test Salary Preferences matches PRD specification"""
        table = self.tables["Salary Preferences"]
        field_names = [f.name for f in table.fields]

        required = [
            "Preferred Rate", "Minimum Rate", "Currency",
            "Availability (hrs/wk)", "Applicant ID"
        ]

        for field in required:
            self.assertIn(field, field_names,
                         f"PRD requires '{field}' in Salary Preferences table")

    def test_prd_shortlisted_leads_compliance(self):
        """Test Shortlisted Leads matches PRD specification"""
        table = self.tables["Shortlisted Leads"]
        field_names = [f.name for f in table.fields]

        required = ["Applicant", "Compressed JSON", "Score Reason", "Created At"]

        for field in required:
            self.assertIn(field, field_names,
                         f"PRD requires '{field}' in Shortlisted Leads table")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
