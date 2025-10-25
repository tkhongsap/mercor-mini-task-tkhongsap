# Quick Test Guide

## Run All Tests

```bash
# Simple run
python tests/test_runner.py

# Verbose output
python tests/test_runner.py --verbose
```

## What Gets Tested

The test suite validates all 5 Airtable tables against PRD requirements:

### 53 Total Tests

#### Schema Structure (4 tests)
- Environment variables loaded
- Airtable connection works
- All 5 tables exist
- No extra tables

#### Applicants Table (8 tests)
- Table exists
- 6 required fields present
- Field types correct (autoNumber, multilineText, checkbox, richText, number)
- 4 linked record fields to child tables

#### Personal Details Table (7 tests)
- 5 required fields present
- Field types correct (singleLineText, email, url)
- Linked to Applicants table

#### Work Experience Table (7 tests)
- 6 required fields present
- Field types correct (singleLineText, date)
- Linked to Applicants table

#### Salary Preferences Table (8 tests)
- 5 required fields present
- Field types correct (number with precision)
- Currency single-select with 5 options (USD, EUR, GBP, CAD, INR)
- Linked to Applicants table

#### Shortlisted Leads Table (6 tests)
- 4 required fields present
- Field types correct (multipleRecordLinks, multilineText, dateTime)
- Linked to Applicants table

#### Linked Relationships (5 tests)
- Bidirectional links between Applicants and all child tables
- All child tables link back to Applicants

#### PRD Compliance (6 tests)
- All tables match PRD exactly
- All required fields present with correct names

## Expected Output

```
======================================================================
Test Summary
======================================================================
Tests Run: 53
Successes: 53
Failures: 0
Errors: 0
Skipped: 0

✓ ALL TESTS PASSED - Schema is 100% PRD compliant!
```

## Troubleshooting

If tests fail:

1. **Authentication Error**
   - Check `.env` file has correct credentials
   - Verify PAT has required scopes

2. **Table Not Found**
   - Run `python setup_airtable_schema.py` to create tables
   - Check table names match exactly (case-sensitive)

3. **Field Not Found**
   - Run `python tests/verify_prd_schema.py` for detailed diagnostics
   - Check field names and types

## Other Verification Tools

```bash
# Verify PRD compliance (detailed report)
python tests/verify_prd_schema.py

# Test authentication only
python tests/test_auth.py

# General schema check
python tests/verify_schema.py
```

## CI/CD Integration

Exit codes:
- `0` = All tests passed
- `1` = Tests failed

Use in automation:
```bash
python tests/test_runner.py && echo "Schema valid" || echo "Schema invalid"
```
