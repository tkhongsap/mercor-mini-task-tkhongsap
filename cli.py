#!/usr/bin/env python3
"""
Unified CLI interface for Airtable Contractor Application System.
Provides commands for all operations: compress, decompress, evaluate, and process-all.
"""

import sys
import logging
import argparse
from src.config import get_config
from src.airtable_client import AirtableClient
from src.json_compressor import compress_and_save
from src.json_decompressor import decompress_applicant_data
from src.shortlist_evaluator import process_shortlist
from src.llm_evaluator import process_llm_evaluation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_compress(args, airtable_client):
    """Execute compress command."""
    if args.applicant_id:
        applicant_ids = [args.applicant_id]
    else:
        # Get all applicants
        all_applicants = airtable_client.get_all_records("Applicants")
        applicant_ids = [
            app.get("fields", {}).get("Applicant ID")
            for app in all_applicants
            if app.get("fields", {}).get("Applicant ID")
        ]
        logger.info(f"Found {len(applicant_ids)} applicants to compress")
    
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
    
    logger.info(f"\nCompression complete: {success_count} success, {failed_count} failed")
    return failed_count == 0


def cmd_decompress(args, airtable_client):
    """Execute decompress command."""
    if not args.applicant_id:
        logger.error("--applicant-id is required for decompress command")
        return False
    
    try:
        logger.info(f"Decompressing data for applicant {args.applicant_id}...")
        results = decompress_applicant_data(airtable_client, args.applicant_id)
        
        logger.info(f"✓ Successfully decompressed applicant {args.applicant_id}")
        
        if "personal_details" in results:
            logger.info("  - Updated Personal Details")
        if "work_experiences" in results:
            count = len(results["work_experiences"])
            logger.info(f"  - Updated {count} Work Experience record(s)")
        if "salary_preferences" in results:
            logger.info("  - Updated Salary Preferences")
        
        return True
    except Exception as e:
        logger.error(f"✗ Failed to decompress applicant {args.applicant_id}: {e}")
        return False


def cmd_evaluate(args, airtable_client, config):
    """Execute evaluate command."""
    if args.applicant_id:
        applicant_ids = [args.applicant_id]
    else:
        # Get all applicants with compressed JSON
        all_applicants = airtable_client.get_all_records("Applicants")
        applicant_ids = [
            app.get("fields", {}).get("Applicant ID")
            for app in all_applicants
            if app.get("fields", {}).get("Applicant ID")
            and app.get("fields", {}).get("Compressed JSON")
        ]
        logger.info(f"Found {len(applicant_ids)} applicants to evaluate")
    
    success_count = 0
    failed_count = 0
    shortlisted_count = 0
    
    for app_id in applicant_ids:
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Evaluating applicant {app_id}")
            logger.info(f"{'='*60}")
            
            # Shortlist evaluation
            logger.info("Running shortlist evaluation...")
            shortlist_result = process_shortlist(airtable_client, app_id)
            
            if shortlist_result["is_qualified"]:
                logger.info(f"✓ Applicant {app_id} SHORTLISTED")
                shortlisted_count += 1
            else:
                logger.info(f"✗ Applicant {app_id} NOT shortlisted")
            
            # LLM evaluation (unless skipped)
            if not args.skip_llm:
                logger.info("\nRunning LLM evaluation...")
                llm_result = process_llm_evaluation(
                    airtable_client,
                    config.openai_api_key,
                    app_id
                )
                
                if llm_result.get("skipped"):
                    logger.info(f"⊘ LLM evaluation skipped")
                else:
                    evaluation = llm_result["evaluation"]
                    logger.info(f"✓ LLM Score: {evaluation['score']}/10")
            
            success_count += 1
            
        except Exception as e:
            logger.error(f"✗ Failed to evaluate applicant {app_id}: {e}")
            failed_count += 1
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Evaluation Summary")
    logger.info(f"{'='*60}")
    logger.info(f"Success: {success_count}")
    logger.info(f"Failed: {failed_count}")
    logger.info(f"Shortlisted: {shortlisted_count}")
    
    return failed_count == 0


def cmd_process_all(args, airtable_client, config):
    """Execute process-all command (full pipeline)."""
    logger.info("="*60)
    logger.info("FULL PIPELINE EXECUTION")
    logger.info("="*60)
    
    # Step 1: Compress all applicants
    logger.info("\nStep 1: Compressing all applicants...")
    compress_args = argparse.Namespace(applicant_id=None)
    if not cmd_compress(compress_args, airtable_client):
        logger.error("Compression failed, stopping pipeline")
        return False
    
    # Step 2: Evaluate all applicants
    logger.info("\nStep 2: Evaluating all applicants...")
    eval_args = argparse.Namespace(applicant_id=None, skip_llm=False)
    if not cmd_evaluate(eval_args, airtable_client, config):
        logger.error("Evaluation failed")
        return False
    
    logger.info("\n" + "="*60)
    logger.info("PIPELINE COMPLETE")
    logger.info("="*60)
    return True


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Airtable Contractor Application System - Unified CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  compress         Compress applicant data into JSON
  decompress       Decompress JSON back to tables
  evaluate         Evaluate candidates (shortlist + LLM)
  process-all      Run full pipeline (compress + evaluate)

Examples:
  python cli.py compress --applicant-id 1
  python cli.py compress  # Compress all applicants
  python cli.py decompress --applicant-id 1
  python cli.py evaluate --applicant-id 1
  python cli.py evaluate --skip-llm  # Only shortlist evaluation
  python cli.py process-all  # Full pipeline
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Compress command
    compress_parser = subparsers.add_parser('compress', help='Compress applicant data')
    compress_parser.add_argument('--applicant-id', type=int, help='Specific applicant ID (omit for all)')
    
    # Decompress command
    decompress_parser = subparsers.add_parser('decompress', help='Decompress JSON to tables')
    decompress_parser.add_argument('--applicant-id', type=int, required=True, help='Applicant ID to decompress')
    
    # Evaluate command
    evaluate_parser = subparsers.add_parser('evaluate', help='Evaluate candidates')
    evaluate_parser.add_argument('--applicant-id', type=int, help='Specific applicant ID (omit for all)')
    evaluate_parser.add_argument('--skip-llm', action='store_true', help='Skip LLM evaluation')
    
    # Process-all command
    subparsers.add_parser('process-all', help='Run full pipeline')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = get_config()
        
        # Initialize Airtable client
        logger.info("Initializing Airtable client...")
        airtable_client = AirtableClient(config.airtable_pat, config.airtable_base_id)
        
        # Execute command
        if args.command == 'compress':
            success = cmd_compress(args, airtable_client)
        elif args.command == 'decompress':
            success = cmd_decompress(args, airtable_client)
        elif args.command == 'evaluate':
            success = cmd_evaluate(args, airtable_client, config)
        elif args.command == 'process-all':
            success = cmd_process_all(args, airtable_client, config)
        else:
            logger.error(f"Unknown command: {args.command}")
            sys.exit(1)
        
        if not success:
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

