#!/usr/bin/env python3
"""
Clean up any leftover test tables from test runs
"""

import os
import sys
import requests
from dotenv import load_dotenv
from pyairtable import Api

def main():
    load_dotenv()
    
    pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    
    if not pat or not base_id:
        print("ERROR: Missing credentials in .env")
        sys.exit(1)
    
    # Get all tables
    api = Api(pat)
    base = api.base(base_id)
    schema = base.schema()
    
    print("Looking for test tables to clean up...")
    deleted_count = 0
    
    for table in schema.tables:
        if "_TEST" in table.name:
            print(f"Deleting: {table.name} (ID: {table.id})")
            url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table.id}"
            headers = {"Authorization": f"Bearer {pat}"}
            response = requests.delete(url, headers=headers)
            
            if response.status_code in [200, 204]:
                print(f"  ✓ Deleted successfully")
                deleted_count += 1
            else:
                print(f"  ✗ Failed: {response.status_code} - {response.text}")
    
    if deleted_count == 0:
        print("No test tables found to clean up")
    else:
        print(f"\n✓ Cleaned up {deleted_count} test table(s)")

if __name__ == "__main__":
    main()

