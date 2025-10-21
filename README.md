# Airtable Contractor Application System

A comprehensive Python automation system that manages contractor applications using Airtable as the data backend. The system compresses multi-table data into JSON, evaluates candidates based on predefined criteria, and uses OpenAI's LLM to provide intelligent candidate assessments.

## Features

- **Multi-table Data Compression**: Gather data from linked Airtable tables into a single JSON object
- **Data Decompression**: Restore JSON data back to normalized Airtable tables
- **Automated Shortlisting**: Rule-based candidate evaluation against experience, compensation, and location criteria
- **LLM Integration**: OpenAI-powered candidate assessment with summaries, scoring, and follow-up questions
- **Robust Error Handling**: Exponential backoff retry logic and comprehensive error management
- **Flexible CLI**: Unified command-line interface with support for batch operations

## Prerequisites

- Python 3.8 or higher
- Airtable account with a configured base
- Airtable Personal Access Token (PAT)
- OpenAI API key

## Project Structure

```
mercor-mini-task/
├── src/
│   ├── __init__.py
│   ├── config.py                # Configuration and environment management
│   ├── airtable_client.py       # Airtable API wrapper
│   ├── json_compressor.py       # Data compression logic
│   ├── json_decompressor.py     # Data decompression logic
│   ├── shortlist_evaluator.py   # Rule-based candidate evaluation
│   └── llm_evaluator.py         # OpenAI LLM integration
├── scripts/
│   ├── compress_data.py         # Standalone compression script
│   ├── decompress_data.py       # Standalone decompression script
│   └── evaluate_candidates.py   # Standalone evaluation script
├── cli.py                       # Unified CLI interface
├── requirements.txt             # Python dependencies
├── AIRTABLE_SETUP.md           # Airtable setup guide
└── README.md                    # This file
```

## Setup Instructions

### 1. Set Up Airtable Base

Follow the comprehensive guide in `AIRTABLE_SETUP.md` to:
1. Create your Airtable base with 5 tables
2. Configure forms for data collection
3. Obtain your Personal Access Token
4. Get your Base ID

The system requires these tables:
- **Applicants** (parent table)
- **Personal Details** (linked to Applicants)
- **Work Experience** (linked to Applicants, one-to-many)
- **Salary Preferences** (linked to Applicants)
- **Shortlisted Leads** (auto-populated)

### 2. Install Python Dependencies

```bash
# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file from the template:

```bash
cp env.template .env
```

Then edit `.env` with your credentials:

```bash
# Airtable Configuration
AIRTABLE_PAT=your_personal_access_token_here
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: Custom Table Names (defaults shown)
# APPLICANTS_TABLE=Applicants
# PERSONAL_DETAILS_TABLE=Personal Details
# WORK_EXPERIENCE_TABLE=Work Experience
# SALARY_PREFERENCES_TABLE=Salary Preferences
# SHORTLISTED_LEADS_TABLE=Shortlisted Leads
```

**Important**: Never commit your `.env` file to version control. It's already included in `.gitignore`.

### 4. Obtain API Credentials

#### Airtable Personal Access Token (PAT)
1. Go to https://airtable.com
2. Click your profile picture → Account → Developer
3. Click "Personal access tokens" → "Create new token"
4. Token configuration:
   - Name: "Contractor Application Scripts"
   - Scopes: `data.records:read` and `data.records:write`
   - Access: Select your "Contractor Applications" base
5. Copy the token and add it to your `.env` file

#### Airtable Base ID
1. Go to https://airtable.com/api
2. Select your base
3. Copy the Base ID from the URL (format: `appXXXXXXXXXXXXXX`)

#### OpenAI API Key
1. Go to https://platform.openai.com
2. Navigate to API keys
3. Create a new key
4. Copy the key (starts with `sk-`) and add it to your `.env` file

## Usage

The system provides both a unified CLI interface and standalone scripts.

### Unified CLI Interface (Recommended)

The `cli.py` provides a single entry point for all operations:

```bash
# Compress a specific applicant's data
python cli.py compress --applicant-id 1

