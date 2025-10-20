# Mercor Mini-Task: Airtable Contractor Application System

A comprehensive Airtable-based data model and automation system for managing contractor applications with LLM-powered evaluation.

## Overview

This project implements a multi-table form flow system that:
- Collects contractor application data through structured Airtable forms
- Compresses normalized data into JSON for efficient storage
- Decompresses JSON back to normalized tables for editing
- Auto-shortlists promising candidates based on multi-factor rules
- Uses Anthropic Claude to evaluate, enrich, and sanity-check applications

## Features

- **Multi-table Data Model**: Normalized schema with Applicants, Personal Details, Work Experience, and Salary Preferences tables
- **JSON Compression/Decompression**: Efficient data storage and retrieval via Python scripts
- **Automated Shortlisting**: Rule-based candidate evaluation (experience, compensation, location)
- **LLM Integration**: Anthropic Claude API for intelligent application review
- **Retry Logic**: Exponential backoff for API resilience
- **Security**: Environment-based API key management

## Project Structure

```
mercor-mini-task/
├── scripts/
│   ├── compress.py           # Compress child table data to JSON
│   ├── decompress.py         # Decompress JSON to child tables
│   ├── shortlist.py          # Shortlisting logic
│   ├── llm_evaluator.py      # LLM evaluation with Claude
│   └── config.py             # Configuration management
├── docs/
│   ├── AIRTABLE_SETUP.md     # Airtable configuration guide
│   └── DOCUMENTATION.md      # Complete system documentation
├── .env.example              # Environment variables template
├── .gitignore
├── requirements.txt
├── prd.md                    # Original requirements
└── README.md
```

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Airtable account with API access
- Anthropic API key

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/tkhongsap/mercor-mini-task-tkhongsap.git
cd mercor-mini-task-tkhongsap

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. Airtable Setup

Follow the detailed guide in `docs/AIRTABLE_SETUP.md` to:
- Create the required tables and fields
- Set up form views
- Configure table relationships
- Get your Airtable API credentials

### 4. Usage

**Compress data to JSON:**
```bash
python scripts/compress.py --applicant-id <APPLICANT_ID>
```

**Decompress JSON to tables:**
```bash
python scripts/decompress.py --applicant-id <APPLICANT_ID>
```

**Run full evaluation pipeline:**
```bash
python scripts/compress.py --applicant-id <APPLICANT_ID> --evaluate
```

## Configuration

Required environment variables in `.env`:

```
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_base_id
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Documentation

- **[Airtable Setup Guide](docs/AIRTABLE_SETUP.md)**: Step-by-step Airtable configuration
- **[System Documentation](docs/DOCUMENTATION.md)**: Complete technical documentation
- **[PRD](prd.md)**: Original project requirements

## Shortlisting Criteria

Candidates are automatically shortlisted when they meet ALL criteria:

| Criterion | Rule |
|-----------|------|
| Experience | ≥4 years total OR worked at tier-1 company (Google, Meta, OpenAI, etc.) |
| Compensation | Preferred rate ≤$100/hr AND availability ≥20 hrs/week |
| Location | Based in US, Canada, UK, Germany, or India |

## LLM Evaluation

The system uses Anthropic Claude to:
- Summarize applicants in ≤75 words
- Assign quality scores (1-10)
- Flag missing or contradictory data
- Suggest follow-up questions

Features:
- Retry logic with exponential backoff (3 attempts)
- Token budget controls
- Deduplication to avoid redundant API calls

## Security

- API keys stored in environment variables (never committed)
- `.env` file excluded from Git via `.gitignore`
- Template `.env.example` provided for setup

## License

This project is created for the Mercor mini-interview task.

## Author

Tkhongsap
