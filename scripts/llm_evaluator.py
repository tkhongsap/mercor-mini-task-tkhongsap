"""
LLM evaluation and enrichment for contractor applications.
Uses Anthropic Claude to analyze, score, and provide insights on applications.
"""

import json
import time
import hashlib
from typing import Dict, Optional, Tuple
from anthropic import Anthropic
from pyairtable import Api

from config import (
    AIRTABLE_API_KEY,
    AIRTABLE_BASE_ID,
    TABLE_APPLICANTS,
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    MAX_TOKENS,
    LLM_RETRY_ATTEMPTS,
    LLM_RETRY_DELAY,
    LLM_SUMMARY_MAX_WORDS,
    LLM_PROMPT_TEMPLATE,
    validate_config,
)


class LLMEvaluator:
    """Evaluates applicants using Anthropic Claude API."""

    def __init__(self):
        """Initialize the evaluator with API clients."""
        validate_config()
        self.anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.airtable_api = Api(AIRTABLE_API_KEY)
        self.base = self.airtable_api.base(AIRTABLE_BASE_ID)
        self.applicants_table = self.base.table(TABLE_APPLICANTS)

    def compute_json_hash(self, json_data: Dict) -> str:
        """
        Compute a hash of the JSON data for deduplication.

        Args:
            json_data: The applicant JSON data

        Returns:
            SHA256 hash of the JSON string
        """
        json_string = json.dumps(json_data, sort_keys=True)
        return hashlib.sha256(json_string.encode()).hexdigest()

    def check_if_already_evaluated(self, applicant_id: str, json_hash: str) -> bool:
        """
        Check if this JSON has already been evaluated to avoid redundant API calls.

        Args:
            applicant_id: Airtable record ID
            json_hash: Hash of the JSON data

        Returns:
            True if already evaluated with the same JSON
        """
        try:
            record = self.applicants_table.get(applicant_id)
            existing_hash = record['fields'].get('JSON Hash')

            return existing_hash == json_hash
        except Exception:
            return False

    def parse_llm_response(self, response_text: str) -> Tuple[Optional[str], Optional[int], Optional[str], Optional[str]]:
        """
        Parse the structured LLM response.

        Expected format:
        Summary: <text>
        Score: <integer>
        Issues: <comma-separated list or 'None'>
        Follow-Ups: <bullet list>

        Args:
            response_text: Raw text response from Claude

        Returns:
            Tuple of (summary, score, issues, follow_ups)
        """
        lines = response_text.strip().split('\n')

        summary = None
        score = None
        issues = None
        follow_ups = []

        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith('Summary:'):
                summary = line.replace('Summary:', '').strip()
                current_section = 'summary'
            elif line.startswith('Score:'):
                try:
                    score_str = line.replace('Score:', '').strip()
                    score = int(score_str)
                except ValueError:
                    score = None
                current_section = 'score'
            elif line.startswith('Issues:'):
                issues = line.replace('Issues:', '').strip()
                current_section = 'issues'
            elif line.startswith('Follow-Ups:') or line.startswith('Follow-ups:'):
                current_section = 'follow_ups'
            elif current_section == 'follow_ups' and line:
                # Collect bullet points for follow-ups
                follow_ups.append(line)

        # Join follow-ups into a single string
        follow_ups_text = '\n'.join(follow_ups) if follow_ups else None

        return summary, score, issues, follow_ups_text

    def evaluate_with_llm(self, json_data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Evaluate applicant using Claude API with retry logic.

        Args:
            json_data: Compressed JSON applicant data

        Returns:
            Tuple of (evaluation_results, error_message)
        """
        prompt = LLM_PROMPT_TEMPLATE.format(
            max_words=LLM_SUMMARY_MAX_WORDS,
            json_data=json.dumps(json_data, indent=2)
        )

        for attempt in range(LLM_RETRY_ATTEMPTS):
            try:
                # Call Anthropic API
                message = self.anthropic_client.messages.create(
                    model=CLAUDE_MODEL,
                    max_tokens=MAX_TOKENS,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                # Extract text from response
                response_text = message.content[0].text

                # Parse the response
                summary, score, issues, follow_ups = self.parse_llm_response(response_text)

                # Validate parsed data
                if not summary or score is None:
                    raise ValueError("Failed to parse LLM response correctly")

                return {
                    'summary': summary,
                    'score': score,
                    'issues': issues,
                    'follow_ups': follow_ups,
                    'raw_response': response_text,
                }, None

            except Exception as e:
                error_msg = f"Attempt {attempt + 1}/{LLM_RETRY_ATTEMPTS} failed: {str(e)}"
                print(error_msg)

                if attempt < LLM_RETRY_ATTEMPTS - 1:
                    # Exponential backoff
                    delay = LLM_RETRY_DELAY * (2 ** attempt)
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    return None, f"All retry attempts failed. Last error: {str(e)}"

        return None, "Unexpected error in retry logic"

    def update_applicant_with_llm_results(
        self,
        applicant_id: str,
        evaluation: Dict,
        json_hash: str
    ):
        """
        Update the Applicants table with LLM evaluation results.

        Args:
            applicant_id: Airtable record ID
            evaluation: Evaluation results from LLM
            json_hash: Hash of the JSON data
        """
        update_fields = {
            'LLM Summary': evaluation['summary'],
            'LLM Score': evaluation['score'],
            'LLM Follow-Ups': evaluation.get('follow_ups', 'None'),
            'JSON Hash': json_hash,  # Store hash for deduplication
        }

        # Only add issues if they exist
        if evaluation.get('issues'):
            update_fields['LLM Issues'] = evaluation['issues']

        self.applicants_table.update(applicant_id, update_fields)

    def process_applicant(self, applicant_id: str, json_data: Dict, force: bool = False) -> Dict:
        """
        Process a single applicant through LLM evaluation.

        Args:
            applicant_id: Airtable record ID
            json_data: Compressed JSON data
            force: Force re-evaluation even if already evaluated

        Returns:
            Dictionary with processing results
        """
        # Compute hash for deduplication
        json_hash = self.compute_json_hash(json_data)

        # Check if already evaluated (unless forced)
        if not force and self.check_if_already_evaluated(applicant_id, json_hash):
            print(f"Applicant {applicant_id} already evaluated with this JSON. Skipping.")
            return {
                'applicant_id': applicant_id,
                'status': 'skipped',
                'reason': 'Already evaluated with identical JSON'
            }

        print(f"Evaluating applicant {applicant_id} with Claude...")

        # Call LLM
        evaluation, error = self.evaluate_with_llm(json_data)

        if error:
            print(f"Error evaluating applicant {applicant_id}: {error}")
            return {
                'applicant_id': applicant_id,
                'status': 'error',
                'error': error
            }

        # Update Airtable
        self.update_applicant_with_llm_results(applicant_id, evaluation, json_hash)

        print(f"✓ Applicant {applicant_id} evaluated successfully")
        print(f"  Score: {evaluation['score']}/10")
        print(f"  Summary: {evaluation['summary'][:100]}...")

        return {
            'applicant_id': applicant_id,
            'status': 'success',
            'evaluation': evaluation
        }


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python llm_evaluator.py <applicant_id> [--force]")
        sys.exit(1)

    applicant_id = sys.argv[1]
    force = '--force' in sys.argv

    # Load from Applicants table
    evaluator = LLMEvaluator()
    record = evaluator.applicants_table.get(applicant_id)

    compressed_json = record['fields'].get('Compressed JSON')
    if not compressed_json:
        print(f"Error: No compressed JSON found for applicant {applicant_id}")
        sys.exit(1)

    json_data = json.loads(compressed_json)
    result = evaluator.process_applicant(applicant_id, json_data, force=force)

    print(f"\nLLM Evaluation Result:")
    print(json.dumps(result, indent=2))
