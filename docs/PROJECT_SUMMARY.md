# Project Summary - Airtable Contractor Application System

## What We're Building

A complete automated contractor application system that:
1. Collects applicant data through Airtable forms
2. Compresses multi-table data into portable JSON format
3. Decompresses JSON back to normalized tables for editing
4. Auto-evaluates candidates against multi-factor criteria
5. Uses AI to enrich applications with summaries and insights

---

## Current Progress

### Completed ✅
- [x] Created feature branch: `feature/airtable-setup-implementation`
- [x] Archived previous implementation to `archive_bin/`
- [x] Created clean workspace
- [x] Created DELIVERABLES.md checklist
- [x] Created PROJECT_SUMMARY.md (this file)
- [x] **Airtable**: Created "Contractor Application" base
- [x] **Airtable**: Created Applicants table with 6 fields

### In Progress ⏳
- [ ] **Airtable**: Create remaining 4 tables (Personal Details, Work Experience, Salary Preferences, Shortlisted Leads)
- [ ] **Airtable**: Create 3 data collection forms

### Pending ⏰
- [ ] **API Setup**: Get Airtable Personal Access Token
- [ ] **API Setup**: Get Airtable Base ID
- [ ] **API Setup**: Get OpenAI/Anthropic API key
- [ ] **Python**: Build compression script
- [ ] **Python**: Build decompression script
- [ ] **Python**: Build shortlist evaluator
- [ ] **Python**: Build LLM evaluator
- [ ] **Testing**: End-to-end system testing
- [ ] **Docs**: Create README.md with usage instructions

---

## System Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
│  (3 Airtable Forms: Personal, Work Experience, Salary)          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AIRTABLE DATABASE                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Personal    │  │    Work      │  │   Salary     │          │
│  │  Details     │  │  Experience  │  │ Preferences  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                   │
│         └─────────────────┴──────────────────┘                   │
│                           │                                      │
│                    Links to Applicants                           │
│                           │                                      │
│                           ▼                                      │
│              ┌────────────────────────┐                          │
│              │   Applicants Table     │                          │
│              │  - Applicant ID        │                          │
│              │  - Compressed JSON     │◄─────┐                   │
│              │  - Shortlist Status    │      │                   │
│              │  - LLM Summary         │      │                   │
│              │  - LLM Score           │      │                   │
│              │  - LLM Follow-Ups      │      │                   │
│              └────────────────────────┘      │                   │
└──────────────────────────────────────────────┼───────────────────┘
                                               │
                    ┌──────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────────────┐
    │      PYTHON COMPRESSION SCRIPT                 │
    │  compress_data.py                             │
    │  - Reads 3 child tables                       │
    │  - Builds unified JSON                        │
    │  - Writes to Compressed JSON field            │
    └───────────────────┬───────────────────────────┘
                        │
                        ▼
    ┌───────────────────────────────────────────────┐
    │      EVALUATION PIPELINE                       │
    │                                                │
    │  ┌─────────────────────────────────────────┐  │
    │  │  Shortlist Evaluator                    │  │
    │  │  - Check Experience (4+ yrs OR tier-1)  │  │
    │  │  - Check Compensation (≤$100, ≥20hrs)   │  │
    │  │  - Check Location (5 countries)         │  │
    │  │  - Create Shortlisted Leads if pass     │  │
    │  └─────────────────────────────────────────┘  │
    │                                                │
    │  ┌─────────────────────────────────────────┐  │
    │  │  LLM Evaluator                          │  │
    │  │  - Send JSON to OpenAI/Anthropic        │  │
    │  │  - Generate 75-word summary             │  │
    │  │  - Assign quality score (1-10)          │  │
    │  │  - Suggest follow-up questions          │  │
    │  │  - Write to LLM fields                  │  │
    │  └─────────────────────────────────────────┘  │
    └───────────────────────────────────────────────┘
                        │
                        ▼
    ┌───────────────────────────────────────────────┐
    │      PYTHON DECOMPRESSION SCRIPT               │
    │  decompress_data.py (Optional)                │
    │  - Reads Compressed JSON                      │
    │  - Upserts data back to child tables          │
    │  - Used for bulk editing via JSON             │
    └───────────────────────────────────────────────┘
