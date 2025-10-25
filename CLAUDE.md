# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated Airtable-based contractor application system with Python automation for data processing, candidate evaluation, and LLM-powered enrichment. The system uses a multi-table Airtable base with Python scripts to compress/decompress data, auto-shortlist candidates based on criteria, and enrich applications using LLM evaluation.

**Live Airtable Base:** https://airtable.com/app5go7iUaSsc0uKs

**Status:** Complete implementation with 10 test applicants, 6 shortlisted, all LLM-evaluated.

## Essential Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure credentials (first time only)
cp env.template .env
# Then edit .env to add:
# - AIRTABLE_PERSONAL_ACCESS_TOKEN (from Account → Developer → Personal access tokens)
# - AIRTABLE_BASE_ID (from Airtable API docs, starts with "app")
# - OPENAI_API_KEY (from platform.openai.com/api-keys)
```

### Full Automation Pipeline
```bash
# Run scripts in numbered order (01-05)
python 01_setup_airtable_schema.py      # Creates all 5 tables via API
python 02_generate_test_data.py         # Generates 10 diverse test applicants
python 03_compress_data.py              # Compresses multi-table data → JSON
python 04_shortlist_evaluator.py        # Evaluates against 3 criteria, creates shortlist
python 05_llm_evaluator.py              # LLM evaluation for ALL applicants

# Optional: Bulk editing workflow
python decompress_data.py --dry-run     # Preview JSON → tables sync
python decompress_data.py               # Apply changes
```

### Testing
```bash
# Run all 53 unit tests
python tests/test_runner.py

# PRD compliance verification
python tests/verify_prd_schema.py

# Run specific test class
python -m unittest tests.test_schema_setup.TestApplicantsTable
```

## Architecture

### Data Model
5 linked Airtable tables with parent-child relationships:

```
Applicants (Parent)
├─► Personal Details (1:1)      → Full Name, Email, Location, LinkedIn
├─► Work Experience (1:N)       → Company, Title, Start/End, Technologies
├─► Salary Preferences (1:1)    → Rates, Currency, Availability (hrs/wk)
└─► Shortlisted Leads (1:N)     → Auto-populated when ALL criteria met
```

**Key Design:** All child tables link to Applicants via `Applicant ID` field. Airtable auto-creates bidirectional links.

### Applicant ID: Python-Managed Sequence

**Critical Design Decision:** Uses `number` field type instead of `autoNumber` because:
- Airtable API doesn't support creating autoNumber fields programmatically
- Python scripts query max existing ID and increment (see `02_generate_test_data.py:357-367`)
- Enables full API automation without manual intervention

**Implementation Pattern:**
```python
# Query max existing ID
existing_applicants = applicants_table.all()
max_id = max([r['fields'].get('Applicant ID', 0) for r in existing_applicants], default=0)
next_id = max_id + 1

# Create with managed ID
applicants_table.create({"Applicant ID": next_id})
```

### Shortlist Criteria (ALL Must Pass)

Evaluated in `04_shortlist_evaluator.py:183-246`:

1. **Experience** (lines 199-211):
   - ≥4 years total experience OR
   - Worked at tier-1 company (Google, Meta, OpenAI, Microsoft, Amazon, Apple, Netflix, Tesla, SpaceX, Uber, Airbnb, Stripe)

2. **Compensation** (lines 213-227):
   - Preferred Rate ≤$100 USD/hour AND
   - Availability ≥20 hrs/week

3. **Location** (lines 229-237):
   - Must be in: US, Canada, UK, Germany, or India
   - Enhanced matching: country codes, major cities, word boundaries
   - Blacklist prevents false positives (Australia, Austria, Indonesia, Indiana)

**Location Matching Logic** (`04_shortlist_evaluator.py:137-181`):
```python
# Supports: "San Francisco, CA, USA", "NYC", "Toronto", "Berlin", "Bangalore"
# Prevents: "us" in "Australia", "india" in "Indiana"
APPROVED_LOCATIONS = {
    'united states', 'usa', 'us ', 'nyc', 'san francisco', 'sf',
    'canada', 'toronto', 'vancouver',
    'uk ', 'london', 'manchester',
    'germany', 'berlin', 'munich',
    'india', 'bangalore', 'mumbai'
}
APPROVED_COUNTRY_CODES = {'us', 'usa', 'ca', 'uk', 'gb', 'de', 'in'}
blacklist = ['australia', 'austria', 'indonesia', 'indiana']
```

### Date Parsing for Experience Calculation

Handles real-world data variations (`04_shortlist_evaluator.py:61-117`):
```python
# Recognizes current employment
if end_str.lower() in ['present', 'current', 'ongoing', 'now']:
    end = datetime.now()

