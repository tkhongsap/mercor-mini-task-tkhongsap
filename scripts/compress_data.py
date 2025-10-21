#!/usr/bin/env python3
"""
Standalone script to compress applicant data from Airtable tables into JSON.
"""

import sys
import os
import logging
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import get_config
from src.airtable_client import AirtableClient
from src.json_compressor import compress_and_save

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to compress applicant data."""
    parser = argparse.ArgumentParser(
        description='Compress applicant data from Airtable into JSON'
    )
    parser.add_argument(
        '--applicant-id',
        type=int,
        help='Specific applicant ID to compress (omit to compress all)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Compress all applicants'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = get_config()
        
        # Initialize Airtable client
        logger.info("Initializing Airtable client...")
        airtable_client = AirtableClient(config.airtable_pat, config.airtable_base_id)
        
        # Determine which applicants to compress
        if args.applicant_id:
            applicant_ids = [args.applicant_id]
        elif args.all:
            # Get all applicants
            all_applicants = airtable_client.get_all_records("Applicants")
            applicant_ids = [
                app.get("fields", {}).get("Applicant ID")
                for app in all_applicants
                if app.get("fields", {}).get("Applicant ID")
            ]
            logger.info(f"Found {len(applicant_ids)} applicants to compress")
        else:
            logger.error("Please specify --applicant-id <ID> or --all")
            sys.exit(1)
        
        # Compress each applicant
        success_count = 0
        failed_count = 0
        
        for app_id in applicant_ids:
            try:
                logger.info(f"Compressing data for applicant {app_id}...")
                compress_and_save(airtable_client, app_id)
                logger.info(f"✓ Successfully compressed applicant {app_id}")
                success_count += 1
            except Exception as e:
                logger.error(f"✗ Failed to compress applicant {app_id}: {e}")
                failed_count += 1
        
        # Summary
        logger.info(f"\nCompression complete:")
        logger.info(f"  Success: {success_count}")
        logger.info(f"  Failed: {failed_count}")
        
        if failed_count > 0:
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

