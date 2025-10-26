# Mercor Mini-Interview Task: Submission Documentation

**Project:** Airtable Multi-Table Form + JSON Automation System
**Date:** 2025-10-25
**GitHub Repository:** https://github.com/tkhongsap/mercor-mini-task-tkhongsap

---

## Table of Contents

1. [Airtable Base Access](#airtable-base-access)
2. [Setup Instructions](#setup-instructions)
3. [Airtable Schema & Field Definitions](#airtable-schema--field-definitions)
4. [Automation Scripts](#automation-scripts)
5. [LLM Integration: Configuration & Security](#llm-integration-configuration--security)
6. [Customizing Shortlist Criteria](#customizing-shortlist-criteria)
7. [Testing & Verification](#testing--verification)
8. [Project Structure](#project-structure)

---

## Airtable Base Access

**Airtable Base:** https://airtable.com/app5go7iUaSsc0uKs

**GitHub Repository:** https://github.com/tkhongsap/mercor-mini-task-tkhongsap

All Python automation scripts (01-05.py), tests, and source code are available in the GitHub repository above.

### Base Contents

The base contains **5 linked tables** with **10 test applicants**:
- **6 applicants** meet shortlist criteria (shown in Shortlisted Leads table)
- **4 applicants** do not meet criteria (with detailed reasons)
- All applicants have LLM-generated summaries, scores (1-10), and follow-up questions

### Quick Overview

| Table | Record Count | Purpose |
|-------|--------------|---------|
| Applicants | 10 | Parent table with compressed JSON and LLM fields |
| Personal Details | 10 | One-to-one: Contact information |
| Work Experience | 26 | One-to-many: Employment history (1-3 jobs per applicant) |
| Salary Preferences | 10 | One-to-one: Rate and availability |
| Shortlisted Leads | 6 | Auto-populated: Qualified candidates only |

---

## Setup Instructions

### Prerequisites

- **Python:** 3.8 or higher
- **Airtable Account:** With Personal Access Token
- **OpenAI Account:** With API key for LLM evaluation

### Step 1: Install Dependencies

```bash
# Clone or extract the project
cd mercor-mini-task

# Install required Python packages
pip install -r requirements.txt
```

**Dependencies installed:**
- `pyairtable>=2.3.0` - Airtable API client
- `openai>=1.54.0` - OpenAI API for LLM evaluation
- `python-dotenv>=1.0.0` - Environment variable management
- `python-dateutil>=2.9.0` - Robust date parsing
- `pydantic>=2.12.0` - Data validation for LLM responses
- `pytest>=7.4.0` - Testing framework

### Step 2: Configure Credentials

```bash
# Copy environment template
cp env.template .env

# Edit .env file and add your credentials
```

**Required environment variables:**
```bash
AIRTABLE_PERSONAL_ACCESS_TOKEN=patXXXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXX
```

**How to obtain credentials:**

1. **Airtable Personal Access Token:**
   - Go to https://airtable.com/create/tokens
   - Click "Create new token"
   - Add scopes: `data.records:read`, `data.records:write`, `schema.bases:read`
   - Add access to your base
   - Copy the token (starts with `pat`)

2. **Airtable Base ID:**
   - Open your base in Airtable
   - Go to Help > API documentation
   - Base ID is shown at the top (starts with `app`)

3. **OpenAI API Key:**
   - Go to https://platform.openai.com/api-keys
   - Create new secret key
   - Copy the key (starts with `sk-`)

### Step 3: Run Automation Pipeline

Execute scripts in order (numbered sequentially):

```bash
# 1. Create all 5 tables in Airtable
python 01_setup_airtable_schema.py

# 2. Generate 10 test applicants with realistic data
python 02_generate_test_data.py

# 3. Compress data from 3 child tables into JSON
python 03_compress_data.py

# 4. Evaluate applicants and create shortlist
python 04_shortlist_evaluator.py

# 5. Enrich ALL applicants with LLM analysis
python 05_llm_evaluator.py
```

### Step 4: Verify Setup

```bash
# Run test suite (53 unit tests)
python tests/test_runner.py
```

Expected output:
```
✓ ALL TESTS PASSED - Schema is 100% PRD compliant!
Tests Run: 53
Successes: 53
Failures: 0
```

---

## Airtable Schema & Field Definitions

### Table 1: Applicants (Parent Table)

**Purpose:** Central table storing one record per applicant with compressed JSON and AI-generated fields.

| Field Name | Type | Description |
|------------|------|-------------|
| **Applicant ID** | Number | Python-managed sequence (1, 2, 3...). Used instead of autoNumber to enable full API automation. |
| **Compressed JSON** | Long text | JSON object combining data from Personal Details, Work Experience, and Salary Preferences tables. |
| **Shortlist Status** | Checkbox | Set to TRUE by shortlist evaluator if candidate meets all 3 criteria. |
| **LLM Summary** | Long text | AI-generated 75-word summary of candidate profile. |
| **LLM Score** | Number (integer) | AI-assigned quality score from 1-10 (higher is better). |
| **LLM Follow-Ups** | Long text | AI-suggested follow-up questions (up to 3). |
| **Personal Details** | Linked records | Auto-generated reverse link to Personal Details table. |
| **Work Experience** | Linked records | Auto-generated reverse link to Work Experience table. |
| **Salary Preferences** | Linked records | Auto-generated reverse link to Salary Preferences table. |
| **Shortlisted Leads** | Linked records | Auto-generated reverse link to Shortlisted Leads table. |

**Relationships:**
- One-to-one with Personal Details
- One-to-many with Work Experience (applicant can have multiple jobs)
- One-to-one with Salary Preferences
- One-to-many with Shortlisted Leads (for audit trail)

### Table 2: Personal Details

**Purpose:** Stores applicant contact information and location (one-to-one with Applicants).

| Field Name | Type | Description |
|------------|------|-------------|
| **Full Name** | Single line text | Applicant's full name (required). |
| **Email** | Email | Contact email address (validated format). |
| **Location** | Single line text | City, state/province, country. Used for location-based qualification. |
| **LinkedIn** | URL | LinkedIn profile URL (validated format). |
| **Applicant ID** | Link to Applicants | Links to parent Applicants record (one-to-one). |

### Table 3: Work Experience

**Purpose:** Stores employment history (one-to-many with Applicants - multiple jobs per applicant).

| Field Name | Type | Description |
|------------|------|-------------|
| **Company** | Single line text | Company or organization name. Checked against tier-1 company list. |
| **Title** | Single line text | Job title or role. |
| **Start** | Date | Employment start date (MM/DD/YYYY format). |
| **End** | Date | Employment end date. Can be empty for current employment (handled as "present" in calculations). |
| **Technologies** | Single line text | Comma-separated list of technologies, frameworks, or skills used. |
| **Applicant ID** | Link to Applicants | Links to parent Applicants record (one-to-many). |

### Table 4: Salary Preferences

**Purpose:** Stores compensation and availability preferences (one-to-one with Applicants).

| Field Name | Type | Description |
|------------|------|-------------|
| **Preferred Rate** | Number (decimal, 2 precision) | Desired hourly rate in specified currency. Used in qualification criteria (must be ≤$100/hr). |
| **Minimum Rate** | Number (decimal, 2 precision) | Minimum acceptable hourly rate. |
| **Currency** | Single select | Currency for rates. Options: USD, EUR, GBP, CAD, INR. |
| **Availability (hrs/wk)** | Number (integer) | Available hours per week. Used in qualification criteria (must be ≥20 hrs/wk). |
| **Applicant ID** | Link to Applicants | Links to parent Applicants record (one-to-one). |

### Table 5: Shortlisted Leads

**Purpose:** Auto-populated table containing only qualified candidates who meet all 3 shortlist criteria.

| Field Name | Type | Description |
|------------|------|-------------|
| **Applicant** | Link to Applicants | Links to parent Applicants record. |
| **Compressed JSON** | Long text | Copy of applicant's compressed JSON for easy export/review. |
| **Score Reason** | Long text | Human-readable explanation of why candidate qualified, showing how each criterion was met. |
| **Created At** | Date & time (UTC) | Timestamp when candidate was shortlisted. |

---

## Automation Scripts

### 01_setup_airtable_schema.py

**Purpose:** Creates all 5 tables via Airtable API with exact field specifications.

**How It Works:**

1. Loads credentials from `.env` file
2. Connects to Airtable using Personal Access Token
3. Checks if Applicants table exists (idempotent - can run multiple times safely)
4. Creates Applicants table with 6 core fields
5. Creates 4 child tables (Personal Details, Work Experience, Salary Preferences, Shortlisted Leads)
6. Airtable automatically creates reverse-link fields in Applicants table

**Key Design Decision:** Uses `number` field for Applicant ID instead of `autoNumber` because:
- Airtable API does not support creating autoNumber fields programmatically
- Python-managed sequence provides full automation without manual intervention
- Scripts query max existing ID and increment for new records

**Code Snippet - Creating Applicants Table:**

```python
# Create Applicants table with 6 fields
applicants_fields = [
    {
        "name": "Applicant ID",
        "type": "number",
        "options": {"precision": 0}  # Integer values only
    },
    {
        "name": "Compressed JSON",
        "type": "multilineText"
    },
    {
        "name": "Shortlist Status",
        "type": "checkbox",
        "options": {"icon": "check", "color": "greenBright"}
    },
    {
        "name": "LLM Summary",
        "type": "multilineText"
    },
    {
        "name": "LLM Score",
        "type": "number",
        "options": {"precision": 0}
    },
    {
        "name": "LLM Follow-Ups",
        "type": "multilineText"
    }
]

applicants_table = base.create_table(
    "Applicants",
    applicants_fields,
    description="Parent table storing applicant data and LLM evaluation results"
)
```

**Running:**
```bash
python 01_setup_airtable_schema.py
```

**Output:**
- Creates all 5 tables in ~10 seconds
- Displays table IDs and field counts
- Safe to run multiple times (checks for existing tables)

---

### 03_compress_data.py

**Purpose:** Reads data from 3 child tables and combines into single JSON object stored in Applicants.Compressed JSON field.

**How It Works:**

1. Reads Applicants table records
2. For each applicant:
   - Queries Personal Details (filters by Applicant ID link)
   - Queries all Work Experience records for this applicant
   - Queries Salary Preferences (filters by Applicant ID link)
3. Builds JSON structure per PRD specification
4. Writes JSON string to Compressed JSON field

**JSON Structure:**

```json
{
  "personal": {
    "name": "Sarah Chen",
    "email": "sarah.chen@example.com",
    "location": "San Francisco, CA, USA",
    "linkedin": "https://linkedin.com/in/sarahchen"
  },
  "experience": [
    {
      "company": "Google",
      "title": "Senior Software Engineer",
      "start": "2021-01-01",
      "end": "2024-01-01",
      "technologies": "Python, Kubernetes, gRPC, Distributed Systems"
    },
    {
      "company": "DoorDash",
      "title": "Software Engineer",
      "start": "2019-06-01",
      "end": "2020-12-31",
      "technologies": "React, Node.js, PostgreSQL, Microservices"
    }
  ],
  "salary": {
    "preferred_rate": 95.00,
    "minimum_rate": 80.00,
    "currency": "USD",
    "availability": 30
  }
}
```

**Code Snippet - Compression Logic:**

```python
# Build JSON structure per PRD specification
compressed_json = {
    "personal": {
        "name": personal_data.get("Full Name", ""),
        "email": personal_data.get("Email", ""),
        "location": personal_data.get("Location", ""),
        "linkedin": personal_data.get("LinkedIn", "")
    },
    "experience": [
        {
            "company": work['fields'].get("Company", ""),
            "title": work['fields'].get("Title", ""),
            "start": work['fields'].get("Start", ""),
            "end": work['fields'].get("End", ""),
            "technologies": work['fields'].get("Technologies", "")
        }
        for work in work_records
    ],
    "salary": {
        "preferred_rate": salary_data.get("Preferred Rate", 0),
        "minimum_rate": salary_data.get("Minimum Rate", 0),
        "currency": salary_data.get("Currency", "USD"),
        "availability": salary_data.get("Availability (hrs/wk)", 0)
    }
}

# Write to Applicants table
json_string = json.dumps(compressed_json, indent=2)
applicants_table.update(applicant_id, {
    "Compressed JSON": json_string
})
```

**Running:**
```bash
# Process all applicants
python 03_compress_data.py

# Process single applicant
python 03_compress_data.py --id recXXXXXXXXXXXXXX
```

---

### 04_shortlist_evaluator.py

**Purpose:** Evaluates applicants against 3 qualification criteria and creates Shortlisted Leads records for candidates who pass ALL criteria.

**Qualification Criteria (ALL must pass):**

#### Criterion 1: Experience
**Pass if:**
- Total years of experience ≥ 4 years **OR**
- Worked at a tier-1 company (Google, Meta, OpenAI, Microsoft, Amazon, Apple, Netflix, Tesla, SpaceX, Uber, Airbnb, Stripe)

**Calculation logic:**
- Parses all Work Experience records for applicant
- Handles "present", "current", "ongoing" for end dates (treats as current date)
- Validates dates (rejects future starts, end before start)
- Sums total days across all jobs
- Converts to years (accounting for leap years)

#### Criterion 2: Compensation
**Pass if:**
- Preferred Rate ≤ $100 USD/hour **AND**
- Availability ≥ 20 hours/week

**Both conditions must be true.**

#### Criterion 3: Location
**Pass if:**
- Location is in: United States, Canada, United Kingdom, Germany, or India

**Enhanced matching logic:**
- Supports country codes (US, CA, UK, GB, DE, IN)
- Recognizes major cities (NYC, San Francisco, Toronto, London, Berlin, Bangalore, etc.)
- Uses word boundary detection to prevent false positives
- Blacklists similar names (Australia, Austria, Indonesia, Indiana)

**Code Snippet - Evaluation Logic:**

```python
# Criterion 1: Experience
experience_list = applicant_data.get('experience', [])
years = calculate_years_of_experience(experience_list)
has_tier1, tier1_company = check_tier1_company(experience_list)

if years >= 4:
    reasons['experience']['passes'] = True
    reasons['experience']['reason'] = f"{years:.1f} years total experience (>=4 required)"
elif has_tier1:
    reasons['experience']['passes'] = True
    reasons['experience']['reason'] = f"Worked at {tier1_company} (tier-1 company)"
else:
    reasons['experience']['reason'] = f"Only {years:.1f} years and no tier-1 company"

# Criterion 2: Compensation
salary = applicant_data.get('salary', {})
preferred_rate = salary.get('preferred_rate', 999)
availability = salary.get('availability', 0)

if preferred_rate <= 100 and availability >= 20:
    reasons['compensation']['passes'] = True
    reasons['compensation']['reason'] = f"${preferred_rate}/hr (<=$100), {availability} hrs/wk (>=20)"
else:
    # Generate failure reason
    fail_parts = []
    if preferred_rate > 100:
        fail_parts.append(f"rate ${preferred_rate}/hr >$100")
    if availability < 20:
        fail_parts.append(f"availability {availability} hrs/wk <20")
    reasons['compensation']['reason'] = ', '.join(fail_parts)

# Criterion 3: Location
personal = applicant_data.get('personal', {})
location = personal.get('location', '')

if check_location(location):
    reasons['location']['passes'] = True
    reasons['location']['reason'] = f"{location} (approved region)"
else:
    reasons['location']['reason'] = f"{location} (not in approved regions)"

# Check if all criteria pass
all_pass = all([
    reasons['experience']['passes'],
    reasons['compensation']['passes'],
    reasons['location']['passes']
])
```

**If Candidate Qualifies:**
1. Sets `Shortlist Status` to TRUE in Applicants table
2. Creates record in Shortlisted Leads table
3. Copies Compressed JSON to Shortlisted Leads
4. Generates detailed Score Reason explaining qualification

**If Candidate Does NOT Qualify:**
1. Sets `Shortlist Status` to FALSE
2. Does NOT create Shortlisted Leads record

**Running:**
```bash
# Evaluate all applicants
python 04_shortlist_evaluator.py

# Evaluate single applicant
python 04_shortlist_evaluator.py --id recXXXXXXXXXXXXXX
```

**Example Output:**
```
[1/10] Sarah Chen (recXXXXXXXXXXXX):
  ✓ QUALIFIES
    - Experience: 4.6 years total experience (>=4 required)
    - Compensation: $95/hr (<=$100), 30 hrs/wk (>=20)
    - Location: San Francisco, CA, USA (approved region)

[2/10] Alex Rivera (recYYYYYYYYYYYY):
  ✗ Does NOT qualify
    - Compensation: rate $150/hr >$100
```

---

### 05_llm_evaluator.py

**Purpose:** Uses OpenAI API to evaluate ALL applicants (per PRD: trigger is "after Compressed JSON is written") and enrich their profiles with AI-generated insights.

**How It Works:**

1. Reads all Applicants records with Compressed JSON
2. For each applicant (unless already evaluated - caching):
   - Parses Compressed JSON
   - Sends to OpenAI with structured prompt
   - Uses Pydantic models for structured output parsing
   - Validates response format
3. Writes results to 3 LLM fields in Applicants table

**LLM Prompt Template:**

```python
instructions = """You are a recruiting analyst evaluating contractor applications.

Analyze the candidate's profile and provide:
1. A concise 75-word summary highlighting key strengths and fit
2. An overall quality score from 1-10 (higher is better)
3. Any data gaps or inconsistencies you notice
4. Up to 3 follow-up questions to clarify gaps or gather more info

Focus on technical skills, experience relevance, and professional background."""

input_text = f"""Evaluate this contractor application:

{json_data}

Provide your evaluation in the requested format."""
```

**Structured Output with Pydantic:**

```python
class LLMEvaluation(BaseModel):
    """Structured output model for LLM evaluation responses."""
    summary: str = Field(
        description="Concise 75-word summary of the candidate's profile"
    )
    score: int = Field(
        ge=1, le=10,
        description="Overall candidate quality score from 1-10 (higher is better)"
    )
    issues: str = Field(
        description="Comma-separated list of data gaps or inconsistencies, or 'None'"
    )
    follow_ups: str = Field(
        description="Bullet list of 1-3 follow-up questions to clarify gaps"
    )
```

**Error Handling & Retry Logic:**

```python
for attempt in range(max_retries):
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[...],
            response_format=LLM_JSON_RESPONSE_FORMAT,
            temperature=0.3,
            max_tokens=600
        )

        # Parse structured response
        parsed = LLMEvaluation(**json.loads(content_text))
        return parsed

    except RateLimitError as e:
        wait_time = (2 ** attempt) * 1  # Exponential backoff: 1s, 2s, 4s
        print(f"Rate limit hit. Waiting {wait_time}s before retry...")
        time.sleep(wait_time)

    except APIConnectionError as e:
        print(f"Connection error: {e}")
        # Retry with exponential backoff
```

**Caching to Prevent Duplicate Calls:**

```python
def should_skip_evaluation(applicant_fields: Dict[str, Any], force: bool = False) -> bool:
    """Check if applicant already has LLM evaluation (caching)."""
    if force:
        return False

    # Skip if all LLM fields are populated
    has_summary = bool(applicant_fields.get('LLM Summary'))
    has_score = applicant_fields.get('LLM Score') is not None
    has_followups = bool(applicant_fields.get('LLM Follow-Ups'))

    return has_summary and has_score and has_followups
```

**Running:**
```bash
# Evaluate all applicants (skips already-evaluated)
python 05_llm_evaluator.py

# Evaluate single applicant
python 05_llm_evaluator.py --id recXXXXXXXXXXXXXX

# Re-evaluate all (force)
python 05_llm_evaluator.py --force
```

**Example LLM Output:**

```
[1/10] Sarah Chen (recXXXXXXXXXXXX):
  ✓ Evaluation complete
    - Score: 9/10
    - Summary: 61 words
    - Issues: None
    - Follow-ups: 2 questions

LLM Summary:
"Senior software engineer with 5+ years at top-tier companies (Google, DoorDash).
Strong distributed systems expertise with Python and Kubernetes. Proven track record
in production environments. Excellent compensation fit ($95/hr). Based in San Francisco.
Available 30 hrs/week. Well-rounded technical profile with modern tech stack."

LLM Score: 9

LLM Follow-Ups:
- Can you provide examples of distributed systems projects you led at Google?
- What is your experience with team leadership or mentoring?
```

---

### decompress_data.py (Bonus Feature)

**Purpose:** Reads Compressed JSON and writes data back to normalized child tables. Enables bulk editing workflow: edit JSON → run decompression → sync changes to tables.

**How It Works:**

1. Reads Compressed JSON from Applicants table
2. For each applicant:
   - **Personal Details (one-to-one):** Upsert (update if exists, create if not)
   - **Work Experience (one-to-many):** Delete all existing records, then create new ones from JSON (ensures exact match)
   - **Salary Preferences (one-to-one):** Upsert

**Code Snippet - Upsert Strategy:**

```python
def decompress_personal_details(table, applicant_id, personal_data, dry_run=False):
    """Upsert Personal Details record (one-to-one relationship)."""
    fields = {
        "Full Name": personal_data.get("name", ""),
        "Email": personal_data.get("email", ""),
        "Location": personal_data.get("location", ""),
        "LinkedIn": personal_data.get("linkedin", ""),
        "Applicant ID": [applicant_id]
    }

    # Check if record exists
    existing_id = find_existing_record(table, applicant_id)

    if existing_id:
        # Update existing record
        table.update(existing_id, fields)
    else:
        # Create new record
        table.create(fields)
```

**Running:**
```bash
# Preview changes without applying (safe)
python decompress_data.py --dry-run

# Apply decompression to all applicants
python decompress_data.py

# Decompress single applicant
python decompress_data.py --id recXXXXXXXXXXXXXX
```

---

## LLM Integration: Configuration & Security

### Security Best Practices Implemented

#### 1. API Key Management

**NEVER hardcode credentials:**
```python
# ✓ CORRECT - Load from environment
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# ✗ WRONG - Never do this
openai_api_key = "sk-XXXXXXXXXXXXXXXX"  # NEVER!
```

**Environment variable protection:**
- All credentials stored in `.env` file
- `.env` file is in `.gitignore` (never committed to version control)
- `env.template` provided as example (no real credentials)

#### 2. API Key Validation

```python
if not openai_api_key:
    print("ERROR: Missing OPENAI_API_KEY in .env file")
    sys.exit(1)

# Verify key format
if not openai_api_key.startswith('sk-'):
    print("WARNING: OpenAI API key should start with 'sk-'")
```

#### 3. Token Budget Controls

**Rate Limiting:**
- Max 600 output tokens per call (prevents runaway costs)
- Exponential backoff on rate limit errors (1s, 2s, 4s)
- Max 3 retry attempts per request

**Caching to Prevent Duplicate Calls:**
```python
# Skip if already evaluated (unless --force flag)
if should_skip_evaluation(applicant_fields, args.force):
    print(f"  → Skipped (already evaluated, use --force to re-evaluate)")
    skip_count += 1
    continue
```

#### 4. Error Handling

**Comprehensive error handling for all failure modes:**

```python
try:
    response = client.chat.completions.create(...)
except RateLimitError as e:
    # Wait and retry with exponential backoff
    wait_time = (2 ** attempt) * 1
    time.sleep(wait_time)
except APIConnectionError as e:
    # Network error - retry with backoff
    print(f"Connection error: {e}")
except APIError as e:
    # API error - retry with backoff
    print(f"API error: {e}")
except Exception as e:
    # Unexpected error - log and continue to next applicant
    print(f"Unexpected error: {e}")
    continue  # Don't stop entire batch for one failure
```

**Benefits:**
- Individual failures don't stop entire batch
- Clear error messages for debugging
- Automatic retry with backoff for transient errors

### LLM Configuration

**Model Selection:**
```python
model = "gpt-4o-mini"  # Fast, cost-effective, high quality
```

**Parameters:**
```python
{
    "temperature": 0.3,     # Low temperature for consistent, focused output
    "max_tokens": 600,      # Cap output length (budget control)
    "response_format": {    # Structured JSON output
        "type": "json_schema",
        "json_schema": {...}
    }
}
```

**Why These Settings:**
- **Low temperature (0.3):** Reduces creativity, increases consistency in evaluation
- **Max tokens (600):** 75-word summary + score + issues + follow-ups fits comfortably
- **Structured output:** Ensures parseable responses, no regex parsing needed

### Monitoring & Debugging

**Detailed logging for all operations:**
```python
print(f"[{idx}/{len(applicants)}] {name} ({applicant_id}):")
print(f"    Calling OpenAI API (attempt {attempt + 1}/{max_retries})...")
print(f"    ✓ OpenAI API call successful")
print(f"  ✓ Evaluation complete")
print(f"    - Score: {evaluation.score}/10")
print(f"    - Summary: {len(evaluation.summary.split())} words")
```

**Summary report at end:**
```
Total applicants: 10
✓ Successfully evaluated: 6
→ Skipped (already evaluated): 4
✗ Errors: 0
```

---

## Customizing Shortlist Criteria

All shortlist criteria are defined in `04_shortlist_evaluator.py` as constants and functions. Here's how to customize each criterion:

### 1. Modify Experience Threshold

**Current requirement:** ≥ 4 years total experience

**How to change:**

Open `04_shortlist_evaluator.py` and find the experience evaluation logic (around line 204):

```python
# Change this line:
if years >= 4:  # Current: 4 years minimum
    reasons['experience']['passes'] = True

# To (for example, 5 years):
if years >= 5:
    reasons['experience']['passes'] = True
```

### 2. Add/Remove Tier-1 Companies

**Current tier-1 list:** Google, Meta, OpenAI, Microsoft, Amazon, Apple, Netflix, Tesla, SpaceX, Uber, Airbnb, Stripe

**How to change:**

Find the `TIER1_COMPANIES` constant at the top of `04_shortlist_evaluator.py` (around line 28):

```python
# Current list:
TIER1_COMPANIES = [
    'google', 'meta', 'openai', 'microsoft', 'amazon', 'apple',
    'netflix', 'tesla', 'spacex', 'uber', 'airbnb', 'stripe'
]

# Add companies:
TIER1_COMPANIES = [
    'google', 'meta', 'openai', 'microsoft', 'amazon', 'apple',
    'netflix', 'tesla', 'spacex', 'uber', 'airbnb', 'stripe',
    'stripe', 'databricks', 'anthropic', 'deepmind'  # Added
]

# Remove companies (example: remove Tesla, SpaceX):
TIER1_COMPANIES = [
    'google', 'meta', 'openai', 'microsoft', 'amazon', 'apple',
    'netflix', 'uber', 'airbnb', 'stripe'  # Removed tesla, spacex
]
```

**Note:** Company names are lowercase and checked with substring matching, so "google" matches "Google LLC", "Google Cloud", etc.

### 3. Adjust Compensation Limits

**Current requirements:**
- Preferred rate ≤ $100 USD/hour **AND**
- Availability ≥ 20 hours/week

**How to change:**

Find the compensation evaluation logic (around line 218):

```python
# Current limits:
if preferred_rate <= 100 and availability >= 20:
    reasons['compensation']['passes'] = True

# Example: Increase rate to $120/hr, reduce hours to 15/week:
if preferred_rate <= 120 and availability >= 15:
    reasons['compensation']['passes'] = True

# Example: Rate only (no hours requirement):
if preferred_rate <= 100:
    reasons['compensation']['passes'] = True
```

### 4. Update Approved Locations

**Current approved regions:** United States, Canada, United Kingdom, Germany, India

**How to change:**

Find the `APPROVED_LOCATIONS` set (around line 34):

```python
# Current approved locations:
APPROVED_LOCATIONS = {
    # United States
    'united states', 'usa', 'us ', ' us', 'america', 'american',
    'new york', 'nyc', 'san francisco', 'sf', 'los angeles', 'la',
    'seattle', 'wa', 'austin', 'tx', 'boston', 'ma', 'chicago', 'il',

    # Canada
    'canada', 'canadian', 'ca ',
    'toronto', 'on', 'vancouver', 'bc', 'montreal', 'qc',

    # United Kingdom
    'united kingdom', 'uk ', ' uk', 'britain', 'british', 'england',
    'london', 'manchester', 'birmingham', 'edinburgh',

    # Germany
    'germany', 'deutschland', 'german', 'de ',
    'berlin', 'munich', 'hamburg', 'frankfurt', 'cologne',

    # India
    'india', 'indian', 'in ',
    'bangalore', 'bengaluru', 'mumbai', 'delhi', 'hyderabad', 'chennai', 'pune'
}

# Add Australia:
APPROVED_LOCATIONS = {
    # (keep all existing)...

    # Australia (new)
    'australia', 'australian', 'au ',
    'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide'
}

# Update country codes (around line 59):
APPROVED_COUNTRY_CODES = {'us', 'usa', 'can', 'ca', 'uk', 'gb', 'de', 'deu', 'in', 'ind', 'au', 'aus'}
```

**Important:** If adding countries with names similar to existing locations, update the blacklist (line 155):

```python
# Current blacklist (prevents false positives):
blacklist = ['australia', 'austria', 'indonesia', 'indiana']

# If adding Australia to approved list, remove from blacklist:
blacklist = ['austria', 'indonesia', 'indiana']
```

### 5. Change Logic (AND vs OR)

**Current logic:** ALL 3 criteria must pass (AND logic)

**How to change to OR logic (any criterion passes):**

Find the final qualification check (around line 240):

```python
# Current (AND - all must pass):
all_pass = all([
    reasons['experience']['passes'],
    reasons['compensation']['passes'],
    reasons['location']['passes']
])

# Change to OR (any can pass):
any_pass = any([
    reasons['experience']['passes'],
    reasons['compensation']['passes'],
    reasons['location']['passes']
])
```

### 6. Add New Criteria

**Example:** Add minimum LLM score requirement

1. Add new criterion to evaluation function:

```python
def evaluate_applicant(applicant_data: Dict[str, Any], llm_score: Optional[int] = None) -> Tuple[bool, Dict]:
    reasons = {
        'experience': {'passes': False, 'reason': ''},
        'compensation': {'passes': False, 'reason': ''},
        'location': {'passes': False, 'reason': ''},
        'llm_score': {'passes': False, 'reason': ''}  # New criterion
    }

    # (existing criteria code)...

    # Criterion 4: LLM Score
    if llm_score and llm_score >= 7:
        reasons['llm_score']['passes'] = True
        reasons['llm_score']['reason'] = f"LLM score {llm_score}/10 (>=7 required)"
    else:
        reasons['llm_score']['reason'] = f"LLM score {llm_score or 'N/A'}/10 (<7)"

    # Check if all criteria pass (including new one)
    all_pass = all([
        reasons['experience']['passes'],
        reasons['compensation']['passes'],
        reasons['location']['passes'],
        reasons['llm_score']['passes']  # Add to check
    ])

    return all_pass, reasons
```

2. Update main evaluation loop to pass LLM score:

```python
for applicant in applicants:
    llm_score = applicant['fields'].get('LLM Score')
    qualifies, reasons = evaluate_applicant(applicant_data, llm_score)
```

### Testing Customizations

After modifying criteria:

1. **Test with existing data:**
```bash
python 04_shortlist_evaluator.py
```

2. **Review output:**
Check that the correct number of candidates qualify and that reasons are displayed correctly.

3. **Adjust test data if needed:**
Modify `02_generate_test_data.py` to create applicants that test your new criteria edge cases.

---

## Testing & Verification

### Automated Test Suite

The project includes **53 unit tests** covering all aspects of the schema:

```bash
# Run all tests
python tests/test_runner.py

# Run with verbose output
python tests/test_runner.py --verbose

# Run specific test file
python -m unittest tests.test_schema_setup

# Run specific test class
python -m unittest tests.test_schema_setup.TestApplicantsTable
```

**Expected output (after fixing Table-01 deletion):**
```
======================================================================
Airtable Schema Setup - Unit Test Suite
======================================================================

.....................................................
----------------------------------------------------------------------
Ran 53 tests in 12.456s

OK

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

### Test Coverage

**TestAirtableSchemaSetup (4 tests):**
- Environment variables loaded correctly
- Airtable connection successful
- All 5 required tables exist
- No extra tables (exactly 5)

**TestApplicantsTable (8 tests):**
- Table exists
- 6 required fields present
- Field types correct (number for Applicant ID, multilineText, checkbox, number)
- 4 linked record fields to child tables

**TestPersonalDetailsTable (7 tests):**
- 5 required fields present
- Field types correct (singleLineText, email, url)
- Linked to Applicants table
- Email field has proper validation
- URL field has proper validation

**TestWorkExperienceTable (8 tests):**
- 6 required fields present
- Field types correct (date fields with US format)
- Linked to Applicants table
- Date format validation (M/D/YYYY)

**TestSalaryPreferencesTable (9 tests):**
- 5 required fields present
- Field types correct (number with decimal precision)
- Currency single-select with 5 options (USD, EUR, GBP, CAD, INR)
- Number precision validation

**TestShortlistedLeadsTable (8 tests):**
- 4 required fields present
- DateTime field with UTC timezone
- Linked to Applicants table
- Timestamp validation

**TestPRDCompliance (9 tests):**
- Exactly 5 tables per PRD
- All required tables present
- Applicants table compliance
- Child tables compliance
- Linked relationships working bidirectionally

### Manual Verification in Airtable

1. **Open base:** https://airtable.com/app5go7iUaSsc0uKs

2. **Check Applicants table:**
   - 10 records with sequential IDs (1-10)
   - Compressed JSON populated for all records
   - 6 records have Shortlist Status = TRUE
   - LLM Summary, LLM Score, LLM Follow-Ups populated

3. **Check Shortlisted Leads table:**
   - 6 records (matching shortlisted applicants)
   - Each has Score Reason explaining qualification
   - Created At timestamps present

4. **Verify linked relationships:**
   - Click any Applicants record
   - Expand Personal Details link → should show 1 record
   - Expand Work Experience link → should show 1-3 records
   - Expand Salary Preferences link → should show 1 record
   - Expand Shortlisted Leads link → should show 0-1 record

5. **Check data quality:**
   - No duplicate records
   - All required fields populated
   - No orphaned records (child records without parent link)

### PRD Compliance Verification

Run the PRD compliance checker:

```bash
python tests/verify_prd_schema.py
```

**Expected output:**
```
======================================================================
Airtable Schema - PRD Compliance Verification
======================================================================

Table Count
-----------
✓ Found exactly 5 tables (required by PRD)

Table Names
-----------
✓ Applicants
✓ Personal Details
✓ Work Experience
✓ Salary Preferences
✓ Shortlisted Leads

Applicants Table
----------------
✓ 6 core fields present
✓ 4 linked record fields (reverse links from child tables)
✓ Field types match PRD specifications

Personal Details Table
---------------------
✓ 5 fields present
✓ Email field type: email
✓ LinkedIn field type: url
✓ Linked to Applicants

Work Experience Table
--------------------
✓ 6 fields present
✓ Date fields with correct format
✓ Linked to Applicants

Salary Preferences Table
-----------------------
✓ 5 fields present
✓ Number fields with decimal precision
✓ Currency single-select with 5 options
✓ Linked to Applicants

Shortlisted Leads Table
-----------------------
✓ 4 fields present
✓ DateTime field with UTC timezone
✓ Linked to Applicants

======================================================================
RESULT: 100% PRD COMPLIANT
======================================================================
```

---

## Project Structure

```
mercor-mini-task/
│
├── README.md                          # Quick start guide
├── SUBMISSION.md                      # This document (comprehensive deliverables)
├── prd.md                             # Original project requirements
├── DESIGN_DECISIONS.md                # Architectural choices explained
│
├── 01_setup_airtable_schema.py        # Script 1: Create tables via API
├── 02_generate_test_data.py           # Script 2: Generate 10 test applicants
├── 03_compress_data.py                # Script 3: Multi-table → JSON
├── 04_shortlist_evaluator.py          # Script 4: Evaluate & shortlist
├── 05_llm_evaluator.py                # Script 5: LLM enrichment
│
├── decompress_data.py                 # Bonus: JSON → tables (bulk editing)
├── cleanup_test_data.py               # Utility: Clean test data
├── logger.py                          # Shared: Logging utility
│
├── requirements.txt                   # Python dependencies
├── env.template                       # Environment variable template
├── .env                               # Credentials (gitignored, you create this)
├── .gitignore                         # Git ignore rules
│
└── tests/                             # Test suite (53 tests, 838 LOC)
    ├── test_schema_setup.py           # 53 unit tests validating schema
    ├── test_runner.py                 # Test runner with summary reporting
    └── verify_prd_schema.py           # PRD compliance verification script
```

### Execution Order

**Initial setup (one time):**
```bash
1. pip install -r requirements.txt
2. cp env.template .env
3. Edit .env with your credentials
```

**Full pipeline (run in order):**
```bash
python 01_setup_airtable_schema.py   # ~10 seconds
python 02_generate_test_data.py      # ~30 seconds (creates 10 applicants)
python 03_compress_data.py           # ~5 seconds (10 JSON objects)
python 04_shortlist_evaluator.py     # ~10 seconds (6 shortlisted)
python 05_llm_evaluator.py           # ~2-3 minutes (10 LLM calls)
```

**Verification:**
```bash
python tests/test_runner.py          # ~15 seconds (53 tests)
```

### Dependencies

**Production dependencies (requirements.txt):**
```
pyairtable>=2.3.0       # Airtable API client
openai>=1.54.0          # OpenAI API for LLM evaluation
python-dotenv>=1.0.0    # Environment variable management
python-dateutil>=2.9.0  # Robust date parsing
pydantic>=2.12.0        # Data validation for LLM responses
pytest>=7.4.0           # Testing framework
mypy>=1.8.0             # Type checking (optional)
```

**Install all:**
```bash
pip install -r requirements.txt
```

---

## Summary

This project delivers a complete, production-ready contractor application system with:

**Core Features:**
- 5-table Airtable schema with bidirectional relationships
- Automated schema setup via Python API
- JSON compression/decompression for data portability
- Multi-factor shortlist evaluation (experience, compensation, location)
- LLM-powered application enrichment with structured outputs

**Engineering Excellence:**
- Full type hints throughout codebase
- Comprehensive test suite (53 unit tests)
- PRD compliance verification
- Security best practices (no hardcoded credentials)
- Error handling with retry logic
- Detailed documentation

**Extensibility:**
- Easy to customize shortlist criteria (constants and clear functions)
- Modular script design (single responsibility)
- Test data generator for different scenarios
- Cleanup utilities for development iteration

**Total Lines of Code:** ~2,500 lines of production Python code + tests

For questions or issues, refer to:
- `README.md` for quick start
- `DESIGN_DECISIONS.md` for architectural rationale
- `prd.md` for original requirements
- Test suite (`tests/`) for validation

**Airtable Base:** https://airtable.com/app5go7iUaSsc0uKs