# Validates dates
if start > datetime.now():  # Future start = skip
if end < start:             # End before start = skip
if days > 365.25 * 50:      # Cap at 50 years (sanity check)
```

### LLM Integration Architecture

**Trigger:** Processes ALL applicants after Compressed JSON is written (per PRD Section 6.2).

**Implementation** (`05_llm_evaluator.py`):
- Uses Pydantic models for structured output validation (lines 32-46)
- Retry logic with exponential backoff (lines 128-189)
- Caching prevents duplicate calls (lines 198-217)
- Budget controls: max 600 tokens per call

**Structured Output:**
```python
class LLMEvaluation(BaseModel):
    summary: str        # 75 words max
    score: int          # 1-10 (ge=1, le=10)
    issues: str         # Comma-separated or "None"
    follow_ups: str     # Bullet list of 1-3 questions
```

**Error Handling:**
```python
# Retry on transient errors
for attempt in range(max_retries):
    try:
        response = client.chat.completions.create(...)
    except RateLimitError:
        wait_time = (2 ** attempt) * 1  # 1s, 2s, 4s
        time.sleep(wait_time)
    except APIConnectionError:
        # Retry with backoff
    except Exception:
        # Log and continue (don't fail entire batch)
```

## Critical Implementation Details

### Airtable API Field Types
When creating/modifying tables via `01_setup_airtable_schema.py`:

```python
# Email with validation
{"name": "Email", "type": "email"}

# URL with validation
{"name": "LinkedIn", "type": "url"}

# Date with US format
{"name": "Start", "type": "date",
 "options": {"dateFormat": {"name": "us", "format": "M/D/YYYY"}}}

# Number with decimal precision
{"name": "Preferred Rate", "type": "number", "options": {"precision": 2}}

# Single-select dropdown
{"name": "Currency", "type": "singleSelect",
 "options": {"choices": [{"name": "USD"}, {"name": "EUR"}, ...]}}

# Linked records (auto-creates reverse link)
{"name": "Applicant ID", "type": "multipleRecordLinks",
 "options": {"linkedTableId": "tblXXXXXXXXXXXXXX"}}
```

### Testing Architecture

Uses `unittest` framework (not pytest), 53 tests across 9 test classes:
- `TestAirtableSchemaSetup` - Connection and table count
- `TestApplicantsTable` - 6 core fields + 4 linked fields
- `TestPersonalDetailsTable` - Email/URL validation
- `TestWorkExperienceTable` - Date format validation
- `TestSalaryPreferencesTable` - Number precision, currency options
- `TestShortlistedLeadsTable` - DateTime with UTC timezone
- `TestPRDCompliance` - 100% specification adherence

**Test runner** (`tests/test_runner.py`):
- Auto-discovers all test classes
- Summary reporting with counts
- Exit codes: 0 (success), 1 (failure) for CI/CD

**Run single test:**
```bash
python -m unittest tests.test_schema_setup.TestApplicantsTable.test_applicant_id_field_type
```

### Environment Variables Pattern

**Always use python-dotenv:**
```python
from dotenv import load_dotenv
import os

load_dotenv()
pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
base_id = os.getenv('AIRTABLE_BASE_ID')
openai_key = os.getenv('OPENAI_API_KEY')

if not pat or not base_id:
    print("ERROR: Missing credentials in .env file")
    sys.exit(1)
```

`.env` is gitignored. Use `env.template` as reference (no real credentials).

## Script Execution Order & Purpose

**Sequential pipeline** (numbered 01-05):

1. **01_setup_airtable_schema.py** - Creates all 5 tables via Airtable API
   - Idempotent (safe to run multiple times)
   - Checks if Applicants exists before creating
   - Auto-creates linked relationships

2. **02_generate_test_data.py** - Generates 10 diverse test applicants
   - 6 that qualify for shortlist (various reasons)
   - 4 that don't qualify (edge cases)
   - Manages Applicant ID sequence

3. **03_compress_data.py** - Multi-table → JSON compression
   - Reads Personal Details, Work Experience, Salary Preferences
   - Builds JSON per PRD spec
   - Writes to Applicants.Compressed JSON field
   - Supports `--id` flag for single applicant

4. **04_shortlist_evaluator.py** - Evaluates and shortlists
   - Checks ALL 3 criteria (experience, compensation, location)
   - Sets Shortlist Status checkbox
   - Creates Shortlisted Leads record with reasoning
   - Supports `--id` flag for single applicant

5. **05_llm_evaluator.py** - LLM enrichment
   - Evaluates ALL applicants (not just shortlisted)
   - Generates 75-word summary, 1-10 score, follow-up questions
   - Uses caching (skip if already evaluated)
   - Supports `--force` to re-evaluate

**Optional:**
- **decompress_data.py** - JSON → tables (bulk editing workflow)
  - Upserts Personal Details, Salary Preferences (1:1)
  - Delete + recreate Work Experience (1:N ensures exact match)
  - Supports `--dry-run` for preview

- **cleanup_test_data.py** - Deletes all test data (keeps schema)

## Common Workflows

### Adding/Modifying Shortlist Criteria

**Location example** (`04_shortlist_evaluator.py:34-59`):
```python
# Add new approved location
APPROVED_LOCATIONS = {
    # ... existing ...
    'singapore', 'sg',  # Add Singapore
}

