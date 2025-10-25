# Mercor Mini-Interview Task - Deliverables Checklist

## Project Overview

Build an Airtable-based contractor application system with automated data processing, candidate evaluation, and LLM-powered enrichment.

## Current Status

**Phase**: Airtable Base Setup
**Progress**: Applicants table completed (6 fields)
**Next**: Create 4 child tables, build Python automation scripts

---

## PRD Requirements Breakdown

### 1. Airtable Base Setup

**Requirement**: Create a base with 5 linked tables

**Tables to Create**:

#### Table 1: Applicants (Parent Table) - ✅ COMPLETED
- [x] Applicant ID (Number, Auto number) - Primary field
- [x] Compressed JSON (Long text, plain text only)
- [x] Shortlist Status (Checkbox)
- [x] LLM Summary (Long text, rich text OK)
- [x] LLM Score (Number, Integer, 1-10)
- [x] LLM Follow-Ups (Long text, rich text OK)

**Note**: Verify Compressed JSON is plain text (not rich text) for JSON compatibility

#### Table 2: Personal Details - ⏳ PENDING
- [ ] Record ID (Auto-generated primary field)
- [ ] Full Name (Single line text)
- [ ] Email (Email field)
- [ ] Location (Single line text)
- [ ] LinkedIn (URL field)
- [ ] Applicant ID (Link to Applicants table)
  - Creates "Personal Details" linked field in Applicants

#### Table 3: Work Experience - ⏳ PENDING
- [ ] Record ID (Auto-generated primary field)
- [ ] Company (Single line text)
- [ ] Title (Single line text)
- [ ] Start (Date field)
- [ ] End (Date field)
- [ ] Technologies (Single line text)
- [ ] Applicant ID (Link to Applicants table)
  - Creates "Work Experience" linked field in Applicants
  - One-to-many relationship

#### Table 4: Salary Preferences - ⏳ PENDING
- [ ] Record ID (Auto-generated primary field)
- [ ] Preferred Rate (Number, Decimal, precision 2)
- [ ] Minimum Rate (Number, Decimal, precision 2)
- [ ] Currency (Single select: USD, EUR, GBP, CAD, INR)
- [ ] Availability (hrs/wk) (Number, Integer)
- [ ] Applicant ID (Link to Applicants table)
  - Creates "Salary Preferences" linked field in Applicants

#### Table 5: Shortlisted Leads - ⏳ PENDING
- [ ] Record ID (Auto-generated primary field)
- [ ] Applicant (Link to Applicants table)
  - Creates "Shortlisted" linked field in Applicants
- [ ] Compressed JSON (Long text, plain text)
- [ ] Score Reason (Long text, rich text OK)
- [ ] Created At (Created time field)

---

### 2. User Input Flow

**Requirement**: Create 3 Airtable forms for data collection

#### Form 1: Personal Details Form - ⏳ PENDING
- [ ] Create form from Personal Details table
- [ ] Include fields: Full Name, Email, Location, LinkedIn, Applicant ID
- [ ] Configure "After submission" message to show Applicant ID
- [ ] Copy form URL

#### Form 2: Work Experience Form - ⏳ PENDING
- [ ] Create form from Work Experience table
- [ ] Include fields: Applicant ID, Company, Title, Start, End, Technologies
- [ ] Enable prefill for Applicant ID field
- [ ] Allow multiple submissions per applicant
- [ ] Copy prefill URL

#### Form 3: Salary Preferences Form - ⏳ PENDING
- [ ] Create form from Salary Preferences table
- [ ] Include fields: Applicant ID, Preferred Rate, Minimum Rate, Currency, Availability
- [ ] Enable prefill for Applicant ID field
- [ ] Copy prefill URL

---

### 3. JSON Compression Automation

**Requirement**: Python script to compress multi-table data into JSON

**Script to Build**: `compress_data.py`

**Functionality**:
- [ ] Read data from Personal Details table (by Applicant ID)
- [ ] Read data from Work Experience table (all records for Applicant ID)
- [ ] Read data from Salary Preferences table (by Applicant ID)
- [ ] Build JSON structure:
  ```json
  {
    "personal": { "name": "...", "email": "...", "location": "...", "linkedin": "..." },
    "experience": [
      { "company": "...", "title": "...", "start": "...", "end": "...", "technologies": "..." }
    ],
    "salary": { "preferred_rate": ..., "minimum_rate": ..., "currency": "...", "availability": ... }
  }
  ```
- [ ] Write JSON to Applicants.Compressed JSON field
- [ ] Handle missing/incomplete data gracefully
- [ ] Support single applicant and batch processing

