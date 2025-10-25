# Mercor Mini-Interview Task: Airtable Contractor Application System

Automated Airtable-based contractor application system with Python automation for data processing, candidate evaluation, and LLM-powered enrichment.

## Overview

This project implements a complete data model and automation system that:
1. Collects contractor application data through multi-table Airtable forms
2. Compresses data from multiple tables into JSON format
3. Auto-shortlists candidates based on multi-factor rules
4. Uses LLM to evaluate and enrich applications

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

### 2. Create Airtable Schema

```bash
# Run the setup script to create all tables (fully automated)
python setup_airtable_schema.py
```

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
├── README.md                      # This file
├── prd.md                         # Project requirements
├── setup_airtable_schema.py       # Main setup script
├── requirements.txt               # Python dependencies
├── env.template                   # Environment variable template
│
├── docs/                          # Documentation
│   ├── DELIVERABLES.md           # Requirements checklist
│   ├── PROJECT_SUMMARY.md        # Implementation guide
│   ├── RUN_TESTS.md              # Testing guide
│   └── TESTING_SUMMARY.md        # Test reports
│
└── tests/                         # Test suite
    ├── test_runner.py            # Main test runner (53 tests)
    ├── test_schema_setup.py      # Unit tests
    ├── verify_prd_schema.py      # PRD compliance verification
    └── helpers/                  # Test utilities
```

## Airtable Schema

The system uses 5 linked tables:

### Applicants (Parent Table)
- Applicant ID (auto number)
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

- **[prd.md](prd.md)** - Original project requirements
- **[docs/DELIVERABLES.md](docs/DELIVERABLES.md)** - Complete requirements checklist
- **[docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - Implementation roadmap
- **[docs/RUN_TESTS.md](docs/RUN_TESTS.md)** - Detailed testing guide
- **[docs/TESTING_SUMMARY.md](docs/TESTING_SUMMARY.md)** - Test reports

## Implementation Status

### ✅ Completed
- Fully automated schema setup (all 5 tables via one script)
- Idempotent setup script (safe to re-run)
- All fields with correct types and relationships
- Automated Applicants table creation with 6 core fields
- Comprehensive unit tests (53 tests, all passing)
- PRD compliance verification

### 🚧 Next Steps
1. Create Airtable forms for data collection
2. Build Python compression/decompression scripts
3. Build shortlist evaluator
4. Build LLM evaluator integration

## Requirements

- Python 3.8+
- Airtable account with Personal Access Token
- OpenAI API key (for LLM evaluation)

## Dependencies

```
pyairtable>=2.3.0       # Airtable API client
python-dotenv>=1.0.0    # Environment variable management
pytest>=7.4.0           # Testing framework
```

## Key Features

- **Automated Schema Setup** - Create all tables via Python script
- **Type-Safe Fields** - Proper field types (email, URL, date, number with precision)
- **Bidirectional Links** - Automatic relationship management
- **Currency Support** - USD, EUR, GBP, CAD, INR
- **Comprehensive Testing** - 53 unit tests with PRD validation
- **CI/CD Ready** - Exit codes for automation pipelines

## View Airtable Base

https://airtable.com/app5go7iUaSsc0uKs

## License

This is a mini-interview task project for Mercor.