APPROVED_COUNTRY_CODES = {'us', 'ca', 'uk', 'de', 'in', 'sg'}  # Add 'sg'

# Update blacklist if needed
blacklist = ['australia', 'austria', 'indonesia', 'indiana']
```

**Compensation threshold** (`04_shortlist_evaluator.py:218`):
```python
# Change from $100/hr to $120/hr
if preferred_rate <= 120 and availability >= 20:
```

**Tier-1 companies** (`04_shortlist_evaluator.py:28-32`):
```python
TIER1_COMPANIES = [
    'google', 'meta', 'openai', 'microsoft', 'amazon',
    'databricks', 'anthropic'  # Add new companies
]
```

### Debugging Test Failures

1. **Check credentials:**
   ```bash
   cat .env  # Verify all 3 credentials present
   ```

2. **Verify schema manually:**
   ```bash
   python tests/verify_prd_schema.py  # Field-by-field validation
   ```

3. **Check table count:**
   - If tests fail on "Expected 5 tables, found 6" → Delete extra table via Airtable UI
   - Common cause: "Table-01" leftover from testing

4. **Field type mismatch:**
   - Tests expect `number` for Applicant ID (not `autoNumber`)
   - See `tests/test_schema_setup.py:111-118` for expected types

### Adding New Automation Scripts

**Pattern to follow:**
```python
#!/usr/bin/env python3
"""
Script Purpose - Brief description

Usage:
    python script_name.py              # Process all
    python script_name.py --id recXXX  # Process one
"""

import os
import sys
import argparse
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pyairtable import Api

def main() -> None:
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument('--id', type=str, help='Specific record ID')
    args = parser.parse_args()

    # Load env
    load_dotenv()
    pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID')

    # Connect
    api = Api(pat)
    base = api.base(base_id)

    # Process
    # ...

if __name__ == "__main__":
    main()
```

**Best practices:**
- Support both batch and single-record processing
- Use type hints for all functions
- Handle errors gracefully (don't fail entire batch)
- Print progress for long operations
- Exit with proper codes (0 = success, 1 = error)

## Important Constraints

### PRD Compliance
- **No emojis** in field names, table names, or documentation
- Field names must match PRD exactly (case-sensitive, spaces matter)
- All 5 tables required for 100% compliance

### Airtable API Limitations
- **Cannot create autoNumber via API** → Use Python-managed number sequence
- Cannot rename primary field via API
- Cannot delete tables via API (must use Airtable UI)
- Linked record fields auto-create reverse links (intentional)

### Security Requirements
- Never hardcode credentials
- All secrets in `.env` (gitignored)
- Use `env.template` for examples only
- Minimal PAT scopes: `schema.bases:read`, `schema.bases:write`, `data.records:read`, `data.records:write`

## Type Safety & Code Quality

### Type Hints
All scripts use comprehensive type hints:
```python
from typing import Optional, Dict, List, Tuple, Any

def compress_applicant_data(
    api: Api,
    base_id: str,
    applicant_record: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Compress data from child tables into JSON."""
    # ...
```

### Logging (Optional)
`logger.py` provides color-coded logging:
```python
from logger import get_logger

logger = get_logger(__name__)
logger.info("Processing applicant...")
logger.warning("Missing field: %s", field_name)
logger.error("API call failed: %s", error)
```

## Documentation Files

- **SUBMISSION.md** - Complete deliverables documentation (13,000+ words)
  - Setup instructions
  - Field definitions for all 5 tables
  - Automation scripts explained with code snippets
  - LLM integration & security
  - Customization guide

- **DESIGN_DECISIONS.md** - Architectural rationale
  - Why Python-managed ID vs autoNumber
  - Why test data generation instead of forms
  - Enhanced validation logic (location, dates)

- **README.md** - Quick start guide

- **prd.md** - Original project requirements

## Reference Links

- Airtable API Docs: https://airtable.com/developers/web/api/introduction
- pyairtable Docs: https://pyairtable.readthedocs.io/
- OpenAI API Docs: https://platform.openai.com/docs/api-reference
- Live Airtable Base: https://airtable.com/app5go7iUaSsc0uKs
