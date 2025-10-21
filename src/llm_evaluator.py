"""
LLM evaluation module for Airtable Contractor Application System.
Uses OpenAI API to evaluate and enrich applicant data.
"""

import json
import logging
import time
from typing import Dict, Any, Optional, Tuple
from openai import OpenAI

logger = logging.getLogger(__name__)

# LLM prompt template as specified in PRD
EVALUATION_PROMPT_TEMPLATE = """You are a recruiting analyst. Given this JSON applicant profile, do four things:
1. Provide a concise 75-word summary.
2. Rate overall candidate quality from 1-10 (higher is better).
3. List any data gaps or inconsistencies you notice.
4. Suggest up to three follow-up questions to clarify gaps.

Applicant Profile JSON:
{json_data}

Return exactly:
Summary: <text>
Score: <integer>
Issues: <comma-separated list or 'None'>
Follow-Ups: <bullet list>
"""


def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Parse LLM response into structured fields.
    
    Args:
        response_text: Raw response text from LLM
        
    Returns:
        Dictionary with parsed fields: summary, score, issues, follow_ups
    """
    result = {
        "summary": "",
        "score": 0,
        "issues": "",
        "follow_ups": ""
    }
    
    lines = response_text.strip().split("\n")
    current_field = None
    
    for line in lines:
        line = line.strip()
        
        if line.startswith("Summary:"):
            result["summary"] = line.replace("Summary:", "").strip()
            current_field = "summary"
        elif line.startswith("Score:"):
            score_str = line.replace("Score:", "").strip()
            try:
                result["score"] = int(score_str)
            except ValueError:
                logger.warning(f"Could not parse score: {score_str}")
                result["score"] = 0
            current_field = None
        elif line.startswith("Issues:"):
            result["issues"] = line.replace("Issues:", "").strip()
            current_field = "issues"
        elif line.startswith("Follow-Ups:"):
            result["follow_ups"] = line.replace("Follow-Ups:", "").strip()
            current_field = "follow_ups"
        elif current_field and line:
            # Continue multi-line fields
            if current_field == "summary":
                result["summary"] += " " + line
            elif current_field == "issues":
                result["issues"] += " " + line
            elif current_field == "follow_ups":
                if result["follow_ups"]:
                    result["follow_ups"] += "\n" + line
                else:
                    result["follow_ups"] = line
    
    return result


def call_openai_with_retry(
    client: OpenAI,
    prompt: str,
    max_retries: int = 3,
    initial_delay: float = 1.0
) -> str:
    """
    Call OpenAI API with exponential backoff retry logic.
    
    Args:
        client: OpenAI client instance
        prompt: Prompt to send to the API
        max_retries: Maximum number of retry attempts (default 3)
        initial_delay: Initial delay in seconds before first retry
        
    Returns:
        Response text from the API
        
    Raises:
        Exception: If all retries fail
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Calling OpenAI API (attempt {attempt + 1}/{max_retries})")
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Using gpt-4o-mini as it's the latest mini model
                messages=[
                    {"role": "system", "content": "You are a professional recruiting analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,  # Budget guardrail: limit tokens per call
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content
            logger.info("OpenAI API call successful")
            return response_text
            
        except Exception as e:
            last_exception = e
            logger.warning(f"OpenAI API call failed (attempt {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                logger.error(f"All {max_retries} retry attempts failed")
    
    raise Exception(f"OpenAI API call failed after {max_retries} attempts: {last_exception}")


def evaluate_with_llm(
    openai_api_key: str,
    compressed_json: str,
    previous_json: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Evaluate applicant using LLM (OpenAI).
    
    Args:
        openai_api_key: OpenAI API key
        compressed_json: Compressed JSON string to evaluate
        previous_json: Previously evaluated JSON (to skip if unchanged)
        
    Returns:
        Dictionary with evaluation results: summary, score, issues, follow_ups
        Returns None if JSON unchanged from previous evaluation
    """
    try:
        # Skip if JSON unchanged (budget guardrail)
        if previous_json and compressed_json == previous_json:
            logger.info("JSON unchanged from previous evaluation, skipping LLM call")
            return None
        
        # Initialize OpenAI client
        client = OpenAI(api_key=openai_api_key)
        
        # Build prompt
        prompt = EVALUATION_PROMPT_TEMPLATE.format(json_data=compressed_json)
        
        # Call OpenAI with retry logic
        response_text = call_openai_with_retry(client, prompt, max_retries=3)
        
        # Parse response
        evaluation = parse_llm_response(response_text)
        
        logger.info(f"LLM evaluation complete: Score {evaluation['score']}/10")
        return evaluation
        
    except Exception as e:
        logger.error(f"Error during LLM evaluation: {e}")
        raise


def process_llm_evaluation(airtable_client, openai_api_key: str, applicant_id: int) -> Dict[str, Any]:
    """
    Process LLM evaluation for an applicant and update Airtable.
    
    Args:
        airtable_client: AirtableClient instance
        openai_api_key: OpenAI API key
        applicant_id: Applicant ID number
        
    Returns:
        Dictionary with evaluation results
    """
    try:
        # Get applicant record
        applicant_record = airtable_client.get_applicant(applicant_id)
        if not applicant_record:
            raise ValueError(f"Applicant {applicant_id} not found")
        
        applicant_record_id = applicant_record["id"]
        fields = applicant_record.get("fields", {})
        
        # Get compressed JSON
        compressed_json = fields.get("Compressed JSON", "")
        if not compressed_json:
            raise ValueError(f"No compressed JSON found for applicant {applicant_id}. Run compression first.")
        
        # Get previous LLM summary to check if evaluation already done
        previous_summary = fields.get("LLM Summary", "")
        
        # Note: We don't have a field to store the previous JSON used for evaluation,
        # so we'll always evaluate if the summary is empty or re-evaluate if compressed JSON changed
        # In a production system, you'd want to store a hash or the previous JSON
        
        # Evaluate with LLM
        evaluation = evaluate_with_llm(openai_api_key, compressed_json)
        
        if evaluation is None:
            logger.info(f"Skipped LLM evaluation for applicant {applicant_id} (unchanged)")
            return {
                "applicant_id": applicant_id,
                "skipped": True,
                "reason": "JSON unchanged from previous evaluation"
            }
        
        # Update Airtable with LLM results
        update_fields = {
            "LLM Summary": evaluation["summary"],
            "LLM Score": evaluation["score"],
            "LLM Follow-Ups": evaluation["follow_ups"]
        }
        
        airtable_client.update_record("Applicants", applicant_record_id, update_fields)
        
        logger.info(f"Updated LLM evaluation results for applicant {applicant_id}")
        
        return {
            "applicant_id": applicant_id,
            "skipped": False,
            "evaluation": evaluation
        }
        
    except Exception as e:
        logger.error(f"Error processing LLM evaluation for applicant {applicant_id}: {e}")
        raise


def batch_evaluate_applicants(
    airtable_client,
    openai_api_key: str,
    applicant_ids: Optional[list] = None
) -> Dict[str, Any]:
    """
    Batch evaluate multiple applicants with LLM.
    
    Args:
        airtable_client: AirtableClient instance
        openai_api_key: OpenAI API key
        applicant_ids: List of applicant IDs (None = all applicants)
        
    Returns:
        Dictionary with batch results
    """
    results = {
        "success": [],
        "failed": [],
        "skipped": []
    }
    
    # Get applicants to evaluate
    if applicant_ids:
        applicants_to_evaluate = []
        for app_id in applicant_ids:
            applicant = airtable_client.get_applicant(app_id)
            if applicant:
                applicants_to_evaluate.append(applicant)
    else:
        # Get all applicants with compressed JSON
        all_applicants = airtable_client.get_all_records("Applicants")
        applicants_to_evaluate = [
            app for app in all_applicants 
            if app.get("fields", {}).get("Compressed JSON", "")
        ]
    
    logger.info(f"Evaluating {len(applicants_to_evaluate)} applicants with LLM")
    
    for applicant in applicants_to_evaluate:
        app_id = applicant.get("fields", {}).get("Applicant ID")
        
        try:
            result = process_llm_evaluation(airtable_client, openai_api_key, app_id)
            
            if result.get("skipped"):
                results["skipped"].append(app_id)
            else:
                results["success"].append(app_id)
                
        except Exception as e:
            logger.error(f"Failed to evaluate applicant {app_id}: {e}")
            results["failed"].append({"applicant_id": app_id, "error": str(e)})
    
    logger.info(
        f"Batch evaluation complete: "
        f"{len(results['success'])} successful, "
        f"{len(results['skipped'])} skipped, "
        f"{len(results['failed'])} failed"
    )
    
    return results