```

---

## Airtable Schema Design

### Tables and Relationships

```
Applicants (Parent)
├─► Personal Details (1:1)
├─► Work Experience (1:N)
├─► Salary Preferences (1:1)
└─► Shortlisted Leads (1:N) [auto-populated]
```

### Detailed Table Schemas

#### 1. Applicants Table ✅ COMPLETED
| Field Name | Type | Notes |
|------------|------|-------|
| Applicant ID | Number (Auto) | Primary field, auto-increments |
| Compressed JSON | Long text | Plain text only, stores unified JSON |
| Shortlist Status | Checkbox | Set by shortlist evaluator |
| LLM Summary | Long text | 75-word summary from LLM |
| LLM Score | Number (Integer) | 1-10 quality score |
| LLM Follow-Ups | Long text | Follow-up questions from LLM |
| Personal Details | Link | Auto-created from Personal Details table |
| Work Experience | Link | Auto-created from Work Experience table |
| Salary Preferences | Link | Auto-created from Salary Preferences table |
| Shortlisted | Link | Auto-created from Shortlisted Leads table |

#### 2. Personal Details Table ⏳ PENDING
| Field Name | Type | Notes |
|------------|------|-------|
| Record ID | Auto | Primary field |
| Full Name | Single line text | Required |
| Email | Email | Required |
| Location | Single line text | Required for location criterion |
| LinkedIn | URL | Optional |
| Applicant ID | Link to Applicants | Creates reverse link |

#### 3. Work Experience Table ⏳ PENDING
| Field Name | Type | Notes |
|------------|------|-------|
| Record ID | Auto | Primary field |
| Company | Single line text | Used for tier-1 company check |
| Title | Single line text | Job title |
| Start | Date | Start date of position |
| End | Date | End date (empty if current) |
| Technologies | Single line text | Comma-separated list |
| Applicant ID | Link to Applicants | Creates reverse link, one-to-many |

**Relationship**: One applicant can have multiple work experiences

#### 4. Salary Preferences Table ⏳ PENDING
| Field Name | Type | Notes |
|------------|------|-------|
| Record ID | Auto | Primary field |
| Preferred Rate | Number (Decimal) | Hourly rate preference |
| Minimum Rate | Number (Decimal) | Minimum acceptable rate |
| Currency | Single select | USD, EUR, GBP, CAD, INR |
| Availability (hrs/wk) | Number (Integer) | Hours per week available |
| Applicant ID | Link to Applicants | Creates reverse link |

#### 5. Shortlisted Leads Table ⏳ PENDING
| Field Name | Type | Notes |
|------------|------|-------|
| Record ID | Auto | Primary field |
| Applicant | Link to Applicants | Which applicant qualified |
| Compressed JSON | Long text | Copy of applicant's JSON |
| Score Reason | Long text | Why they were shortlisted |
| Created At | Created time | Auto-timestamp |

**Populated By**: Shortlist evaluator script (automatic)

---

## Python Scripts to Build

### 1. compress_data.py
**Purpose**: Gather multi-table data and create unified JSON

**Input**: Applicant ID(s)

**Process**:
1. Query Personal Details table for applicant
2. Query Work Experience table for all applicant records
3. Query Salary Preferences table for applicant
4. Build JSON structure:
   ```json
   {
     "personal": {...},
     "experience": [{...}, {...}],
     "salary": {...}
   }
   ```
5. Write to Applicants.Compressed JSON field

**Usage**:
```bash
python compress_data.py --applicant-id 1
python compress_data.py --all  # Process all applicants
```

---

### 2. decompress_data.py
**Purpose**: Restore JSON data to normalized tables

**Input**: Applicant ID

**Process**:
1. Read Applicants.Compressed JSON field
2. Parse JSON
3. Upsert Personal Details (update if exists, create if not)
4. Delete existing Work Experience records for applicant
5. Create new Work Experience records from JSON array
6. Upsert Salary Preferences
7. Maintain Applicant ID links throughout

**Usage**:
```bash
python decompress_data.py --applicant-id 1
```

---

### 3. shortlist_evaluator.py
**Purpose**: Evaluate candidates against criteria and auto-shortlist

**Input**: Applicant ID(s)

**Evaluation Logic**:
```python
# Criterion 1: Experience
experience_years = calculate_total_years(work_experience_records)
has_tier1 = any(company in TIER1_COMPANIES for company in companies)
experience_pass = experience_years >= 4 or has_tier1