# Compress all applicants
python cli.py compress

# Decompress data back to tables
python cli.py decompress --applicant-id 1

# Evaluate a specific candidate (shortlist + LLM)
python cli.py evaluate --applicant-id 1

# Evaluate all candidates
python cli.py evaluate

# Evaluate without LLM (shortlist only)
python cli.py evaluate --skip-llm

# Run full pipeline (compress all + evaluate all)
python cli.py process-all
```

### Standalone Scripts

For specific operations, you can use individual scripts:

```bash
# Compression
python scripts/compress_data.py --applicant-id 1
python scripts/compress_data.py --all

# Decompression
python scripts/decompress_data.py --applicant-id 1

# Evaluation
python scripts/evaluate_candidates.py --applicant-id 1
python scripts/evaluate_candidates.py --all
python scripts/evaluate_candidates.py --all --skip-llm
python scripts/evaluate_candidates.py --all --llm-only
```

## How It Works

### 1. Data Compression

The compression process gathers data from multiple linked tables and creates a unified JSON structure:

```json
{
  "personal": {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "location": "NYC",
    "linkedin": "https://linkedin.com/in/janedoe"
  },
  "experience": [
    {
      "company": "Google",
      "title": "Software Engineer",
      "start": "2020-01-01",
      "end": "2023-06-01",
      "technologies": "Python, Go, Kubernetes"
    }
  ],
  "salary": {
    "preferred_rate": 85,
    "minimum_rate": 75,
    "currency": "USD",
    "availability": 30
  }
}
```

This JSON is stored in the `Compressed JSON` field of the Applicants table.

### 2. Data Decompression

The decompression process reads the JSON and upserts records back to the child tables:
- Updates or creates Personal Details (one-to-one)
- Replaces all Work Experience records (one-to-many)
- Updates or creates Salary Preferences (one-to-one)

This is useful when you need to edit applicant data via JSON and reflect changes back to the normalized structure.

### 3. Candidate Shortlisting

The system evaluates candidates against three criteria (all must be met):

#### Experience Criterion
- **Requirement**: ≥4 years total experience **OR** worked at a tier-1 company
- **Tier-1 Companies**: Google, Meta, OpenAI, Microsoft, Amazon, Apple, Netflix, Tesla, SpaceX, Uber, Airbnb, Stripe

#### Compensation Criterion
- **Requirement**: Preferred Rate ≤ $100 USD/hour **AND** Availability ≥ 20 hrs/week
- Note: Currently only USD currency is supported for accurate comparison

#### Location Criterion
- **Requirement**: Located in US, Canada, UK, Germany, or India

When all criteria are met:
- `Shortlist Status` field is checked
- A new record is created in `Shortlisted Leads` table
- `Score Reason` field contains a detailed explanation

### 4. LLM Evaluation

The system uses OpenAI's GPT-4-mini model to:
1. Generate a 75-word candidate summary
2. Assign a quality score from 1-10
3. Identify data gaps or inconsistencies
4. Suggest up to 3 follow-up questions

**Features**:
- **Budget Guardrails**: Token limits per call
- **Smart Caching**: Skips evaluation if JSON unchanged
- **Retry Logic**: 3 attempts with exponential backoff
- **Error Handling**: Comprehensive logging of failures

Results are stored in:
- `LLM Summary`: Concise candidate summary
- `LLM Score`: Quality score (1-10)
- `LLM Follow-Ups`: Suggested follow-up questions

## Customizing Shortlist Criteria

To modify the shortlist rules, edit `src/shortlist_evaluator.py`:

### Adding More Tier-1 Companies

```python
TIER_1_COMPANIES = {
    "Google", "Meta", "OpenAI", 
    # Add your companies here
    "YourCompany", "AnotherCompany"
}
```

### Changing Compensation Thresholds

Modify the `evaluate_compensation_criteria` function:

```python
rate_meets_criteria = preferred_rate <= 100  # Change to your threshold
availability_meets_criteria = availability >= 20  # Change to your threshold
```

### Adding/Removing Allowed Locations

```python
ALLOWED_LOCATIONS = {
    "US", "Canada", "UK", "Germany", "India",
    # Add more locations
    "Australia", "Singapore"
}
```

## Scheduling and Automation

### Cron Jobs (Linux/Mac)

Run the full pipeline daily at 2 AM:

```bash
crontab -e
```

Add this line:

```
0 2 * * * cd /path/to/mercor-mini-task && /path/to/venv/bin/python cli.py process-all >> logs/cron.log 2>&1
```

### Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 2 AM)
4. Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `cli.py process-all`
   - Start in: `C:\path\to\mercor-mini-task`

### Webhook Integration

To trigger on form submissions, you can:
1. Use Airtable Automations to call a webhook
2. Set up a simple web server that executes the CLI commands
3. Use services like Zapier or Make (formerly Integromat)

## Troubleshooting

### Authentication Errors

**Error**: `Invalid AIRTABLE_PAT format`
- Ensure your PAT is correct and has not expired
- Verify scopes include `data.records:read` and `data.records:write`
- Check that the token has access to your specific base

**Error**: `Invalid OPENAI_API_KEY format`
- Verify your API key starts with `sk-`
- Check that your API key is active at https://platform.openai.com

### Data Issues

**Error**: `No compressed JSON found`
- Run compression first: `python cli.py compress --applicant-id <ID>`

**Error**: `Applicant not found`
- Verify the Applicant ID exists in your Applicants table
- Check that the record has not been deleted

### API Rate Limits

If you encounter rate limit errors:
- Airtable: Has a 5 requests/second limit (per base)
- OpenAI: Depends on your account tier
- The system includes automatic retry logic

For batch operations, the system processes records sequentially to avoid rate limits.

### LLM Evaluation Failures

If LLM evaluation fails repeatedly:
- Check your OpenAI API key balance
- Verify network connectivity
- Review logs for specific error messages
- The system will retry up to 3 times with exponential backoff

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

### Code Style

The codebase follows:
- PEP 8 style guide
- Snake case for functions and variables
- Comprehensive docstrings
- Type hints where appropriate

### Contributing

When making changes:
1. Follow the existing code patterns
2. Add comprehensive error handling
3. Update documentation
4. Add logging for important operations

## Security Best Practices

1. **Never commit credentials**: Always use `.env` for secrets
2. **Rotate keys regularly**: Change API keys periodically
3. **Limit token scopes**: Only grant necessary Airtable permissions
4. **Monitor usage**: Track API usage to detect anomalies
5. **Secure your `.env`**: Set proper file permissions (chmod 600)

## Support and Documentation

- **Airtable API Documentation**: https://airtable.com/api
- **OpenAI API Documentation**: https://platform.openai.com/docs
- **pyairtable Library**: https://github.com/gtalarico/pyairtable

## License

This project is provided as-is for the Mercor Mini-Interview Task.

## Deliverables

This project fulfills all requirements from the PRD:

1. **Airtable Base**: Follow `AIRTABLE_SETUP.md` to create the base
2. **Local Python Scripts**: 
   - Compression: `src/json_compressor.py`
   - Decompression: `src/json_decompressor.py`
   - Shortlisting: `src/shortlist_evaluator.py`
   - LLM Evaluation: `src/llm_evaluator.py`
3. **Automation System**: CLI and standalone scripts for all operations
4. **Documentation**: This README, plus detailed setup guide
5. **LLM Integration**: OpenAI with retry logic and budget guardrails
6. **Extensibility**: Easy customization of shortlist criteria

## Quick Start Summary

```bash
# 1. Set up Airtable (see AIRTABLE_SETUP.md)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file with your credentials
cp env.template .env
# Edit .env with your API keys

# 4. Verify your setup
python verify_setup.py

# 5. Add test applicants through Airtable forms

# 6. Run the full pipeline
python cli.py process-all

# 7. Check results in your Airtable base
```

For questions or issues, review the troubleshooting section or check the inline code documentation.

