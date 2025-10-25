#!/usr/bin/env python3
"""
Quick script to delete the Shortlisted Leads table so we can recreate it
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

def main():
    print("Deleting Shortlisted Leads table...")

    load_dotenv()
    pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID')

    api = Api(pat)
    base = api.base(base_id)

    schema = base.schema()
    for table in schema.tables:
        if table.name == "Shortlisted Leads":
            print(f"Found table: {table.name} (ID: {table.id})")
            print("Deleting...")
            base.delete_table(table.id)
            print("Table deleted successfully!")
            return

    print("Shortlisted Leads table not found")

if __name__ == "__main__":
    main()
