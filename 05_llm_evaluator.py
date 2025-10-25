#!/usr/bin/env python3
"""
LLM Evaluator - Airtable Contractor Application System

Uses OpenAI Responses API to evaluate ALL applicants and enrich their applications
with AI-generated summaries, scores, and follow-up questions.

Per PRD Section 6.2: Trigger is "After Compressed JSON is written OR updated"
This means ALL applicants are evaluated, not just shortlisted ones.

Reads Compressed JSON from Applicants table, sends to OpenAI, and writes results
to LLM Summary, LLM Score, and LLM Follow-Ups fields in Applicants table.

Usage:
    python llm_evaluator.py                 # Evaluate ALL applicants
    python llm_evaluator.py --id <id>       # Evaluate single applicant
    python llm_evaluator.py --force         # Re-evaluate even if already processed
"""

import os
import sys
import json
import time
import argparse
from typing import Optional, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from pyairtable import Api
from openai import OpenAI, APIError, RateLimitError, APIConnectionError


class LLMEvaluation(BaseModel):
    """Structured output model for LLM evaluation responses."""
    summary: str = Field(
        description="Concise 75-word summary of the candidate's profile"
    )
    score: int = Field(
        ge=1, le=10,
        description="Overall candidate quality score from 1-10 (higher is better)"
    )
    issues: str = Field(
        description="Comma-separated list of data gaps or inconsistencies, or 'None'"
    )
    follow_ups: str = Field(
        description="Bullet list of 1-3 follow-up questions to clarify gaps"
    )


LLM_JSON_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "llm_evaluation",
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["summary", "score", "issues", "follow_ups"],
            "properties": {
                "summary": {"type": "string"},
                "score": {"type": "integer", "minimum": 1, "maximum": 10},
                "issues": {"type": "string"},
                "follow_ups": {"type": "string"},
            },
        },
        "strict": True,
    },
}


def _extract_message_text(content: Any) -> str:
    """
    Normalize chat completion message content into a plain string.
    """
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict):
                if part.get("type") == "text" and "text" in part:
                    text_parts.append(part["text"])
                elif "content" in part and isinstance(part["content"], str):
                    text_parts.append(part["content"])
        return "\n".join(t.strip() for t in text_parts if t and t.strip())

    return str(content).strip()


def call_openai_with_retry(
    client: OpenAI,
    applicant_data: dict,
    max_retries: int = 3
) -> Optional[LLMEvaluation]:
    """
    Call OpenAI Responses API with retry logic and exponential backoff.

    Args:
        client: OpenAI client instance
        applicant_data: Parsed JSON data of the applicant
        max_retries: Maximum number of retry attempts

    Returns:
        LLMEvaluation object or None if all retries fail
    """
    # Build prompt input
    json_data = json.dumps(applicant_data, indent=2)

    instructions = """You are a recruiting analyst evaluating contractor applications.

Analyze the candidate's profile and provide:
1. A concise 75-word summary highlighting key strengths and fit
2. An overall quality score from 1-10 (higher is better)
3. Any data gaps or inconsistencies you notice
4. Up to 3 follow-up questions to clarify gaps or gather more info

Focus on technical skills, experience relevance, and professional background."""

    input_text = f"""Evaluate this contractor application:

{json_data}

Provide your evaluation in the requested format."""

    supports_responses_api = hasattr(client, "responses") and hasattr(
        getattr(client, "responses", None), "parse"
    )

    for attempt in range(max_retries):
        try:
            print(f"    Calling OpenAI API (attempt {attempt + 1}/{max_retries})...")

            if supports_responses_api:
                response = client.responses.parse(
                    model="gpt-4o-mini",
                    instructions=instructions,
                    input=input_text,
                    text_format=LLMEvaluation,
                )

                # Extract parsed structured output
                if hasattr(response, 'output_parsed') and response.output_parsed:
                    print(f"    ✓ OpenAI API call successful")
                    return response.output_parsed
                else:
                    print(f"    ✗ Unexpected response format: {type(response)}")
                    print(f"    Available attrs: {[x for x in dir(response) if not x.startswith('_')][:10]}")
                    return None
            else:
                # Fallback to Chat Completions with JSON schema response format
                chat_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": instructions},
                        {"role": "user", "content": input_text},
                    ],
                    response_format=LLM_JSON_RESPONSE_FORMAT,
                    temperature=0.3,
                    max_tokens=600,
                )

                message = chat_response.choices[0].message
                content_text = _extract_message_text(message.content)
                if not content_text:
                    print("    ✗ Empty response content")
                    return None

                parsed = LLMEvaluation(**json.loads(content_text))
                print(f"    ✓ OpenAI API call successful (chat.completions fallback)")
                return parsed

        except RateLimitError as e:
            wait_time = (2 ** attempt) * 1  # Exponential backoff: 1s, 2s, 4s
            print(f"    Rate limit hit. Waiting {wait_time}s before retry...")
            time.sleep(wait_time)

        except APIConnectionError as e:
            print(f"    Connection error: {e}")
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 1
                print(f"    Retrying in {wait_time}s...")
                time.sleep(wait_time)

        except APIError as e:
            print(f"    API error: {e}")
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 1
                print(f"    Retrying in {wait_time}s...")
                time.sleep(wait_time)

        except Exception as e:
            print(f"    Unexpected error: {e}")
            return None

    print(f"    ✗ All {max_retries} attempts failed")
    return None