# Criterion 2: Compensation
rate_pass = preferred_rate <= 100 and currency == 'USD'
availability_pass = availability >= 20
compensation_pass = rate_pass and availability_pass

# Criterion 3: Location
location_pass = location_country in ['US', 'Canada', 'UK', 'Germany', 'India']

# Overall
qualifies = experience_pass and compensation_pass and location_pass
```

**If Qualified**:
1. Set Shortlist Status checkbox
2. Create Shortlisted Leads record
3. Generate detailed Score Reason

**Usage**:
```bash
python shortlist_evaluator.py --applicant-id 1
python shortlist_evaluator.py --all
```

---

### 4. llm_evaluator.py
**Purpose**: Use LLM to enrich applications

**Input**: Applicant ID(s)

**Process**:
1. Read Compressed JSON
2. Check if JSON changed (caching)
3. Build LLM prompt with JSON
4. Call OpenAI/Anthropic API
5. Parse response:
   - Extract summary (≤75 words)
   - Extract score (1-10)
   - Extract issues
   - Extract follow-up questions
6. Write to LLM fields in Applicants table

**Error Handling**:
- Retry up to 3 times with exponential backoff
- Log errors but continue processing
- Skip if API fails after retries

**Usage**:
```bash
python llm_evaluator.py --applicant-id 1
python llm_evaluator.py --all
```

---

### 5. airtable_client.py (Helper Module)
**Purpose**: Reusable Airtable API wrapper

**Functionality**:
- Connect to Airtable base
- CRUD operations (Create, Read, Update, Delete)
- Query records with filters
- Handle linked records
- Error handling and retries

**Example**:
```python
from airtable_client import AirtableClient

client = AirtableClient()
applicant = client.get_record('Applicants', applicant_id)
experiences = client.get_linked_records('Work Experience', applicant_id)
```

---

### 6. config.py (Configuration Module)
**Purpose**: Centralized configuration management

**Functionality**:
- Load environment variables from .env
- Validate required variables exist
- Provide configuration to other scripts

**Example**:
```python
from config import Config

config = Config()
base_id = config.AIRTABLE_BASE_ID
api_key = config.AIRTABLE_PAT
```

---

## Technology Stack

### Airtable
- **Purpose**: Data storage, forms, UI
- **Features Used**: Tables, linked records, forms, field types
- **API**: REST API via pyairtable

### Python 3.8+
- **Purpose**: Automation scripts
- **Libraries**:
  - `pyairtable` - Airtable API client
  - `openai` or `anthropic` - LLM integration
  - `python-dotenv` - Environment variable management
  - `json` - JSON parsing (built-in)
  - `datetime` - Date calculations (built-in)

### LLM Provider
- **Options**: OpenAI GPT-4, Anthropic Claude, Google Gemini
- **Recommended**: OpenAI (easiest to set up)
- **Model**: GPT-4-mini or Claude 3 Haiku (cost-effective)

---

## File Structure Plan

```
mercor-mini-task/
│
├── Core Scripts
│   ├── compress_data.py          # JSON compression
│   ├── decompress_data.py        # JSON decompression
│   ├── shortlist_evaluator.py   # Candidate evaluation
│   └── llm_evaluator.py          # LLM integration
│
├── Helper Modules
│   ├── airtable_client.py        # Airtable API wrapper
│   └── config.py                 # Configuration management
│
├── Configuration
│   ├── .env                      # API credentials (gitignored)
│   ├── env.template              # Template for .env
│   └── requirements.txt          # Python dependencies
│
├── Documentation
│   ├── prd.md                    # Original requirements
│   ├── DELIVERABLES.md           # Detailed checklist
│   ├── PROJECT_SUMMARY.md        # This file
│   └── README.md                 # Usage guide (to be created)
│
└── Archive
    └── archive_bin/              # Previous implementation (reference only)
