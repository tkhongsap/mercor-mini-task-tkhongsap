#!/usr/bin/env python3
"""
Standalone script to evaluate candidates for shortlisting and LLM analysis.
"""

import sys
import os
import logging
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import get_config
from src.airtable_client import AirtableClient
from src.shortlist_evaluator import process_shortlist
from src.llm_evaluator import process_llm_evaluation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to evaluate candidates."""
    parser = argparse.ArgumentParser(
        description='Evaluate candidates for shortlisting and LLM analysis'
    )
    parser.add_argument(
        '--applicant-id',
        type=int,
        help='Specific applicant ID to evaluate (omit to evaluate all)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Evaluate all applicants'
    )
    parser.add_argument(
        '--skip-llm',
        action='store_true',
        help='Skip LLM evaluation (only do shortlist evaluation)'
    )
    parser.add_argument(
        '--llm-only',
        action='store_true',
        help='Only run LLM evaluation (skip shortlist evaluation)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = get_config()
        
        # Initialize Airtable client
        logger.info("Initializing Airtable client...")
        airtable_client = AirtableClient(config.airtable_pat, config.airtable_base_id)
        
        # Determine which applicants to evaluate
        if args.applicant_id:
            applicant_ids = [args.applicant_id]
        elif args.all:
            # Get all applicants with compressed JSON
            all_applicants = airtable_client.get_all_records("Applicants")
            applicant_ids = [
                app.get("fields", {}).get("Applicant ID")
                for app in all_applicants
                if app.get("fields", {}).get("Applicant ID") 
                and app.get("fields", {}).get("Compressed JSON")
            ]
            logger.info(f"Found {len(applicant_ids)} applicants to evaluate")
        else:
            logger.error("Please specify --applicant-id <ID> or --all")
            sys.exit(1)
        
        # Evaluate each applicant
        success_count = 0
        failed_count = 0
        shortlisted_count = 0
        
        for app_id in applicant_ids:
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Evaluating applicant {app_id}")
                logger.info(f"{'='*60}")
                
                # Shortlist evaluation
                if not args.llm_only:
                    logger.info("Running shortlist evaluation...")
                    shortlist_result = process_shortlist(airtable_client, app_id)
                    
                    if shortlist_result["is_qualified"]:
                        logger.info(f"✓ Applicant {app_id} SHORTLISTED")
                        shortlisted_count += 1
                    else:
                        logger.info(f"✗ Applicant {app_id} NOT shortlisted")
                    
                    logger.info(f"\nReason:\n{shortlist_result['reason']}")
                
                # LLM evaluation
                if not args.skip_llm:
                    logger.info("\nRunning LLM evaluation...")
                    llm_result = process_llm_evaluation(
                        airtable_client,
                        config.openai_api_key,
                        app_id
                    )
                    
                    if llm_result.get("skipped"):
                        logger.info(f"⊘ LLM evaluation skipped: {llm_result['reason']}")
                    else:
                        evaluation = llm_result["evaluation"]
                        logger.info(f"✓ LLM Score: {evaluation['score']}/10")
                        logger.info(f"Summary: {evaluation['summary'][:100]}...")
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"✗ Failed to evaluate applicant {app_id}: {e}")
                failed_count += 1
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info("Evaluation Summary")
        logger.info(f"{'='*60}")
        logger.info(f"Total processed: {len(applicant_ids)}")
        logger.info(f"Success: {success_count}")
        logger.info(f"Failed: {failed_count}")
        if not args.llm_only:
            logger.info(f"Shortlisted: {shortlisted_count}")
        
        if failed_count > 0:
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

