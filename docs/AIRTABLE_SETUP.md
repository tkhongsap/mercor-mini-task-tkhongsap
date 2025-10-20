# Airtable Setup Guide

This guide walks you through setting up the Airtable base for the Mercor Contractor Application System.

## Table of Contents

1. [Create a New Base](#create-a-new-base)
2. [Table Schemas](#table-schemas)
3. [Create Forms](#create-forms)
4. [Get API Credentials](#get-api-credentials)
5. [Testing the Setup](#testing-the-setup)

## Create a New Base

1. Log in to [Airtable](https://airtable.com)
2. Click "Add a base" or "Create a new base"
3. Choose "Start from scratch"
4. Name your base: "Contractor Applications" (or any name you prefer)

## Table Schemas

You need to create 5 tables with specific fields and relationships.

### Table 1: Applicants (Parent Table)

This is the main table that stores one row per applicant.

**Fields:**

| Field Name | Field Type | Description |
|------------|------------|-------------|
| Applicant ID | Single line text (Primary Field) | Unique identifier for each applicant |
| Compressed JSON | Long text | Stores the compressed JSON representation |
| Shortlist Status | Single select | Options: "Pending", "Shortlisted", "Not Shortlisted" |
| LLM Summary | Long text | Summary from Claude (≤75 words) |
| LLM Score | Number | Quality score from 1-10 |
| LLM Follow-Ups | Long text | Suggested follow-up questions |
| LLM Issues | Long text | Data gaps or inconsistencies |
| JSON Hash | Single line text | Hash for deduplication (internal use) |
| Created Time | Created time | Auto-populated |

**Setup Steps:**

1. Rename the default "Table 1" to "Applicants"
2. Rename the default "Name" field to "Applicant ID"
3. Add each additional field using the "+" button
4. For "Shortlist Status", add options: "Pending", "Shortlisted", "Not Shortlisted"

### Table 2: Personal Details

Stores personal information (one-to-one with Applicants).

**Fields:**

| Field Name | Field Type | Description |
|------------|------------|-------------|
| Record ID | Autonumber (Primary Field) | Auto-generated ID |
| Applicant ID | Link to another record | Links to Applicants table |
| Full Name | Single line text | Applicant's full name |
| Email | Email | Applicant's email address |
| Location | Single line text | City/Country |
| LinkedIn | URL | LinkedIn profile URL |

**Setup Steps:**

1. Create new table: Click "+" next to table tabs, name it "Personal Details"
2. Delete or rename the default "Name" field to "Record ID", change type to "Autonumber"
3. Add "Applicant ID" field:
   - Type: "Link to another record"
   - Choose "Applicants" table
   - Choose "Allow linking to multiple records" = OFF (one-to-one)
4. Add remaining fields with appropriate types

### Table 3: Work Experience

Stores work history (one-to-many with Applicants).

**Fields:**

| Field Name | Field Type | Description |
|------------|------------|-------------|
| Record ID | Autonumber (Primary Field) | Auto-generated ID |
| Applicant ID | Link to another record | Links to Applicants table |
| Company | Single line text | Company name |
| Title | Single line text | Job title |
| Start | Date | Start date |
| End | Date | End date (empty if current) |
| Technologies | Long text | Technologies used |

**Setup Steps:**

1. Create new table: "Work Experience"
2. Set up "Record ID" as autonumber
3. Add "Applicant ID" field:
   - Type: "Link to another record"
   - Choose "Applicants" table
   - Choose "Allow linking to multiple records" = ON (one-to-many)
4. Add remaining fields

### Table 4: Salary Preferences

Stores compensation preferences (one-to-one with Applicants).

**Fields:**

| Field Name | Field Type | Description |
|------------|------------|-------------|
| Record ID | Autonumber (Primary Field) | Auto-generated ID |
| Applicant ID | Link to another record | Links to Applicants table |
| Preferred Rate | Number | Preferred hourly rate |
| Minimum Rate | Number | Minimum acceptable rate |
| Currency | Single select | Options: "USD", "EUR", "GBP", "INR", "CAD" |
| Availability (hrs/wk) | Number | Hours available per week |

**Setup Steps:**

1. Create new table: "Salary Preferences"
2. Set up "Record ID" as autonumber
3. Add "Applicant ID" field (one-to-one link to Applicants)
4. Add number fields with appropriate decimal precision
5. For "Currency", add options: USD, EUR, GBP, INR, CAD

### Table 5: Shortlisted Leads

Auto-populated when candidates meet shortlisting criteria.

**Fields:**

| Field Name | Field Type | Description |
|------------|------------|-------------|
| Record ID | Autonumber (Primary Field) | Auto-generated ID |
| Applicant | Link to another record | Links to Applicants table |
| Compressed JSON | Long text | Copy of compressed JSON |
| Score Reason | Long text | Human-readable explanation |
| Created At | Date & time | When shortlisted |

**Setup Steps:**

1. Create new table: "Shortlisted Leads"
2. Set up "Record ID" as autonumber
3. Add "Applicant" field (link to Applicants table)
4. Add remaining fields

## Create Forms

Airtable forms can only write to one table at a time. Create three separate forms:

### Form 1: Personal Details Form

1. Go to Personal Details table
2. Click "Form" view button at the top
3. Create new form view: "Application Form - Personal"
4. Configure fields to show:
   - Applicant ID (ask user to enter their unique ID)
   - Full Name
   - Email
   - Location
   - LinkedIn
5. Share form link with applicants

### Form 2: Work Experience Form

1. Go to Work Experience table
2. Create form view: "Application Form - Experience"
3. Configure fields (include Applicant ID)
4. Note: Applicants can submit this form multiple times for multiple experiences

### Form 3: Salary Preferences Form

1. Go to Salary Preferences table
2. Create form view: "Application Form - Salary"
3. Configure fields (include Applicant ID)

### Form Workflow

Instruct applicants to:
1. Generate or receive a unique Applicant ID
2. Fill out all three forms using the same Applicant ID
3. Submit each form

## Get API Credentials

### Step 1: Get Your Base ID

1. Go to [Airtable API Documentation](https://airtable.com/api)
2. Select your base ("Contractor Applications")
3. Look for the base ID in the URL or in the introduction section
4. Format: `appXXXXXXXXXXXXXX`
5. Copy this value for your `.env` file

### Step 2: Create a Personal Access Token

1. Go to [Airtable Account Settings](https://airtable.com/create/tokens)
2. Click "Create new token"
3. Name it: "Mercor Contractor System"
4. Add these scopes:
   - `data.records:read`
   - `data.records:write`
   - `schema.bases:read`
5. Add access to your specific base ("Contractor Applications")
6. Click "Create token"
7. Copy the token (you won't be able to see it again!)
8. This is your `AIRTABLE_API_KEY`

### Step 3: Get Anthropic API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to "API Keys" in settings
4. Click "Create Key"
5. Name it: "Mercor Contractor System"
6. Copy the API key
7. This is your `ANTHROPIC_API_KEY`

### Step 4: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your credentials:
   ```
   AIRTABLE_API_KEY=your_actual_api_key_here
   AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
   ANTHROPIC_API_KEY=your_anthropic_key_here
   ```

3. Never commit the `.env` file to Git!

## Testing the Setup

### Test 1: Verify Configuration

```bash
cd scripts
python config.py
```

Expected output:
```
Configuration validated successfully!
Base ID: appXXXXXXXXXXXXXX
Claude Model: claude-3-5-sonnet-20241022
Max Tokens: 1000
```

### Test 2: Create Test Data

1. Manually create a test applicant in Airtable:
   - In Applicants table, create a record with Applicant ID: "TEST001"
   - In Personal Details, create a record:
     - Link to TEST001
     - Full Name: "John Doe"
     - Email: "john@example.com"
     - Location: "San Francisco, US"
     - LinkedIn: "https://linkedin.com/in/johndoe"

   - In Work Experience, create 1-2 records:
     - Link to TEST001
     - Company: "Google"
     - Title: "Software Engineer"
     - Start: 2018-01-01
     - End: 2022-12-31
     - Technologies: "Python, React, PostgreSQL"

   - In Salary Preferences, create a record:
     - Link to TEST001
     - Preferred Rate: 90
     - Minimum Rate: 75
     - Currency: USD
     - Availability: 30

### Test 3: Run Compression

```bash
python compress.py --applicant-id TEST001
```

Expected: Compressed JSON appears in Applicants table, shortlist evaluation runs, LLM evaluation runs.

### Test 4: Run Decompression

1. Manually edit the Compressed JSON in Airtable
2. Run:
   ```bash
   python decompress.py --applicant-id TEST001
   ```
3. Verify child tables are updated with the new JSON data

## Troubleshooting

### "Configuration validation failed"

- Check that your `.env` file exists and has the correct keys
- Verify API keys are valid and not expired

### "Could not find table"

- Check table names exactly match those in `config.py`
- Table names are case-sensitive

### "Permission denied"

- Verify your Airtable token has the required scopes
- Ensure the token has access to the specific base

### "Link field not working"

- Make sure linked records exist in the parent table first
- Use record IDs (not field values) when linking via API

## Next Steps

Once your Airtable base is set up and tested:

1. Review `docs/DOCUMENTATION.md` for complete system documentation
2. Customize shortlisting criteria in `scripts/config.py`
3. Set up regular processing workflows
4. Create views and dashboards in Airtable for your team

## Additional Resources

- [Airtable API Documentation](https://airtable.com/api)
- [Airtable Field Types Reference](https://support.airtable.com/hc/en-us/articles/360055885353)
- [Anthropic API Documentation](https://docs.anthropic.com/)