```

---

## Implementation Roadmap

### Phase 1: Airtable Setup (Current)
**Timeline**: 1-2 hours

**Tasks**:
- [x] Create Applicants table (6 fields)
- [ ] Create Personal Details table
- [ ] Create Work Experience table
- [ ] Create Salary Preferences table
- [ ] Create Shortlisted Leads table
- [ ] Verify all linked relationships
- [ ] Create 3 data collection forms
- [ ] Test forms with sample data

---

### Phase 2: API Credentials
**Timeline**: 15-30 minutes

**Tasks**:
- [ ] Get Airtable Personal Access Token
  - Account → Developer → Personal access tokens
  - Scopes: data.records:read, data.records:write
- [ ] Get Airtable Base ID
  - From Airtable API docs or base URL
- [ ] Get LLM API key
  - OpenAI: platform.openai.com/api-keys
  - Or Anthropic: console.anthropic.com
- [ ] Create .env file from template
- [ ] Add all credentials to .env

---

### Phase 3: Python Development
**Timeline**: 4-6 hours

**Iteration 1: Foundation (1 hour)**
- [ ] Set up Python environment
- [ ] Install dependencies (requirements.txt)
- [ ] Create config.py
- [ ] Create airtable_client.py
- [ ] Test Airtable connection

**Iteration 2: Compression & Decompression (2 hours)**
- [ ] Build compress_data.py
- [ ] Test with sample applicant
- [ ] Build decompress_data.py
- [ ] Test round-trip (compress → decompress)

**Iteration 3: Evaluation (2-3 hours)**
- [ ] Build shortlist_evaluator.py
- [ ] Test shortlist criteria
- [ ] Build llm_evaluator.py
- [ ] Test LLM integration
- [ ] End-to-end testing

---

### Phase 4: Testing & Documentation
**Timeline**: 1-2 hours

**Tasks**:
- [ ] Create test applicants (5 scenarios)
- [ ] Run full pipeline
- [ ] Verify results in Airtable
- [ ] Write README.md
- [ ] Add code comments
- [ ] Final review

---

### Phase 5: Submission
**Timeline**: 30 minutes

**Tasks**:
- [ ] Create Airtable share link
- [ ] Verify .env not in git
- [ ] Push code to GitHub
- [ ] Create submission package
- [ ] Submit deliverables

---

## Key Design Principles

### 1. Modularity
Each script has a single responsibility:
- Compression handles only JSON creation
- Decompression handles only JSON restoration
- Shortlist handles only evaluation
- LLM handles only enrichment

### 2. Security
- No hardcoded credentials
- All secrets in .env file
- .env in .gitignore
- env.template provided as example

### 3. Error Handling
- Try-except blocks for API calls
- Retry logic for LLM (3 attempts)
- Graceful degradation
- Detailed error logging

### 4. Maintainability
- Clear variable names
- Docstrings for functions
- Comments for complex logic
- Consistent code style

### 5. Extensibility
- Easy to add new evaluation criteria
- Easy to switch LLM providers
- Easy to add new fields
- Configuration-driven behavior

---

## Success Metrics

**The project is successful when**:
1. Applicants can submit data via 3 forms
2. Data flows correctly through all tables
3. Compression creates valid JSON
4. Decompression restores data accurately
5. Shortlist correctly identifies qualified candidates
6. LLM generates meaningful insights
7. System runs end-to-end without errors
8. Code is clean, documented, and maintainable

---

## Risk Mitigation

### Risk: API Rate Limits
**Mitigation**: Process applicants sequentially, add delays if needed

### Risk: LLM API Failures
**Mitigation**: Retry logic with exponential backoff, continue processing even if LLM fails

### Risk: Data Integrity Issues
**Mitigation**: Validate data before writing, use transactions where possible

### Risk: Incomplete Applicant Data
**Mitigation**: Handle None values gracefully, provide defaults where appropriate

---

## Next Steps

1. **Immediate**: Complete Airtable table setup
   - Create Personal Details table
   - Create Work Experience table
   - Create Salary Preferences table
   - Create Shortlisted Leads table

2. **Short-term**: Set up forms and get credentials
   - Create 3 Airtable forms
   - Get API credentials
   - Configure .env file

3. **Medium-term**: Build Python scripts
   - Start with airtable_client.py and config.py
   - Then compression and decompression
   - Finally evaluation scripts

4. **Final**: Test, document, submit
   - End-to-end testing
   - Write README.md
   - Create submission package

---

## Resources

- **Airtable API Docs**: https://airtable.com/developers/web/api/introduction
- **pyairtable Docs**: https://pyairtable.readthedocs.io/
- **OpenAI API Docs**: https://platform.openai.com/docs/
- **Anthropic API Docs**: https://docs.anthropic.com/

---

**Last Updated**: 2025-10-25
**Status**: Airtable Applicants table completed, ready to create child tables
**Next Milestone**: Complete all 5 Airtable tables and forms
