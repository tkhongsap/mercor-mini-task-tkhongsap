# Quick Reference Card

## Essential Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.template .env
nano .env  # Add your credentials

# Verify setup
python verify_setup.py
```

### CLI Commands

```bash
# Compress data
python cli.py compress --applicant-id 1
python cli.py compress  # All applicants

# Decompress data
python cli.py decompress --applicant-id 1

# Evaluate candidates
python cli.py evaluate --applicant-id 1
python cli.py evaluate  # All applicants
python cli.py evaluate --skip-llm  # Without LLM

# Full pipeline
python cli.py process-all
```

### Standalone Scripts

```bash
# Compression
python scripts/compress_data.py --applicant-id 1
python scripts/compress_data.py --all

# Decompression
python scripts/decompress_data.py --applicant-id 1

# Evaluation
python scripts/evaluate_candidates.py --all
python scripts/evaluate_candidates.py --applicant-id 1
python scripts/evaluate_candidates.py --all --skip-llm
```

## Environment Variables

Required in `.env`:
```bash
AIRTABLE_PAT=your_token_here          # From Airtable → Account → Developer
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX   # From Airtable API documentation page
OPENAI_API_KEY=sk-your-key-here       # From OpenAI platform
```

## Airtable Tables

1. **Applicants** - Parent table with compressed JSON and LLM results
2. **Personal Details** - Full Name, Email, Location, LinkedIn
3. **Work Experience** - Company, Title, Start, End, Technologies
4. **Salary Preferences** - Rates, Currency, Availability
5. **Shortlisted Leads** - Auto-populated for qualified candidates

## Shortlist Criteria

All three must be met:

1. **Experience**: ≥4 years OR tier-1 company (Google, Meta, OpenAI, etc.)
2. **Compensation**: Preferred Rate ≤$100/hr AND Availability ≥20 hrs/week
3. **Location**: US, Canada, UK, Germany, or India

## JSON Structure

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
      "technologies": "Python, Go"
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

## LLM Output Fields

- **LLM Summary**: 75-word candidate summary
- **LLM Score**: Quality score from 1-10
- **LLM Follow-Ups**: Suggested follow-up questions

## Common Workflows

### Process New Applicant
```bash
# 1. Applicant fills out 3 forms in Airtable
# 2. Compress their data
python cli.py compress --applicant-id <ID>

# 3. Evaluate them
python cli.py evaluate --applicant-id <ID>

# 4. Check results in Airtable
```

### Batch Process All Applicants
```bash
python cli.py process-all
```

### Edit Applicant Data
```bash
# 1. Edit Compressed JSON in Airtable
# 2. Decompress to update child tables
python cli.py decompress --applicant-id <ID>
```

## Troubleshooting

### Setup Issues
```bash
python verify_setup.py  # Check your configuration
```

### Common Errors

**"No compressed JSON found"**
```bash
python cli.py compress --applicant-id <ID>
```

**"Invalid AIRTABLE_PAT format"**
- Check your Personal Access Token
- Verify it has correct scopes
- Ensure it has access to your base

**"Applicant not found"**
- Verify the Applicant ID exists
- Check you're using the correct base

## File Locations

- Configuration: `src/config.py`
- Airtable client: `src/airtable_client.py`
- Compression: `src/json_compressor.py`
- Decompression: `src/json_decompressor.py`
- Shortlisting: `src/shortlist_evaluator.py`
- LLM: `src/llm_evaluator.py`

## Documentation

- Full setup: `AIRTABLE_SETUP.md`
- User guide: `README.md`
- Deliverables: `DELIVERABLES.md`
- This reference: `QUICK_REFERENCE.md`

## Support

For detailed information:
1. Check README.md for comprehensive documentation
2. Review AIRTABLE_SETUP.md for setup help
3. Examine inline code documentation
4. Run `python verify_setup.py` for diagnostics

