#!/usr/bin/env python3
"""
Quick test to verify Airtable authentication works
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

def main():
    print("Testing Airtable Authentication...")
    print()

    # Load environment variables
    load_dotenv()

    pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID')

    if not pat:
        print("ERROR: AIRTABLE_PERSONAL_ACCESS_TOKEN not found in .env")
        return False

    if not base_id:
        print("ERROR: AIRTABLE_BASE_ID not found in .env")
        return False

    print(f"✓ PAT loaded: {pat[:10]}...")
    print(f"✓ Base ID: {base_id}")
    print()

    # Try to connect
    print("Connecting to Airtable...")
    try:
        api = Api(pat)
        base = api.base(base_id)
        print("✓ Connection successful!")
        print()

        # Try to get schema
        print("Fetching base schema...")
        schema = base.schema()
        print(f"✓ Schema retrieved successfully!")
        print()

        print("Tables in your base:")
        for i, table in enumerate(schema.tables, 1):
            print(f"  {i}. {table.name} (ID: {table.id})")

        print()
        print("=" * 60)
        print("SUCCESS! Authentication is working correctly.")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        print()
        print("Possible issues:")
        print("  1. PAT is incorrect or expired")
        print("  2. PAT doesn't have required scopes:")
        print("     - schema.bases:read")
        print("     - schema.bases:write")
        print("     - data.records:read")
        print("     - data.records:write")
        print("  3. PAT doesn't have access to this specific base")
        return False

if __name__ == "__main__":
    main()
