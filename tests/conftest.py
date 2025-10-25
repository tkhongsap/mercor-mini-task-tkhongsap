#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Airtable schema tests
"""

import os
import pytest
from dotenv import load_dotenv
from pyairtable import Api


@pytest.fixture(scope="session")
def airtable_credentials():
    """
    Load Airtable credentials from .env file
    
    Returns:
        dict: Contains 'pat' and 'base_id'
    """
    load_dotenv()
    
    pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    
    if not pat or not base_id:
        pytest.fail("Missing AIRTABLE_PERSONAL_ACCESS_TOKEN or AIRTABLE_BASE_ID in .env file")
    
    return {
        'pat': pat,
        'base_id': base_id
    }


@pytest.fixture(scope="session")
def airtable_api(airtable_credentials):
    """
    Create Airtable API connection
    
    Returns:
        Api: Connected Airtable API instance
    """
    try:
        api = Api(airtable_credentials['pat'])
        return api
    except Exception as e:
        pytest.fail(f"Failed to connect to Airtable: {e}")


@pytest.fixture(scope="session")
def airtable_base(airtable_api, airtable_credentials):
    """
    Get Airtable base instance
    
    Returns:
        Base: Airtable base instance
    """
    try:
        base = airtable_api.base(airtable_credentials['base_id'])
        return base
    except Exception as e:
        pytest.fail(f"Failed to access Airtable base: {e}")


@pytest.fixture(scope="session")
def applicants_table_id(airtable_base):
    """
    Get the ID of the existing Applicants table
    
    Returns:
        str: Table ID for Applicants table
    """
    try:
        schema = airtable_base.schema()
        for table in schema.tables:
            if table.name == "Applicants":
                return table.id
        pytest.fail("Applicants table not found in base")
    except Exception as e:
        pytest.fail(f"Failed to get Applicants table ID: {e}")


@pytest.fixture(scope="function")
def test_table_tracker():
    """
    Track tables created during tests for cleanup
    
    Yields:
        list: List to store table IDs for cleanup
    """
    created_tables = []
    yield created_tables
    # Cleanup happens in individual test teardown


@pytest.fixture(scope="function")
def create_test_table(airtable_base, airtable_credentials):
    """
    Factory fixture to create test tables
    
    NOTE: Airtable's Meta API does NOT support table deletion via API.
    Test tables must be manually deleted through the Airtable web interface.
    All test tables are created with "_TEST" suffix for easy identification.
    
    Yields:
        function: Function that creates tables and tracks them
    """
    created_tables = []
    
    def _create_table(name: str, fields: list, description: str = ""):
        """Create a table and track it (manual cleanup required)"""
        try:
            table = airtable_base.create_table(name, fields, description)
            created_tables.append({"id": table.id, "name": table.name})
            return table
        except Exception as e:
            raise Exception(f"Failed to create table '{name}': {e}")
    
    yield _create_table
    
    # NOTE: Automatic cleanup is not possible via API
    # Print list of tables that need manual deletion
    if created_tables:
        print("\n" + "=" * 60)
        print("⚠️  MANUAL CLEANUP REQUIRED")
        print("=" * 60)
        print("The following test tables were created and must be")
        print("manually deleted through the Airtable web interface:")
        print()
        for table in created_tables:
            print(f"  • {table['name']} (ID: {table['id']})")
        print()
        print(f"Visit: https://airtable.com/{airtable_credentials['base_id']}")
        print("=" * 60)


@pytest.fixture(scope="function")
def temp_applicants_table(airtable_base, applicants_table_id):
    """
    Use the existing Applicants table for testing (simpler and more realistic)
    
    Returns:
        A simple object with the ID of the existing Applicants table
    """
    class TableRef:
        def __init__(self, table_id):
            self.id = table_id
            self.name = "Applicants"
    
    return TableRef(applicants_table_id)


def pytest_configure(config):
    """Add custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test that calls real Airtable API"
    )