def should_skip_evaluation(applicant_fields: dict, force: bool = False) -> bool:
    """
    Check if applicant already has LLM evaluation (caching).

    Args:
        applicant_fields: Airtable record fields
        force: If True, re-evaluate even if already processed

    Returns:
        True if should skip, False if should evaluate
    """
    if force:
        return False

    # Skip if all LLM fields are populated
    has_summary = bool(applicant_fields.get('LLM Summary'))
    has_score = applicant_fields.get('LLM Score') is not None
    has_followups = bool(applicant_fields.get('LLM Follow-Ups'))

    return has_summary and has_score and has_followups


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate ALL applicants using OpenAI LLM (per PRD trigger: after Compressed JSON is written)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python llm_evaluator.py              Evaluate all applicants
  python llm_evaluator.py --id rec123  Evaluate single applicant
  python llm_evaluator.py --force      Re-evaluate all (ignore cache)
        """
    )
    parser.add_argument(
        '--id',
        type=str,
        help='Specific Applicant record ID to process'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-evaluate even if LLM fields already populated'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("LLM Evaluator - Contractor Application System")
    print("=" * 70)
    print()

    # Load environment variables
    print("Loading credentials...")
    load_dotenv()

    airtable_pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    openai_api_key = os.getenv('OPENAI_API_KEY')

    if not airtable_pat or not base_id:
        print("ERROR: Missing Airtable credentials in .env file")
        sys.exit(1)

    if not openai_api_key:
        print("ERROR: Missing OPENAI_API_KEY in .env file")
        sys.exit(1)

    print(f"✓ Airtable connected to base: {base_id}")
    print(f"✓ OpenAI API key configured")
    print()

    # Connect to Airtable and OpenAI
    try:
        airtable_api = Api(airtable_pat)
        base = airtable_api.base(base_id)
        applicants_table = base.table("Applicants")

        # Create OpenAI client with explicit API key
        os.environ['OPENAI_API_KEY'] = openai_api_key  # Ensure it's in environment
        openai_client = OpenAI(api_key=openai_api_key)

    except Exception as e:
        print(f"ERROR: Failed to initialize clients: {e}")
        sys.exit(1)

    # Get applicants to evaluate (ALL applicants per PRD trigger)
    if args.id:
        print(f"Evaluating single applicant: {args.id}")
        print()
        try:
            applicant = applicants_table.get(args.id)
            applicants = [applicant]
        except Exception as e:
            print(f"ERROR: Failed to get applicant {args.id}: {e}")
            sys.exit(1)
    else:
        print("Evaluating ALL applicants (per PRD: trigger is after Compressed JSON is written)...")
        print()
        try:
            applicants = applicants_table.all()
        except Exception as e:
            print(f"ERROR: Failed to get applicants: {e}")
            sys.exit(1)

    print("=" * 70)
    print("LLM Evaluation Results")
    print("=" * 70)
    print()

    success_count = 0
    skip_count = 0
    error_count = 0

    for idx, applicant in enumerate(applicants, 1):
        applicant_id = applicant['id']
        fields = applicant['fields']

        # Get compressed JSON
        compressed_json_str = fields.get('Compressed JSON', '')
        if not compressed_json_str:
            print(f"[{idx}/{len(applicants)}] {applicant_id}: Skipped (no compressed JSON)")
            skip_count += 1
            print()
            continue

        try:
            # Parse JSON to get candidate name
            applicant_data = json.loads(compressed_json_str)
            name = applicant_data.get('personal', {}).get('name', 'Unknown')

            print(f"[{idx}/{len(applicants)}] {name} ({applicant_id}):")

            # Check if already evaluated (caching)
            if should_skip_evaluation(fields, args.force):
                print(f"  → Skipped (already evaluated, use --force to re-evaluate)")
                skip_count += 1
                print()
                continue

            # Call OpenAI API
            evaluation = call_openai_with_retry(openai_client, applicant_data)

            if evaluation is None:
                print(f"  ✗ Failed to get LLM evaluation")
                error_count += 1
                print()
                continue

            # Validate summary word count
            summary_words = len(evaluation.summary.split())
            if summary_words > 75:
                print(f"  Warning: Summary has {summary_words} words (>75), truncating...")
                words = evaluation.summary.split()[:75]
                evaluation.summary = ' '.join(words) + "..."

            # Update Applicants table
            applicants_table.update(applicant_id, {
                'LLM Summary': evaluation.summary,
                'LLM Score': evaluation.score,
                'LLM Follow-Ups': evaluation.follow_ups
            })

            print(f"  ✓ Evaluation complete")
            print(f"    - Score: {evaluation.score}/10")
            print(f"    - Summary: {len(evaluation.summary.split())} words")
            print(f"    - Issues: {evaluation.issues}")
            print(f"    - Follow-ups: {len([l for l in evaluation.follow_ups.split('\\n') if l.strip()])} questions")

            success_count += 1

        except json.JSONDecodeError as e:
            print(f"  ERROR: Invalid JSON: {e}")
            error_count += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            error_count += 1

        print()

    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total applicants: {len(applicants)}")
    print(f"✓ Successfully evaluated: {success_count}")
    print(f"→ Skipped (already evaluated): {skip_count}")
    print(f"✗ Skipped (no JSON): {len(applicants) - success_count - skip_count - error_count}")
    print(f"✗ Errors: {error_count}")
    print()

    if success_count > 0:
        print("Next steps:")
        print("  1. View LLM fields in Airtable: https://airtable.com/{base_id}")
        print("  2. Review LLM Summary, LLM Score, and LLM Follow-Ups columns")
        print("  3. Use insights for ALL candidates (shortlisted and rejected)")
    print()


if __name__ == "__main__":
    main()
