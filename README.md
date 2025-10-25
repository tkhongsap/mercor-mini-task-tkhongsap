# Mercor Mini-Interview Task: Airtable Contractor Application System

Automated Airtable-based contractor application system with Python automation for data processing, candidate evaluation, and LLM-powered enrichment.

**For complete submission documentation, see [SUBMISSION.md](SUBMISSION.md)**

## Overview

This project implements a complete data model and automation system that:
1. Creates 5-table Airtable schema via API
2. Compresses data from multiple tables into JSON format
3. Auto-shortlists candidates based on multi-factor rules
4. Uses LLM (OpenAI) to evaluate and enrich applications

**Airtable Base:** https://airtable.com/app5go7iUaSsc0uKs

## Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp env.template .env
# Edit .env and add your:
# - AIRTABLE_PERSONAL_ACCESS_TOKEN
# - AIRTABLE_BASE_ID
# - OPENAI_API_KEY
```

### 2. Run Full Automation Pipeline

```bash
# Sequential execution (scripts are numbered in order)
python 01_setup_airtable_schema.py      # Creates all 5 tables
python 02_generate_test_data.py         # Generates 10 test applicants
python 03_compress_data.py              # Compresses to JSON
python 04_shortlist_evaluator.py        # Evaluates & shortlists
python 05_llm_evaluator.py              # LLM analysis (ALL applicants per PRD)
```

**Note:** Per PRD Section 6.2, the LLM evaluator processes ALL applicants (not just shortlisted ones), as the trigger is "after Compressed JSON is written".

This creates all 5 tables in your Airtable base:
- **Applicants** (parent table with 6 core fields)
- **Personal Details** (one-to-one with Applicants)
- **Work Experience** (one-to-many with Applicants)
- **Salary Preferences** (one-to-one with Applicants)
- **Shortlisted Leads** (auto-populated table)

The script is idempotent - it checks if tables exist and only creates missing ones.

### 3. Verify Setup

```bash
# Run unit tests to verify schema
python tests/test_runner.py
```

Expected output: `✓ ALL TESTS PASSED - Schema is 100% PRD compliant!`

## Project Structure

```
.
├── README.md                          # Quick start guide
├── SUBMISSION.md                      # Complete deliverables documentation
├── DESIGN_DECISIONS.md                # Architectural choices explained
├── prd.md                             # Project requirements
│
├── 01_setup_airtable_schema.py        # Step 1: Schema creation
├── 02_generate_test_data.py           # Step 2: Test data generation
├── 03_compress_data.py                # Step 3: JSON compression
├── 04_shortlist_evaluator.py          # Step 4: Candidate evaluation
├── 05_llm_evaluator.py                # Step 5: LLM enrichment
│
├── decompress_data.py                 # Optional: JSON decompression
├── cleanup_test_data.py               # Utility: Clean test data
├── logger.py                          # Logging utility module
│
├── requirements.txt                   # Python dependencies
├── env.template                       # Environment variable template
│
└── tests/                             # Test suite (53 tests, 838 LOC)
    ├── test_schema_setup.py          # 53 unit tests validating schema
    ├── test_runner.py                # Test runner with summary reporting
    └── verify_prd_schema.py          # PRD compliance verification script
```

## Airtable Schema

The system uses 5 linked tables:

### Applicants (Parent Table)
- Applicant ID (Python-managed number sequence)
- Compressed JSON
- Shortlist Status (checkbox)
- LLM Summary, LLM Score, LLM Follow-Ups

### Personal Details
- Full Name, Email, Location, LinkedIn
- Link to Applicants (one-to-one)

### Work Experience
- Company, Title, Start, End, Technologies
- Link to Applicants (one-to-many)

### Salary Preferences
- Preferred Rate, Minimum Rate, Currency, Availability
- Link to Applicants (one-to-one)

### Shortlisted Leads
- Applicant link, Compressed JSON, Score Reason, Created At
- Auto-populated when candidates meet criteria

## Testing

### Run All Tests
```bash
python tests/test_runner.py
```

### Run PRD Verification
```bash
python tests/verify_prd_schema.py
```

### Test Coverage
- 53 unit tests covering all 5 tables
- Field type validation
- Linked relationship verification
- PRD compliance checking

## Documentation

- **[SUBMISSION.md](SUBMISSION.md)** - Complete submission documentation (setup, automations, LLM integration, customization)
- **[DESIGN_DECISIONS.md](DESIGN_DECISIONS.md)** - Architectural choices explained
- **[prd.md](prd.md)** - Original project requirements

## Implementation Status

### ✅ All 5 PRD Goals Completed
1. **Airtable Schema Setup** - Fully automated via `01_setup_airtable_schema.py`
2. **JSON Compression** - Multi-table → JSON via `03_compress_data.py`
3. **JSON Decompression** - JSON → tables via `decompress_data.py`
4. **Auto-Shortlist** - 3-criteria evaluation via `04_shortlist_evaluator.py`
5. **LLM Evaluation** - OpenAI integration via `05_llm_evaluator.py`

### Additional Features
- Python-managed Applicant ID (100% automation)
- Comprehensive unit tests (53 tests, all passing)
- PRD compliance verification
- Test data generation (`02_generate_test_data.py`)
- Utility scripts (cleanup, decompression)

## Requirements

- Python 3.8+
- Airtable account with Personal Access Token
- OpenAI API key (for LLM evaluation)

## Dependencies

```
pyairtable>=2.3.0       # Airtable API client
openai>=1.54.0          # OpenAI API for LLM evaluation
python-dotenv>=1.0.0    # Environment variable management
python-dateutil>=2.9.0  # Robust date parsing
pydantic>=2.12.0        # Data validation for LLM responses
pytest>=7.4.0           # Testing framework
mypy>=1.8.0             # Type checking
```

## Key Features

- **Automated Schema Setup** - Create all tables via Python script
- **Type-Safe Fields** - Proper field types (email, URL, date, number with precision)
- **Full Type Hints** - Comprehensive type annotations throughout codebase
- **Robust Parsing** - Enhanced location and date validation with edge case handling
- **Bidirectional Links** - Automatic relationship management
- **Currency Support** - USD, EUR, GBP, CAD, INR
- **Comprehensive Testing** - 53 unit tests with PRD validation
- **Logging Infrastructure** - Color-coded logging utility module
- **CI/CD Ready** - Exit codes for automation pipelines

---

**Complete submission documentation:** See [SUBMISSION.md](SUBMISSION.md) for detailed setup instructions, automation explanations, LLM integration details, and customization guide.

**View Airtable Base:** https://airtable.com/app5go7iUaSsc0uKs
