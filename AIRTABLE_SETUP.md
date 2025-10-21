# Airtable Base Setup Guide

This guide walks you through setting up your Airtable base for the Contractor Application System.

## Step 1: Create a New Base

1. Log in to your Airtable account at https://airtable.com
2. Click "Create a base" or the "+" button
3. Choose "Start from scratch"
4. Name your base: **Contractor Applications**

## Step 2: Create Tables and Fields

You need to create 5 tables with specific fields. Follow these exact specifications:

### Table 1: Applicants (Parent Table)

This is the main table that all others link to.

**Fields:**
1. `Applicant ID` - **Number** field (Auto number format)
   - Set as Primary field
   - Configure: Field type → Number → Auto number
2. `Compressed JSON` - **Long text** field
   - This will store the compressed JSON representation
3. `Shortlist Status` - **Checkbox** field
   - Automatically checked when candidate meets criteria
4. `LLM Summary` - **Long text** field
   - Stores AI-generated summary (75 words max)
5. `LLM Score` - **Number** field (Integer, 1-10)
   - Quality score assigned by AI
6. `LLM Follow-Ups` - **Long text** field
   - AI-suggested follow-up questions

### Table 2: Personal Details

**Fields:**
1. `Record ID` - **Auto-generated** (default primary field, can rename or keep)
2. `Full Name` - **Single line text** field
3. `Email` - **Email** field
4. `Location` - **Single line text** field
5. `LinkedIn` - **URL** field
6. `Applicant ID` - **Link to another record** field
   - Link to: **Applicants** table
   - Relationship: Allow linking to multiple records (but typically 1:1)
   - In the Applicants table, name the linked field: "Personal Details"

### Table 3: Work Experience

This table has a **one-to-many** relationship (one applicant can have multiple work experiences).

**Fields:**
1. `Record ID` - **Auto-generated** (default primary field)
2. `Company` - **Single line text** field
3. `Title` - **Single line text** field
4. `Start` - **Date** field
   - Format: MM/DD/YYYY or your preferred format
5. `End` - **Date** field
   - Format: MM/DD/YYYY (can be empty for current positions)
6. `Technologies` - **Single line text** field
   - Comma-separated list of technologies
7. `Applicant ID` - **Link to another record** field
   - Link to: **Applicants** table
   - Allow linking to multiple records: OFF (each experience links to ONE applicant)
   - In the Applicants table, name the linked field: "Work Experience"

### Table 4: Salary Preferences

**Fields:**
1. `Record ID` - **Auto-generated** (default primary field)
2. `Preferred Rate` - **Number** field (Decimal, precision: 2)
   - Format: Decimal (allows values like 85.50)
3. `Minimum Rate` - **Number** field (Decimal, precision: 2)
4. `Currency` - **Single select** field
   - Options: USD, EUR, GBP, CAD, INR
   - Add more currencies as needed
5. `Availability (hrs/wk)` - **Number** field (Integer)
   - Hours per week available
6. `Applicant ID` - **Link to another record** field
   - Link to: **Applicants** table
   - In the Applicants table, name the linked field: "Salary Preferences"

### Table 5: Shortlisted Leads

This table is auto-populated by the Python scripts when candidates meet criteria.

**Fields:**
1. `Record ID` - **Auto-generated** (default primary field)
2. `Applicant` - **Link to another record** field
   - Link to: **Applicants** table
   - In the Applicants table, name the linked field: "Shortlisted"
3. `Compressed JSON` - **Long text** field
   - Copy of applicant's compressed data
4. `Score Reason` - **Long text** field
   - Human-readable explanation of why candidate was shortlisted
5. `Created At` - **Created time** field
   - Automatically tracks when record was created

## Step 3: Create Forms for Data Collection

Airtable forms cannot write to multiple tables simultaneously, so we need **three separate forms**.

### Form 1: Personal Details Form

1. Go to **Personal Details** table
2. Click "Create form" in the top-right toolbar
3. Add these fields to the form:
   - Full Name (required)
   - Email (required)
   - Location (required)
   - LinkedIn (optional)
   - Applicant ID (hidden - will be auto-created or pre-filled)
4. Configure form settings:
   - Form name: "Step 1: Personal Information"
   - After submission message: "Thank you! Your Applicant ID is [Applicant ID]. Please save this for the next steps."
