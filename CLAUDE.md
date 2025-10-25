# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated Airtable-based contractor application system with Python automation for data processing, candidate evaluation, and LLM-powered enrichment. The system uses a multi-table Airtable base with Python scripts to compress/decompress data, auto-shortlist candidates based on criteria, and enrich applications using LLM evaluation.

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

### Schema Setup
```bash
# Create all 5 Airtable tables via API (fully automated, idempotent)
python 01_setup_airtable_schema.py

# This creates:
# - Applicants table (if it doesn't exist)
# - Personal Details, Work Experience, Salary Preferences, Shortlisted Leads

# Verify schema is correct
python tests/verify_prd_schema.py
```

### Testing
```bash
# Run full test suite (53 unit tests)
python tests/test_runner.py

# Run tests in verbose mode
python tests/test_runner.py --verbose

# Run specific test file
python -m unittest tests.test_schema_setup

# Run PRD compliance verification
python tests/verify_prd_schema.py
```

### Development
```bash
# Run individual test classes
python -m unittest tests.test_schema_setup.TestApplicantsTable

# Test authentication
python tests/test_auth.py
```

## Architecture

### Data Model
The system uses 5 linked Airtable tables with a parent-child relationship structure:

```
Applicants (Parent Table)
├─► Personal Details (1:1) - Full Name, Email, Location, LinkedIn
├─► Work Experience (1:N) - Company, Title, Start/End dates, Technologies
├─► Salary Preferences (1:1) - Rates, Currency, Availability
└─► Shortlisted Leads (1:N) - Auto-populated when criteria met
```

**Critical relationships:**
- All child tables link to Applicants via `Applicant ID` field
- Applicants table auto-creates reverse-link fields when child tables are created
- Bidirectional linking is automatic via Airtable API

### Key Tables

**Applicants** (6 core fields + 4 auto-generated links):
- `Applicant ID` (autoNumber, primary key)
- `Compressed JSON` (multilineText) - Stores unified applicant data
- `Shortlist Status` (checkbox) - Set by shortlist evaluator
- `LLM Summary`, `LLM Score`, `LLM Follow-Ups` - AI-generated fields

**Personal Details** (1:1 with Applicants):
- Stores basic contact info and location
- Location field critical for shortlist evaluation

**Work Experience** (1:N with Applicants):
- One applicant can have multiple work history records
- Company field checked against tier-1 list for shortlisting
- Start/End dates used to calculate total years of experience

**Salary Preferences** (1:1 with Applicants):
- Rates must be numbers with 2 decimal precision
- Currency is single-select: USD, EUR, GBP, CAD, INR
- Availability is integer (hours per week)

**Shortlisted Leads** (auto-populated):
- Created automatically by shortlist evaluator when candidate meets ALL criteria
- Contains copy of Compressed JSON and reasoning

### Shortlist Criteria (All Must Pass)

1. **Experience**: ≥4 years total OR worked at tier-1 company (Google, Meta, OpenAI, etc.)
2. **Compensation**: Preferred Rate ≤$100 USD/hour AND Availability ≥20 hrs/week
3. **Location**: In US, Canada, UK, Germany, or India
   - Enhanced with country code support (US, CA, UK/GB, DE, IN)
   - Major city matching (NYC, SF, Toronto, London, Berlin, Bangalore, etc.)
   - Blacklist for false positives (Australia, Austria, Indonesia, Indiana)
   - Improved word boundary detection to prevent substring matches

### Planned Python Scripts (Not Yet Implemented)

**03_compress_data.py**: Gathers data from 3 child tables → builds JSON → writes to Applicants.Compressed JSON

**de03_compress_data.py**: Reads JSON → upserts back to child tables (for bulk editing)

**04_shortlist_evaluator.py**: Evaluates candidates against criteria → creates Shortlisted Leads records

**05_llm_evaluator.py**: Sends JSON to LLM → generates 75-word summary, 1-10 score, follow-up questions

## Critical Implementation Details

### Airtable API Field Types
When creating tables via `01_setup_airtable_schema.py`:
- Email fields: `{"type": "email"}`
- URL fields: `{"type": "url"}`
- Date fields: `{"type": "date", "options": {"dateFormat": {"name": "us", "format": "M/D/YYYY"}}}`
- DateTime fields: `{"type": "dateTime", "options": {"timeZone": "utc"}}`
- Number with precision: `{"type": "number", "options": {"precision": 2}}`
- Single select: `{"type": "singleSelect", "options": {"choices": [{"name": "USD"}, ...]}}`
- Links: `{"type": "multipleRecordLinks", "options": {"linkedTableId": "tblXXX"}}`

### Testing Architecture
Tests use `unittest` framework with class-based test organization:
- Each table has its own test class
- Tests validate field existence, types, and options
- PRD compliance tests ensure 100% specification adherence
- Tests require .env with valid credentials to connect to real Airtable base

