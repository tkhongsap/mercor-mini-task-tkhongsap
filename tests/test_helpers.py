#!/usr/bin/env python3
"""
Helper utilities for validating Airtable schema configurations
"""

from typing import Dict, List, Any, Optional


def validate_field_exists(fields: List[Any], field_name: str) -> Any:
    """
    Check if a field exists in the table schema and return it
    
    Args:
        fields: List of field objects from Airtable schema
        field_name: Name of the field to find
        
    Returns:
        The field object if found
        
    Raises:
        AssertionError: If field is not found
    """
    field = next((f for f in fields if f.name == field_name), None)
    assert field is not None, f"Field '{field_name}' not found in table"
    return field


def validate_field_type(field: Any, expected_type: str) -> None:
    """
    Validate that a field has the expected type
    
    Args:
        field: Field object from Airtable schema
        expected_type: Expected field type (e.g., 'singleLineText', 'email', etc.)
        
    Raises:
        AssertionError: If field type doesn't match
    """
    assert field.type == expected_type, \
        f"Field '{field.name}' has type '{field.type}', expected '{expected_type}'"


def validate_link_field(field: Any, linked_table_id: str) -> None:
    """
    Validate that a multipleRecordLinks field links to the correct table
    
    Args:
        field: Field object from Airtable schema
        linked_table_id: Expected linked table ID
        
    Raises:
        AssertionError: If field is not a link or links to wrong table
    """
    assert field.type == "multipleRecordLinks", \
        f"Field '{field.name}' is not a multipleRecordLinks field"
    assert hasattr(field.options, 'linked_table_id'), \
        f"Field '{field.name}' has no linked_table_id"
    assert field.options.linked_table_id == linked_table_id, \
        f"Field '{field.name}' links to '{field.options.linked_table_id}', expected '{linked_table_id}'"


def validate_number_precision(field: Any, expected_precision: int) -> None:
    """
    Validate that a number field has the correct precision
    
    Args:
        field: Field object from Airtable schema
        expected_precision: Expected precision (0 for integer, 2 for decimal, etc.)
        
    Raises:
        AssertionError: If precision doesn't match
    """
    assert field.type == "number", f"Field '{field.name}' is not a number field"
    assert hasattr(field.options, 'precision'), \
        f"Field '{field.name}' has no precision attribute"
    assert field.options.precision == expected_precision, \
        f"Field '{field.name}' has precision {field.options.precision}, expected {expected_precision}"


def validate_single_select_choices(field: Any, expected_choices: List[str]) -> None:
    """
    Validate that a singleSelect field has the correct choices
    
    Args:
        field: Field object from Airtable schema
        expected_choices: List of expected choice names
        
    Raises:
        AssertionError: If choices don't match
    """
    assert field.type == "singleSelect", f"Field '{field.name}' is not a singleSelect field"
    assert hasattr(field.options, 'choices'), \
        f"Field '{field.name}' has no choices attribute"
    
    actual_choices = [choice.name for choice in field.options.choices]
    assert set(actual_choices) == set(expected_choices), \
        f"Field '{field.name}' has choices {actual_choices}, expected {expected_choices}"


def validate_date_format(field: Any, expected_format: str) -> None:
    """
    Validate that a date field has the correct format
    
    Args:
        field: Field object from Airtable schema
        expected_format: Expected date format (e.g., 'M/D/YYYY')
        
    Raises:
        AssertionError: If date format doesn't match
    """
    assert field.type == "date", f"Field '{field.name}' is not a date field"
    assert hasattr(field.options, 'date_format'), \
        f"Field '{field.name}' has no date_format attribute"
    assert field.options.date_format.format == expected_format, \
        f"Field '{field.name}' has format '{field.options.date_format.format}', expected '{expected_format}'"


def validate_datetime_config(field: Any, expected_timezone: str = "utc", 
                            expected_time_format: str = "12hour") -> None:
    """
    Validate that a dateTime field has the correct configuration
    
    Args:
        field: Field object from Airtable schema
        expected_timezone: Expected timezone (default: 'utc')
        expected_time_format: Expected time format (default: '12hour')
        
    Raises:
        AssertionError: If configuration doesn't match
    """
    assert field.type == "dateTime", f"Field '{field.name}' is not a dateTime field"
    assert hasattr(field.options, 'time_zone'), \
        f"Field '{field.name}' has no time_zone attribute"
    assert field.options.time_zone == expected_timezone, \
        f"Field '{field.name}' has timezone '{field.options.time_zone}', expected '{expected_timezone}'"
    assert hasattr(field.options, 'time_format'), \
        f"Field '{field.name}' has no time_format attribute"
    assert field.options.time_format.name == expected_time_format, \
        f"Field '{field.name}' has time format '{field.options.time_format.name}', expected '{expected_time_format}'"


def validate_table_field_count(table: Any, expected_count: int) -> None:
    """
    Validate that a table has the expected number of fields
    
    Args:
        table: Table object from Airtable schema
        expected_count: Expected number of fields
        
    Raises:
        AssertionError: If field count doesn't match
    """
    actual_count = len(table.fields)
    assert actual_count == expected_count, \
        f"Table '{table.name}' has {actual_count} fields, expected {expected_count}"


def get_field_names(table: Any) -> List[str]:
    """
    Get list of all field names in a table
    
    Args:
        table: Table object from Airtable schema
        
    Returns:
        List of field names
    """
    return [field.name for field in table.fields]


