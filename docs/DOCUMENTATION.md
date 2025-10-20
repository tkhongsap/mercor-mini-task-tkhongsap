# Mercor Contractor Application System - Complete Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Data Model](#data-model)
4. [Script Documentation](#script-documentation)
5. [Shortlisting Criteria](#shortlisting-criteria)
6. [LLM Integration](#llm-integration)
7. [Workflow Examples](#workflow-examples)
8. [Customization Guide](#customization-guide)
9. [API Reference](#api-reference)
10. [Troubleshooting](#troubleshooting)

## System Overview

The Mercor Contractor Application System is an automated pipeline for managing contractor applications. It uses Airtable as a data store and integrates with Anthropic Claude for intelligent application review.

### Key Features

- **Multi-table normalized data model** for structured application data
- **JSON compression/decompression** for efficient storage and data portability
- **Rule-based shortlisting** with configurable criteria
- **LLM-powered evaluation** using Anthropic Claude
- **Retry logic and error handling** for API resilience
- **Deduplication** to avoid redundant LLM API calls

### Technology Stack

- **Python 3.8+**: Core programming language
- **Airtable API**: Data storage and management
- **Anthropic Claude**: LLM evaluation (claude-3-5-sonnet-20241022)
- **pyairtable**: Official Airtable Python client
- **python-dotenv**: Environment variable management
- **python-dateutil**: Date/time parsing

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                       Airtable Base                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Applicants (Parent)                                 │   │
│  │  - Applicant ID                                      │   │
│  │  - Compressed JSON                                   │   │
│  │  - Shortlist Status                                  │   │
│  │  - LLM Summary, Score, Follow-Ups                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│         ┌─────────────────┼─────────────────┐               │
│         ▼                 ▼                 ▼               │
│  ┌───────────┐   ┌─────────────┐   ┌──────────────┐       │
│  │ Personal  │   │    Work     │   │   Salary     │       │
│  │ Details   │   │ Experience  │   │ Preferences  │       │
│  └───────────┘   └─────────────┘   └──────────────┘       │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Shortlisted Leads                                   │   │
│  │  - Auto-populated when criteria met                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Python Scripts                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ compress.py│  │shortlist.py│  │llm_eval.py │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│  ┌────────────┐  ┌────────────┐                             │
│  │decompress  │  │ config.py  │                             │
│  └────────────┘  └────────────┘                             │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Anthropic Claude API                       │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

#### 1. Compression Flow

```
Child Tables → compress.py → Compressed JSON → Applicants Table
                                 │
                                 ├→ shortlist.py → Shortlisted Leads
                                 └→ llm_evaluator.py → LLM Fields
```

#### 2. Decompression Flow

```
Applicants Table → Compressed JSON → decompress.py → Child Tables
```

## Data Model

### Applicants Table (Parent)

Primary table storing one row per applicant with aggregated data.

**Schema:**

| Field | Type | Purpose |
|-------|------|---------|
| Applicant ID | Text (Primary) | Unique identifier |
| Compressed JSON | Long text | Full application data in JSON format |
| Shortlist Status | Single select | "Pending", "Shortlisted", "Not Shortlisted" |
| LLM Summary | Long text | Claude-generated summary (≤75 words) |
| LLM Score | Number | Quality score 1-10 |
| LLM Follow-Ups | Long text | Suggested questions |
| LLM Issues | Long text | Data gaps/inconsistencies |
| JSON Hash | Text | SHA256 hash for deduplication |

### Personal Details Table

One-to-one relationship with Applicants.

**Schema:**

| Field | Type | Purpose |
|-------|------|---------|
| Record ID | Autonumber | Primary key |
| Applicant ID | Link | Reference to Applicants |
| Full Name | Text | Applicant name |
| Email | Email | Contact email |
| Location | Text | Geographic location |
| LinkedIn | URL | Profile URL |

### Work Experience Table

One-to-many relationship with Applicants (multiple jobs per applicant).

**Schema:**

| Field | Type | Purpose |
|-------|------|---------|
| Record ID | Autonumber | Primary key |
| Applicant ID | Link | Reference to Applicants |
| Company | Text | Employer name |
| Title | Text | Job title |
| Start | Date | Start date |
| End | Date | End date (null if current) |
| Technologies | Long text | Skills/technologies used |

### Salary Preferences Table

One-to-one relationship with Applicants.

**Schema:**

| Field | Type | Purpose |
|-------|------|---------|
| Record ID | Autonumber | Primary key |
| Applicant ID | Link | Reference to Applicants |
| Preferred Rate | Number | Desired hourly rate |
| Minimum Rate | Number | Minimum acceptable rate |
| Currency | Single select | USD, EUR, GBP, INR, CAD |
| Availability (hrs/wk) | Number | Hours available per week |

### Shortlisted Leads Table

Auto-populated by shortlisting logic.

**Schema:**

| Field | Type | Purpose |
|-------|------|---------|
| Record ID | Autonumber | Primary key |
| Applicant | Link | Reference to Applicants |
| Compressed JSON | Long text | Copy of application JSON |
| Score Reason | Long text | Human-readable criteria explanation |
| Created At | DateTime | Timestamp of shortlisting |

## Script Documentation

### config.py

Central configuration module.

**Purpose:**
- Load environment variables from `.env`
- Define table names and constants
- Provide utility functions for data normalization
- Validate configuration on startup

**Key Constants:**

```python
TIER_1_COMPANIES = {
    'Google', 'Meta', 'OpenAI', 'Microsoft',
    'Amazon', 'Apple', 'Netflix', ...
}

SHORTLIST_CRITERIA = {
    'min_years_experience': 4,
    'max_hourly_rate_usd': 100,
    'min_weekly_hours': 20,
    'valid_locations': {'US', 'Canada', 'UK', 'Germany', 'India'},
}
```

**Functions:**

- `validate_config()`: Checks all required env vars are set
- `normalize_company_name(company)`: Standardizes company names
- `normalize_location(location)`: Standardizes location names

**Usage:**

```bash
python config.py  # Test configuration
```

### compress.py

Compresses data from child tables into JSON format.

**Purpose:**
- Fetch data from Personal Details, Work Experience, Salary Preferences
- Build structured JSON object
- Store in Applicants table
- Optionally trigger shortlisting and LLM evaluation

**Class: DataCompressor**

**Methods:**

- `compress_applicant_data(applicant_id)`: Build JSON from child tables
- `update_compressed_json(applicant_id, data)`: Write JSON to Airtable
- `process_applicant(applicant_id, run_shortlist, run_llm)`: Full pipeline
- `process_all_applicants()`: Process all applicants in base

**JSON Structure:**

```json
{
  "personal": {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "location": "New York, US",
    "linkedin": "https://linkedin.com/in/janedoe"
  },
  "experience": [
    {
      "company": "Google",
      "title": "Software Engineer",
      "start": "2018-01-15",
      "end": "2022-06-30",
      "technologies": "Python, React, PostgreSQL"
    }
  ],
  "salary": {
    "rate": 95,
    "minimum_rate": 80,
    "currency": "USD",
    "availability": 30
  }
}
```

**Usage:**

```bash
# Compress single applicant with full evaluation
python compress.py --applicant-id rec123456

# Compress without LLM evaluation
python compress.py --applicant-id rec123456 --no-llm

# Compress all applicants
python compress.py

# Compress without any evaluation
python compress.py --applicant-id rec123456 --no-shortlist --no-llm
```

### decompress.py

Decompresses JSON back to normalized tables.

**Purpose:**
- Read Compressed JSON from Applicants table
- Upsert records to child tables
- Maintain referential integrity

**Class: DataDecompressor**

**Methods:**

- `decompress_applicant_data(applicant_id, json_data)`: Upsert to all child tables
- `upsert_personal_details(applicant_id, data)`: Update/create personal record
- `upsert_work_experience(applicant_id, data)`: Delete old + create new experience records
- `upsert_salary_preferences(applicant_id, data)`: Update/create salary record
- `process_applicant(applicant_id, json_data)`: Full decompression
- `process_all_applicants()`: Decompress all applicants

**Upsert Strategy:**

- **Personal Details**: Update if exists, create if not
- **Work Experience**: Delete all existing, create new (ensures exact match)
- **Salary Preferences**: Update if exists, create if not

**Usage:**

```bash
# Decompress single applicant from Airtable
python decompress.py --applicant-id rec123456

# Decompress from JSON file
python decompress.py --applicant-id rec123456 --json-file data.json

# Decompress all applicants
python decompress.py
```

### shortlist.py

Evaluates candidates against shortlisting criteria.

**Purpose:**
- Evaluate experience (years OR tier-1 company)
- Evaluate compensation (rate AND availability)
- Evaluate location
- Create Shortlisted Leads records for qualified candidates

**Class: ShortlistEvaluator**

**Methods:**

- `calculate_years_of_experience(experience_list)`: Sum total experience
- `has_tier1_experience(experience_list)`: Check for tier-1 companies
- `evaluate_experience(json_data)`: Apply experience criteria
- `evaluate_compensation(json_data)`: Apply compensation criteria
- `evaluate_location(json_data)`: Apply location criteria
- `evaluate_applicant(applicant_id, json_data)`: Run all evaluations
- `create_shortlist_record(applicant_id, json_data, evaluation)`: Create lead
- `process_applicant(applicant_id, json_data)`: Full pipeline

**Criteria Logic:**

```
SHORTLISTED = Experience AND Compensation AND Location

Where:
  Experience = (Years >= 4) OR (Tier-1 Company)
  Compensation = (Rate <= $100/hr) AND (Availability >= 20 hrs/wk)
  Location = In {US, Canada, UK, Germany, India}
```

**Usage:**

```bash
# Evaluate single applicant
python shortlist.py rec123456
```

**Output Example:**

```
✓ Applicant rec123456 shortlisted (record: rec789012)

Shortlisting Result:
{
  "applicant_id": "rec123456",
  "shortlisted": true,
  "evaluation": {
    "should_shortlist": true,
    "experience": {
      "pass": true,
      "reason": "Worked at tier-1 company: Google"
    },
    "compensation": {
      "pass": true,
      "reason": "$95/hour with 30 hrs/week availability"
    },
    "location": {
      "pass": true,
      "reason": "Located in New York, US"
    }
  },
  "shortlist_record_id": "rec789012"
}
```

### llm_evaluator.py

Uses Anthropic Claude for intelligent application review.

**Purpose:**
- Analyze applicant JSON with Claude
- Generate summaries, scores, and insights
- Implement retry logic and deduplication
- Update Applicants table with results

**Class: LLMEvaluator**

**Methods:**

- `compute_json_hash(json_data)`: Generate SHA256 hash for deduplication
- `check_if_already_evaluated(applicant_id, json_hash)`: Avoid redundant calls
- `parse_llm_response(response_text)`: Extract structured data from Claude
- `evaluate_with_llm(json_data)`: Call Claude API with retry logic
- `update_applicant_with_llm_results(applicant_id, evaluation, json_hash)`: Write to Airtable
- `process_applicant(applicant_id, json_data, force)`: Full pipeline

**LLM Prompt Structure:**

```
You are a recruiting analyst. Given this JSON applicant profile, do four things:
1. Provide a concise 75-word summary.
2. Rate overall candidate quality from 1-10 (higher is better).
3. List any data gaps or inconsistencies you notice.
4. Suggest up to three follow-up questions to clarify gaps.

Applicant Profile JSON:
{...}

Return exactly in this format:
Summary: <text>
Score: <integer>
Issues: <comma-separated list or 'None'>
Follow-Ups: <bullet list>
```

**Retry Logic:**

- 3 attempts maximum
- Exponential backoff: 1s, 2s, 4s
- Logs all errors

**Deduplication:**

- Computes SHA256 hash of JSON
- Stores hash in Airtable
- Skips evaluation if hash unchanged (unless `--force`)

**Usage:**

```bash
# Evaluate single applicant
python llm_evaluator.py rec123456

# Force re-evaluation
python llm_evaluator.py rec123456 --force
```

**Output Example:**

```
Evaluating applicant rec123456 with Claude...
✓ Applicant rec123456 evaluated successfully
  Score: 8/10
  Summary: Full-stack engineer with 4.5 years at Google, specializing in React and Python...

LLM Evaluation Result:
{
  "applicant_id": "rec123456",
  "status": "success",
  "evaluation": {
    "summary": "Full-stack engineer with 4.5 years at Google...",
    "score": 8,
    "issues": "None",
    "follow_ups": "• Can you describe your most challenging project?\n• Have you led any teams?"
  }
}
```

## Shortlisting Criteria

### Experience Criteria

Candidate meets experience requirement if EITHER:

1. **Total years of experience >= 4 years**
   - Calculated by summing all work experience periods
   - Handles ongoing roles (no end date = present)

2. **Worked at a tier-1 company**
   - Defined in `config.TIER_1_COMPANIES`
   - Includes: Google, Meta, OpenAI, Microsoft, Amazon, Apple, Netflix, etc.

### Compensation Criteria

Candidate meets compensation requirement if BOTH:

1. **Preferred rate <= $100 USD/hour**
   - Currently only validates USD precisely
   - Non-USD currencies accepted with warning

2. **Availability >= 20 hours/week**
   - Minimum commitment threshold

### Location Criteria

Candidate meets location requirement if located in:

- United States (US, USA, United States)
- Canada
- United Kingdom (UK, United Kingdom, Great Britain)
- Germany (Deutschland)
- India

Location matching is flexible (checks if valid location appears in string).

### Customizing Criteria

Edit `scripts/config.py`:

```python
# Add more tier-1 companies
TIER_1_COMPANIES = {
    'Google',
    'Meta',
    # Add your companies here
    'YourCompany',
}

# Change thresholds
SHORTLIST_CRITERIA = {
    'min_years_experience': 5,  # Change from 4 to 5
    'max_hourly_rate_usd': 120,  # Change from 100 to 120
    'min_weekly_hours': 25,  # Change from 20 to 25
    'valid_locations': {
        'US', 'Canada', 'UK', 'Germany', 'India',
        'France',  # Add new location
    },
}
```

## LLM Integration

### Model Configuration

**Default Model:** `claude-3-5-sonnet-20241022`

**Token Budget:** 1000 tokens (configurable via `MAX_TOKENS`)

**Change Model:**

Edit `.env`:
```
CLAUDE_MODEL=claude-3-opus-20240229  # Use Opus instead
```

### Prompt Engineering

The prompt is defined in `config.LLM_PROMPT_TEMPLATE`.

**To customize:**

Edit `scripts/config.py`:

```python
LLM_PROMPT_TEMPLATE = """You are a recruiting analyst for a tech startup.
Given this applicant profile, evaluate their fit for senior engineering roles.

[Your custom instructions here]

Applicant Profile JSON:
{json_data}

Return in this format:
Summary: <text>
Score: <integer>
Issues: <list>
Follow-Ups: <bullet list>
"""
```

### Response Parsing

The system expects structured output:

```
Summary: [75-word summary]
Score: [1-10]
Issues: [comma-separated or 'None']
Follow-Ups:
• [Question 1]
• [Question 2]
• [Question 3]
```

If Claude returns unexpected format, parsing may fail. Review `llm_evaluator.py:parse_llm_response()` for parsing logic.

### Error Handling

**Retry Strategy:**
- Attempt 1: Immediate
- Attempt 2: Wait 1 second
- Attempt 3: Wait 2 seconds
- Final: Wait 4 seconds

**Errors Logged:**
- API connection errors
- Rate limiting
- Parsing failures
- Invalid responses

**Fallback:**
- All retries exhausted → Error logged to console
- Applicant record not updated
- Can be retried manually with `--force`

## Workflow Examples

### End-to-End Workflow

1. **Applicant submits forms**
   - Fills Personal Details form
   - Fills Work Experience form (multiple times if needed)
   - Fills Salary Preferences form

2. **Administrator runs compression**
   ```bash
   python scripts/compress.py --applicant-id rec123456
   ```

3. **System automatically:**
   - Compresses data to JSON
   - Evaluates shortlisting criteria
   - Calls Claude for evaluation
   - Updates all fields

4. **Review in Airtable**
   - Check Shortlist Status
   - Read LLM Summary and Score
   - Review suggested Follow-Ups

5. **Make edits (if needed)**
   - Edit Compressed JSON directly in Airtable
   - Run decompression:
   ```bash
   python scripts/decompress.py --applicant-id rec123456
   ```
   - Child tables now reflect edited JSON

### Batch Processing

Process all pending applicants:

```bash
# Compress all applicants
python scripts/compress.py

# Or without LLM to save costs
python scripts/compress.py --no-llm
```

### Re-evaluation After Criteria Change

If you change shortlisting criteria:

```bash
# Re-compress and re-evaluate all
python scripts/compress.py

# Shortlist status will be updated
```

If you want to re-run LLM without changes:

```bash
python scripts/llm_evaluator.py rec123456 --force
```

## Customization Guide

### Adding New Shortlisting Criteria

Example: Add "degree requirement"

1. **Update JSON schema** (add to compression):

```python
# In compress.py, add degree field
personal = self.extract_personal_details(applicant_id)
personal['degree'] = details.get('Degree')  # Add this
```

2. **Add evaluation logic** (in shortlist.py):

```python
def evaluate_education(self, json_data: Dict) -> Tuple[bool, str]:
    personal = json_data.get('personal', {})
    degree = personal.get('degree', '')

    valid_degrees = {'Bachelors', 'Masters', 'PhD'}

    if degree in valid_degrees:
        return True, f"Has {degree} degree"
    else:
        return False, f"Degree requirement not met"
```

3. **Update criteria** (in shortlist.py `evaluate_applicant()`):

```python
edu_pass, edu_reason = self.evaluate_education(json_data)
should_shortlist = exp_pass and comp_pass and loc_pass and edu_pass
```

### Adding New Tier-1 Company

Edit `scripts/config.py`:

```python
TIER_1_COMPANIES = {
    'Google',
    'Meta',
    # ... existing companies ...
    'Your New Company',  # Add here
}
```

### Changing LLM Evaluation Fields

To add new LLM output field (e.g., "Culture Fit"):

1. **Update Airtable** (add "LLM Culture Fit" field)

2. **Update prompt** (in config.py):

```python
LLM_PROMPT_TEMPLATE = """...
5. Rate culture fit from 1-10.

Return exactly:
Summary: <text>
Score: <integer>
Issues: <list>
Follow-Ups: <list>
Culture Fit: <integer>
"""
```

3. **Update parser** (in llm_evaluator.py):

```python
def parse_llm_response(self, response_text):
    # ... existing parsing ...

    culture_fit = None
    if line.startswith('Culture Fit:'):
        culture_fit = int(line.replace('Culture Fit:', '').strip())

    return summary, score, issues, follow_ups, culture_fit
```

4. **Update Airtable write** (in llm_evaluator.py):

```python
update_fields = {
    # ... existing fields ...
    'LLM Culture Fit': evaluation.get('culture_fit'),
}
```

## API Reference

### DataCompressor

```python
compressor = DataCompressor()

# Compress single applicant
json_data = compressor.compress_applicant_data('rec123456')

# Update Airtable
compressor.update_compressed_json('rec123456', json_data)

# Full pipeline
result = compressor.process_applicant(
    'rec123456',
    run_shortlist=True,
    run_llm=True
)
```

### DataDecompressor

```python
decompressor = DataDecompressor()

# Decompress from Airtable
result = decompressor.process_applicant('rec123456')

# Decompress from custom JSON
json_data = {...}
result = decompressor.process_applicant('rec123456', json_data)
```

### ShortlistEvaluator

```python
evaluator = ShortlistEvaluator()

# Evaluate applicant
should_shortlist, evaluation = evaluator.evaluate_applicant(
    'rec123456',
    json_data
)

# Full process (creates record if shortlisted)
result = evaluator.process_applicant('rec123456', json_data)
```

### LLMEvaluator

```python
llm_eval = LLMEvaluator()

# Evaluate with Claude
evaluation, error = llm_eval.evaluate_with_llm(json_data)

# Full process with deduplication
result = llm_eval.process_applicant(
    'rec123456',
    json_data,
    force=False  # Set True to skip deduplication
)
```

## Troubleshooting

### Configuration Issues

**Problem:** "Configuration validation failed"

**Solution:**
- Ensure `.env` file exists
- Check all required keys are present
- Verify API keys are valid

**Test:**
```bash
python scripts/config.py
```

### Airtable API Errors

**Problem:** "Could not find table"

**Solution:**
- Verify table names exactly match `config.py`
- Check table names are case-sensitive
- Ensure base ID is correct

**Problem:** "Permission denied"

**Solution:**
- Check API token has required scopes
- Verify token has access to the specific base
- Try creating a new token

### LLM API Errors

**Problem:** "All retry attempts failed"

**Solution:**
- Check Anthropic API key is valid
- Verify you have API credits
- Check rate limits
- Review error logs for specific issue

**Problem:** "Failed to parse LLM response"

**Solution:**
- Claude occasionally returns unexpected format
- Use `--force` to retry
- Check `raw_response` field for debugging
- May need to adjust prompt or parser

### Data Issues

**Problem:** "No Compressed JSON found"

**Solution:**
- Run compress.py first
- Check applicant has child table data
- Verify child tables are linked correctly

**Problem:** "Experience calculation incorrect"

**Solution:**
- Check date formats in Work Experience
- Ensure dates are valid (Start < End)
- Review `calculate_years_of_experience()` logic

### Shortlisting Issues

**Problem:** "Expected shortlist but wasn't"

**Solution:**
- Check each criterion individually
- Review score reason in output
- Verify criterion thresholds in config.py
- Normalize company/location names

**Debug:**
```bash
# Run with single applicant to see detailed output
python scripts/shortlist.py rec123456
```

### Performance Issues

**Problem:** "Processing is slow"

**Solution:**
- LLM calls are rate-limited by Anthropic
- Use `--no-llm` for faster compression
- Process in smaller batches
- Consider using faster Claude model (Haiku)

## Best Practices

1. **Environment Management**
   - Never commit `.env` file
   - Use `.env.example` as template
   - Rotate API keys regularly

2. **Data Integrity**
   - Always compress before running shortlist/LLM
   - Test with sample data first
   - Back up Airtable base before batch operations

3. **Cost Management**
   - LLM calls cost money (tokens)
   - Use deduplication (don't use `--force` unless needed)
   - Consider processing in batches
   - Set MAX_TOKENS appropriately

4. **Error Handling**
   - Review logs for failed operations
   - Retry failed applicants individually
   - Monitor API rate limits

5. **Customization**
   - Test config changes with single applicant first
   - Document custom criteria
   - Version control all changes

## Support and Resources

- **Airtable API Docs:** https://airtable.com/api
- **Anthropic API Docs:** https://docs.anthropic.com/
- **pyairtable Docs:** https://pyairtable.readthedocs.io/

For issues or questions about this system, refer to the project README and AIRTABLE_SETUP.md.