5. **Important:** Copy the form URL - you'll need it

### Form 2: Work Experience Form

1. Go to **Work Experience** table
2. Click "Create form"
3. Add these fields:
   - Applicant ID (required - will be pre-filled via URL)
   - Company (required)
   - Title (required)
   - Start (required)
   - End (optional)
   - Technologies (optional)
4. Form settings:
   - Form name: "Step 2: Work Experience"
   - After submission message: "Experience added! You can submit this form multiple times to add more positions, or proceed to Step 3 for Salary Preferences."
5. **Enable pre-filling:**
   - In form settings, click "Prefill link" option
   - Select "Applicant ID" field to be pre-filled
   - Copy the base URL with prefill parameter

### Form 3: Salary Preferences Form

1. Go to **Salary Preferences** table
2. Click "Create form"
3. Add these fields:
   - Applicant ID (required - will be pre-filled via URL)
   - Preferred Rate (required)
   - Minimum Rate (required)
   - Currency (required)
   - Availability (hrs/wk) (required)
4. Form settings:
   - Form name: "Step 3: Salary Preferences"
   - After submission message: "Application complete! We'll review your profile and contact you if there's a match."

### Linking Forms Together

To create a smooth workflow, you can:
1. Use URL parameters to pre-fill the Applicant ID between forms
2. Create a landing page with instructions
3. Example flow:
   - User fills Form 1 → Gets Applicant ID (e.g., "123")
   - User clicks link to Form 2 with URL: `form2-url?prefill_Applicant+ID=123`
   - User clicks link to Form 3 with URL: `form3-url?prefill_Applicant+ID=123`

## Step 4: Obtain Your Personal Access Token (PAT)

1. Click on your profile picture in the top-right corner
2. Go to "Account" or "Settings"
3. Navigate to "Developer" tab
4. Click "Personal access tokens"
5. Click "Create new token"
6. Token configuration:
   - Name: "Contractor Application Scripts"
   - Scopes needed:
     - `data.records:read` - Read records
     - `data.records:write` - Create/update records
     - `schema.bases:read` - Read base schema
   - Access: Select your "Contractor Applications" base
7. Click "Create token"
8. **IMPORTANT:** Copy the token immediately - you won't see it again
9. Save it securely - you'll add it to your `.env` file

## Step 5: Get Your Base ID

1. Go to https://airtable.com/api
2. Select your "Contractor Applications" base
3. Your Base ID is shown at the top of the documentation page
   - Format: `appXXXXXXXXXXXXXX` (starts with "app")
4. Copy this ID - you'll need it for your `.env` file

## Step 6: Get Your Table IDs (Optional but Recommended)

The Python scripts will reference tables by name, but you can also use IDs:

1. From the API documentation page, click on any table
2. Look at the URL - table ID is in the format `tblXXXXXXXXXXXXXX`
3. Alternatively, the `pyairtable` library can reference tables by name, which is easier

**Table Names to Use in Scripts:**
- Applicants
- Personal Details
- Work Experience
- Salary Preferences
- Shortlisted Leads

## Step 7: Share Your Base (For Deliverable)

1. Click "Share" button in the top-right of your base
2. Choose "Create a shared link to the whole base"
3. Set permissions: "Read only" (or as appropriate)
4. Copy the share link - this is part of your project deliverable

## Verification Checklist

Before proceeding to run Python scripts:

- [ ] 5 tables created with exact field names and types
- [ ] All linked record relationships configured
- [ ] 3 forms created and tested with sample data
- [ ] Personal Access Token obtained and saved securely
- [ ] Base ID copied
- [ ] Base share link created

## Troubleshooting

**Issue: Cannot create linked record field**
- Make sure both tables exist before creating the link
- Double-check you're selecting the correct table to link to

**Issue: Form doesn't show Applicant ID**
- For Form 1: Applicant ID can be auto-generated or hidden
- For Forms 2 & 3: Use the prefill URL feature to pass the ID

**Issue: Personal Access Token doesn't work**
- Verify you've granted the correct scopes (read and write)
- Ensure you've selected the specific base in token permissions
- Token must have `data.records:read` and `data.records:write`

## Next Steps

Once your Airtable base is set up:
1. Create a `.env` file with your credentials (see `.env.example`)
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run the compression script to test: `python scripts/compress_data.py`
4. Refer to `README.md` for full usage instructions

