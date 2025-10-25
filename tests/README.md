# Airtable Schema Setup Tests

This directory contains integration tests for validating the Airtable schema setup script.

## Overview

The tests verify that:
- Personal Details table is created with correct field types and links
- Work Experience table has proper date formatting and field structure
- Salary Preferences table includes correct number precision and currency choices
- Shortlisted Leads table has proper datetime configuration
- All tables properly link to the Applicants table
- The complete schema setup creates all relationships correctly

## Prerequisites

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your `.env` file contains valid Airtable credentials:
```
AIRTABLE_PERSONAL_ACCESS_TOKEN=your_token_here
AIRTABLE_BASE_ID=your_base_id_here
```

3. Ensure the Applicants table exists in your base (created by the main setup script)

## Running the Tests

### Run all schema tests:
```bash
pytest tests/test_setup_airtable_schema.py -v
```

### Run specific test class:
```bash
pytest tests/test_setup_airtable_schema.py::TestPersonalDetailsTable -v
```

### Run a specific test:
```bash
pytest tests/test_setup_airtable_schema.py::TestPersonalDetailsTable::test_personal_details_table_structure -v
```

### Run only integration tests (marked tests):
```bash
pytest tests/test_setup_airtable_schema.py -m integration -v
```

### Run with more detailed output:
```bash
pytest tests/test_setup_airtable_schema.py -vv -s
```

## Test Structure

### Test Files

- **`conftest.py`**: Pytest fixtures for Airtable connections and test table management
- **`test_helpers.py`**: Utility functions for validating field schemas
- **`test_setup_airtable_schema.py`**: Main integration tests for schema validation

### Test Classes

1. **TestPersonalDetailsTable**: Validates Personal Details table schema
2. **TestWorkExperienceTable**: Validates Work Experience table schema
3. **TestSalaryPreferencesTable**: Validates Salary Preferences table schema
4. **TestShortlistedLeadsTable**: Validates Shortlisted Leads table schema
5. **TestCompleteSchemaSetup**: Integration test for all tables together

## How Tests Work

1. **Setup**: Each test creates temporary tables with "_TEST" suffix in your Airtable base
2. **Validation**: Tests verify field types, options, links, and relationships
3. **Cleanup**: **Manual deletion required** - Airtable's API does not support automatic table deletion

### ⚠️ Important: Manual Cleanup Required

**Airtable's Meta API does NOT support table deletion.** After running tests, you must manually delete test tables through the web interface:

1. Visit your Airtable base: https://airtable.com/YOUR_BASE_ID
2. Delete any tables with "_TEST" suffix in their names
3. The test output will list exactly which tables need deletion

This is a limitation of Airtable's API, not our test framework.

## Important Notes

- **Real API Calls**: These are integration tests that make actual Airtable API calls
- **Temporary Tables**: Tests create and delete tables with "_TEST" suffix
- **Safe to Run**: Tests do not modify existing tables (except Applicants_TEST)
- **Credentials Required**: Tests require valid Airtable credentials in `.env`

## What Gets Tested

### Field Types
- Single line text fields
- Email fields
- URL fields
- Date fields with US format (M/D/YYYY)
- DateTime fields with UTC timezone and 12-hour format
- Number fields with specific precision (0 for integers, 2 for decimals)
- Single select fields with specific choices
- Multi-line text fields
- Checkbox fields
- Record link fields (relationships)

### Relationships
- One-to-one links (Personal Details → Applicants)
- One-to-many links (Work Experience → Applicants)
- Reverse link creation in Applicants table

### Integration
- All 4 tables can be created together
- Linked fields are automatically created in the parent table
- Table descriptions are set correctly

## Troubleshooting

### Test fails with "Missing credentials"
- Check that your `.env` file exists and contains valid credentials
- Verify the credentials have proper scopes (schema.bases:read, schema.bases:write, etc.)

### Test fails with "Applicants table not found"
- Run the main setup script first to create the Applicants table
- Or manually create an Applicants table in your base

### Test cleanup fails
- If test tables aren't deleted, manually delete any tables with "_TEST" suffix
- Check that your PAT has permission to delete tables

### Tests are slow
- This is normal for integration tests that make real API calls
- Each table creation/deletion requires an API round trip
- Consider running specific test classes instead of all tests

## Example Output

```
$ pytest tests/test_setup_airtable_schema.py -v

tests/test_setup_airtable_schema.py::TestPersonalDetailsTable::test_personal_details_table_structure PASSED
tests/test_setup_airtable_schema.py::TestWorkExperienceTable::test_work_experience_table_structure PASSED
tests/test_setup_airtable_schema.py::TestSalaryPreferencesTable::test_salary_preferences_table_structure PASSED
tests/test_setup_airtable_schema.py::TestShortlistedLeadsTable::test_shortlisted_leads_table_structure PASSED
tests/test_setup_airtable_schema.py::TestCompleteSchemaSetup::test_all_tables_created_successfully PASSED
tests/test_setup_airtable_schema.py::test_schema_matches_prd_requirements PASSED

============================== 6 passed in 45.23s ===============================
```
