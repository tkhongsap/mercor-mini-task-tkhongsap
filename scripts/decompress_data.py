#!/usr/bin/env python3
"""
Standalone script to decompress JSON back into Airtable tables.
"""

import sys
import os
import logging
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import get_config
from src.airtable_client import AirtableClient
from src.json_decompressor import decompress_applicant_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to decompress applicant data."""
    parser = argparse.ArgumentParser(
        description='Decompress JSON data back into Airtable tables'
    )
    parser.add_argument(
        '--applicant-id',
        type=int,
        required=True,
        help='Applicant ID to decompress'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = get_config()
        
        # Initialize Airtable client
        logger.info("Initializing Airtable client...")
        airtable_client = AirtableClient(config.airtable_pat, config.airtable_base_id)
        
        # Decompress applicant data
        logger.info(f"Decompressing data for applicant {args.applicant_id}...")
        results = decompress_applicant_data(airtable_client, args.applicant_id)
        
        # Display results
        logger.info(f"✓ Successfully decompressed applicant {args.applicant_id}")
        
        if "personal_details" in results:
            logger.info("  - Updated Personal Details")
        
        if "work_experiences" in results:
            count = len(results["work_experiences"])
            logger.info(f"  - Updated {count} Work Experience record(s)")
        
        if "salary_preferences" in results:
            logger.info("  - Updated Salary Preferences")
        
        logger.info("\nDecompression complete!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