**Dependencies Needed**:
- [ ] pyairtable (Airtable API client)
- [ ] python-dotenv (Environment variables)
- [ ] JSON library (built-in)

---

### 4. JSON Decompression Automation

**Requirement**: Python script to decompress JSON back to tables

**Script to Build**: `decompress_data.py`

**Functionality**:
- [ ] Read Compressed JSON from Applicants table
- [ ] Parse JSON
- [ ] Upsert Personal Details record (one-to-one)
- [ ] Delete existing Work Experience records for applicant
- [ ] Create new Work Experience records from JSON (one-to-many)
- [ ] Upsert Salary Preferences record (one-to-one)
- [ ] Maintain proper Applicant ID links
- [ ] Handle errors gracefully

---

### 5. Lead Shortlist Automation

**Requirement**: Auto-shortlist candidates based on multi-factor rules

**Script to Build**: `shortlist_evaluator.py`

**Evaluation Criteria** (ALL must be met):

#### Experience Criterion
- [ ] Calculate total years of experience from Work Experience records
- [ ] Check if >= 4 years total experience
- [ ] OR check if worked at tier-1 company (Google, Meta, OpenAI, Microsoft, Amazon, Apple, Netflix, Tesla, SpaceX, Uber, Airbnb, Stripe)
- [ ] Pass if either condition is true

#### Compensation Criterion
- [ ] Check Preferred Rate <= $100 USD/hour
- [ ] AND Availability >= 20 hrs/week
- [ ] Both must be true

#### Location Criterion
- [ ] Check if location is in: US, Canada, UK, Germany, India
- [ ] Handle variations (USA, United States, etc.)

**If All Criteria Met**:
- [ ] Set Shortlist Status checkbox to TRUE
- [ ] Create new record in Shortlisted Leads table
- [ ] Copy Compressed JSON to Shortlisted Leads
- [ ] Generate Score Reason with detailed explanation
- [ ] Set Created At timestamp

**Score Reason Format**:
```
Candidate qualifies for shortlist:
- Experience: [reason]
- Compensation: $X/hr rate, Y hrs/week availability
- Location: [country]
```

---

### 6. LLM Evaluation & Enrichment

**Requirement**: Use LLM to evaluate and enrich applications

**Script to Build**: `llm_evaluator.py`

**LLM Provider**: OpenAI, Anthropic, or Gemini (recommend OpenAI for simplicity)

**Trigger**: After Compressed JSON is written or updated

**Authentication**:
- [ ] Read API key from environment variable (NOT hardcoded)
- [ ] Store in .env file
- [ ] Validate API key format on startup

**Prompt Template**:
```
You are a recruiting analyst. Given this JSON applicant profile, do four things:
1. Provide a concise 75-word summary.
2. Rate overall candidate quality from 1-10 (higher is better).
3. List any data gaps or inconsistencies you notice.
4. Suggest up to three follow-up questions to clarify gaps.

Applicant Data:
{json_data}

Return exactly:
Summary: <text>
Score: <integer>
Issues: <comma-separated list or 'None'>
Follow-Ups: <bullet list>
```

**Functionality**:
- [ ] Read Compressed JSON
- [ ] Send to LLM with prompt
- [ ] Parse LLM response
- [ ] Write to LLM Summary field (75 words max)
- [ ] Write to LLM Score field (1-10)
- [ ] Write to LLM Follow-Ups field (bullet list)

**Error Handling**:
- [ ] Retry up to 3 times with exponential backoff
- [ ] Log errors
- [ ] Continue processing even if LLM fails

**Budget Guardrails**:
- [ ] Cap tokens per call (max 1000 output tokens)
- [ ] Track if JSON changed since last evaluation
- [ ] Skip LLM call if JSON unchanged (caching)

---

## Python Project Structure

```
mercor-mini-task/
├── compress_data.py          # JSON compression script
├── decompress_data.py        # JSON decompression script
├── shortlist_evaluator.py    # Candidate shortlist automation
├── llm_evaluator.py          # LLM evaluation integration
├── airtable_client.py        # Airtable API wrapper (helper)
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── .env                      # API credentials (gitignored)
├── env.template              # Environment variable template
├── prd.md                    # Requirements document
├── DELIVERABLES.md           # This file
├── PROJECT_SUMMARY.md        # Implementation roadmap
└── README.md                 # Usage documentation
```

---

## Dependencies to Install

**requirements.txt**:
```
pyairtable>=2.3.0    # Airtable API client
openai>=1.0.0        # OpenAI API client (if using OpenAI)
python-dotenv>=1.0.0 # Environment variable management
```

---

## Environment Variables (.env)