Test runner (`tests/test_runner.py`) provides:
- Automatic test discovery
- Summary reporting
- CI/CD-friendly exit codes (0 = success, 1 = failure)

### Environment Variables
Always use `python-dotenv` to load credentials from `.env`:
```python
from dotenv import load_dotenv
load_dotenv()
pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
```

Never hardcode credentials. The `.env` file is gitignored.

## Project Structure

```
.
├── 01_setup_airtable_schema.py    # Main schema creation script
├── requirements.txt             # pyairtable, openai, python-dotenv, pytest
├── env.template                 # Template for credentials
│
├── docs/                        # Comprehensive documentation
│   ├── DELIVERABLES.md         # PRD requirements checklist
│   ├── PROJECT_SUMMARY.md      # Implementation roadmap & architecture
│   ├── RUN_TESTS.md            # Testing guide
│   └── TESTING_SUMMARY.md      # Test reports
│
├── tests/                       # 53 unit tests
│   ├── test_runner.py          # Main test runner
│   ├── test_schema_setup.py    # Schema validation tests
│   ├── verify_prd_schema.py    # PRD compliance checker
│   ├── conftest.py             # Pytest configuration
│   └── helpers/                # Test utilities
│
└── archive_bin/                 # Previous implementation (reference only)
```

## Common Workflows

### When Adding New Airtable Fields
1. Update field definitions in `01_setup_airtable_schema.py`
2. Run schema setup script (or manually update via Airtable UI)
3. Add corresponding test cases to `tests/test_schema_setup.py`
4. Run test suite to verify changes
5. Update documentation in `docs/PROJECT_SUMMARY.md` if needed

### When Building Automation Scripts
1. Create helper module `airtable_client.py` first (reusable API wrapper)
2. Create `config.py` for centralized configuration management
3. Build scripts in order: compression → decompression → shortlist → LLM
4. Each script should handle errors gracefully and provide clear output
5. Use LLM retry logic: 3 attempts with exponential backoff

### When Debugging Test Failures
1. Check `.env` file has valid credentials
2. Verify Airtable base has all 5 tables created
3. Run `python tests/verify_prd_schema.py` for detailed field-by-field validation
4. Check field names match EXACTLY (case-sensitive, including spaces)
5. Use `--verbose` flag for detailed test output

## Important Notes

### PRD Compliance Requirements
- No emojis in field names, table names, or documentation
- Field names must match PRD exactly (including capitalization)
- All 5 tables required: Applicants, Personal Details, Work Experience, Salary Preferences, Shortlisted Leads
- Linked relationships must be bidirectional

### Airtable API Limitations
- Cannot create primary field via API (must be auto-generated "Name" field)
- Cannot rename primary field via API
- Linked record fields auto-create reverse links in target table
- Schema fetching requires `data.records:read` scope
- Table creation requires appropriate permissions

### Security
- All API credentials in `.env` (gitignored)
- Use `env.template` as example (no real credentials)
- LLM API keys stored in environment variables, never hardcoded
- Personal Access Tokens should have minimal required scopes

### Future Extensions
When implementing planned scripts:
- Make them modular (single responsibility)
- Support both single applicant and batch processing
- Include comprehensive error handling
- Log operations for debugging
- Use configuration-driven behavior (easy to modify criteria)

## Code Quality & Type Safety

### Type Hints
All Python scripts now have comprehensive type hints:
- Function signatures include parameter and return types
- Using `typing` module: `Optional`, `Dict`, `List`, `Tuple`, `Any`
- Type checking available via `mypy *.py`

### Logging Infrastructure
- `logger.py` provides centralized logging configuration
- Color-coded console output with timestamps
- Supports DEBUG, INFO, WARNING, ERROR levels
- Example usage:
  ```python
  from logger import get_logger
  logger = get_logger(__name__)
  logger.info("Processing applicant...")
  ```

### Enhanced Robustness
**Location Matching** (`04_shortlist_evaluator.py:110-154`):
- Country code detection (US, CA, UK, DE, IN)
- Major city support (50+ cities across 5 countries)
- Blacklist to prevent false matches (Australia, Austria, Indonesia, Indiana)
- Improved word boundary detection

**Date Parsing** (`04_shortlist_evaluator.py:61-117`):
- Handles "present", "current", "ongoing", "now" for end dates
- Validates impossible dates (future starts, end before start)
- Caps unrealistic tenures at 50 years
- Better error messages for debugging

## Reference Documentation

- Airtable API: https://airtable.com/developers/web/api/introduction
- pyairtable: https://pyairtable.readthedocs.io/
- Project PRD: `prd.md`
- Detailed requirements: `docs/DELIVERABLES.md`
- Implementation guide: `docs/PROJECT_SUMMARY.md`
- Live Airtable base: https://airtable.com/app5go7iUaSsc0uKs