```bash
# Airtable Configuration
AIRTABLE_PAT=your_personal_access_token_here
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX

# LLM Configuration (choose one)
OPENAI_API_KEY=sk-your-openai-api-key-here
# OR
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional: Table Names (if different from defaults)
APPLICANTS_TABLE=Applicants
PERSONAL_DETAILS_TABLE=Personal Details
WORK_EXPERIENCE_TABLE=Work Experience
SALARY_PREFERENCES_TABLE=Salary Preferences
SHORTLISTED_LEADS_TABLE=Shortlisted Leads
```

---

## Testing Checklist

### Airtable Base Testing
- [ ] All 5 tables created with correct field types
- [ ] Linked record relationships working
- [ ] Forms accessible and functional
- [ ] Test data can be submitted via forms

### Compression Script Testing
- [ ] Successfully reads from 3 child tables
- [ ] Generates correct JSON structure
- [ ] Writes to Compressed JSON field
- [ ] Handles missing data gracefully
- [ ] Batch processing works

### Decompression Script Testing
- [ ] Reads Compressed JSON correctly
- [ ] Upserts Personal Details (updates existing)
- [ ] Replaces Work Experience records (deletes old, creates new)
- [ ] Upserts Salary Preferences
- [ ] Maintains data integrity

### Shortlist Evaluator Testing
**Test Case 1**: Qualified (4+ years experience)
- [ ] Candidate with 5 years experience passes
- [ ] Shortlist Status checkbox set
- [ ] Shortlisted Leads record created
- [ ] Score Reason populated

**Test Case 2**: Qualified (tier-1 company)
- [ ] Candidate with 2 years at Google passes
- [ ] Shortlisted correctly

**Test Case 3**: Not Qualified (experience)
- [ ] Candidate with 2 years at startup fails
- [ ] Not shortlisted

**Test Case 4**: Not Qualified (compensation)
- [ ] Candidate with $150/hr rate fails
- [ ] Not shortlisted

**Test Case 5**: Not Qualified (location)
- [ ] Candidate in Brazil fails
- [ ] Not shortlisted

### LLM Evaluator Testing
- [ ] Successfully calls LLM API
- [ ] Generates 75-word summary
- [ ] Assigns score 1-10
- [ ] Identifies data gaps
- [ ] Suggests follow-up questions
- [ ] Writes to correct fields
- [ ] Retry logic works on failures
- [ ] Caching prevents duplicate calls

---

## Submission Checklist

### Airtable Base
- [ ] Create share link (read-only or comment access)
- [ ] Verify all tables visible in share link
- [ ] Include sample data (3-5 test applicants)

### Code Repository
- [ ] All Python scripts included
- [ ] requirements.txt with dependencies
- [ ] env.template (NO actual credentials)
- [ ] .env in .gitignore
- [ ] README.md with usage instructions

### Documentation
- [ ] DELIVERABLES.md (this file)
- [ ] PROJECT_SUMMARY.md (implementation roadmap)
- [ ] README.md (setup and usage guide)
- [ ] Code comments and docstrings
- [ ] No emojis in any documentation

### Testing Evidence
- [ ] Screenshots or logs showing successful runs
- [ ] Test data in Airtable base
- [ ] Shortlisted Leads populated
- [ ] LLM fields populated

---

## Success Criteria

**The project is complete when**:
1. All 5 Airtable tables exist with correct schemas
2. 3 forms are functional and linked
3. Compression script successfully creates JSON from multi-table data
4. Decompression script restores JSON to normalized tables
5. Shortlist evaluator correctly identifies qualified candidates
6. LLM evaluator enriches applications with summaries and scores
7. All code follows best practices (no hardcoded secrets, error handling)
8. Documentation is comprehensive and clear
9. System can process real applicant data end-to-end

---

## Timeline Estimate

- **Airtable Setup**: 1-2 hours
  - Create 4 remaining tables (30 min)
  - Create 3 forms (30 min)
  - Get API credentials (15 min)
  - Test data entry (15 min)

- **Python Development**: 4-6 hours
  - Compression script (1 hour)
  - Decompression script (1 hour)
  - Shortlist evaluator (1.5 hours)
  - LLM evaluator (1.5 hours)
  - Testing and debugging (1-2 hours)

- **Documentation**: 1 hour
  - README.md
  - Code comments
  - Final review

**Total**: 6-9 hours

---

## Notes

- No emojis allowed per PRD requirements
- Keep code modular and maintainable
- Use environment variables for all secrets
- Implement proper error handling
- Test with real-world data scenarios
- Previous implementation is archived in archive_bin/ for reference (but rebuilding from scratch)
