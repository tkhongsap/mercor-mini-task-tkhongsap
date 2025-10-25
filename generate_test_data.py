#!/usr/bin/env python3
"""
Test Data Generator for Airtable Contractor Application System

This script generates 10 comprehensive test applicants with realistic data
to test all automation scripts (compression, decompression, shortlist, LLM).

Test Coverage:
- 6 applicants that qualify for shortlist (different qualification reasons)
- 4 applicants that don't qualify (different failure reasons)
- Edge cases: exactly $100/hr, exactly 4 years experience
- Diverse locations, company mix, experience levels
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from pyairtable import Api

def main():
    print("=" * 70)
    print("Test Data Generator - Contractor Application System")
    print("=" * 70)
    print()

    # Load environment variables
    print("Loading credentials from .env file...")
    load_dotenv()

    pat = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID')

    if not pat or not base_id:
        print("ERROR: Missing credentials in .env file")
        print("Required: AIRTABLE_PERSONAL_ACCESS_TOKEN and AIRTABLE_BASE_ID")
        sys.exit(1)

    print(f"✓ Credentials loaded")
    print(f"  Base ID: {base_id}")
    print()

    # Connect to Airtable
    print("Connecting to Airtable...")
    try:
        api = Api(pat)
        base = api.base(base_id)

        # Get table references
        applicants_table = base.table("Applicants")
        personal_details_table = base.table("Personal Details")
        work_experience_table = base.table("Work Experience")
        salary_preferences_table = base.table("Salary Preferences")

        print(f"✓ Connected to base")
        print()
    except Exception as e:
        print(f"ERROR: Failed to connect to Airtable: {e}")
        sys.exit(1)

    # Define 10 test applicants
    test_applicants = [
        {
            "name": "Sarah Chen",
            "email": "sarah.chen@example.com",
            "location": "San Francisco, CA, USA",
            "linkedin": "https://linkedin.com/in/sarahchen",
            "work_history": [
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
            "preferred_rate": 95.00,
            "minimum_rate": 80.00,
            "currency": "USD",
            "availability": 30,
            "should_qualify": True,
            "qualification_reason": "Tier-1 company (Google)"
        },
        {
            "name": "Marcus Johnson",
            "email": "marcus.j@example.com",
            "location": "Toronto, Canada",
            "linkedin": "https://linkedin.com/in/marcusjohnson",
            "work_history": [
                {
                    "company": "Coinbase",
                    "title": "Backend Engineer",
                    "start": "2019-03-01",
                    "end": "2024-10-25",
                    "technologies": "Go, Redis, Kafka, Blockchain"
                },
                {
                    "company": "Instacart",
                    "title": "Full-Stack Developer",
                    "start": "2017-01-01",
                    "end": "2019-02-28",
                    "technologies": "Ruby on Rails, React, GraphQL"
                },
                {
                    "company": "Dropbox",
                    "title": "Junior Engineer",
                    "start": "2015-06-01",
                    "end": "2016-12-31",
                    "technologies": "Python, Distributed Systems, Storage"
                }
            ],
            "preferred_rate": 88.00,
            "minimum_rate": 75.00,
            "currency": "USD",
            "availability": 25,
            "should_qualify": True,
            "qualification_reason": "8 years total experience"
        },
        {
            "name": "Priya Sharma",
            "email": "priya.sharma@example.com",
            "location": "Berlin, Germany",
            "linkedin": "https://linkedin.com/in/priyasharma",
            "work_history": [
                {
                    "company": "Meta",
                    "title": "Engineering Manager",
                    "start": "2020-01-01",
                    "end": "2024-10-25",
                    "technologies": "Rust, GraphQL, ML Infrastructure, Team Leadership"
                },
                {
                    "company": "Microsoft",
                    "title": "Senior Engineer",
                    "start": "2017-06-01",
                    "end": "2019-12-31",
                    "technologies": "C#, Azure, Microservices, DevOps"
                }
            ],
            "preferred_rate": 100.00,
            "minimum_rate": 85.00,
            "currency": "USD",
            "availability": 40,
            "should_qualify": True,
            "qualification_reason": "Tier-1 + 7 years + exactly $100/hr (edge case)"
        },
        {
            "name": "Alex Rivera",
            "email": "alex.rivera@example.com",
            "location": "Austin, TX, USA",
            "linkedin": "https://linkedin.com/in/alexrivera",
            "work_history": [
                {
                    "company": "Rigetti Computing",
                    "title": "Lead Developer",
                    "start": "2022-01-01",
                    "end": "2024-10-25",
                    "technologies": "Quantum Computing, Python, Research"
                },
                {
                    "company": "GitLab",
                    "title": "Senior DevOps Engineer",
                    "start": "2020-03-01",
                    "end": "2021-12-31",
                    "technologies": "Kubernetes, CI/CD, Terraform, GitOps"
                }
            ],
            "preferred_rate": 150.00,
            "minimum_rate": 120.00,
            "currency": "USD",
            "availability": 20,
            "should_qualify": False,
            "qualification_reason": "Rate >$100/hr"
        },
        {
            "name": "Chen Wei",
            "email": "chen.wei@example.com",
            "location": "London, UK",
            "linkedin": "https://linkedin.com/in/chenwei",
            "work_history": [
                {
                    "company": "Amazon",
                    "title": "Software Development Engineer",
                    "start": "2022-06-01",
                    "end": "2024-10-25",
                    "technologies": "Java, AWS, DynamoDB, Lambda"
                },
                {
                    "company": "Oklo",
                    "title": "Backend Developer",
                    "start": "2021-01-01",
                    "end": "2022-05-31",
                    "technologies": "Python, Energy Systems, IoT"
                }
            ],
            "preferred_rate": 92.00,
            "minimum_rate": 78.00,
            "currency": "USD",
            "availability": 35,
            "should_qualify": True,
            "qualification_reason": "Tier-1 company (Amazon)"
        },
        {
            "name": "Lisa Anderson",
            "email": "lisa.anderson@example.com",
            "location": "Mumbai, India",
            "linkedin": "https://linkedin.com/in/lisaanderson",
            "work_history": [
                {
                    "company": "Tech Startup A",
                    "title": "Full-Stack Engineer",
                    "start": "2020-01-01",
                    "end": "2024-10-25",
                    "technologies": "MERN Stack, Docker, AWS"
                },
                {
                    "company": "Software Company B",
                    "title": "Junior Developer",
                    "start": "2019-06-01",
                    "end": "2019-12-31",
                    "technologies": "JavaScript, React, Node.js"
                }
            ],
            "preferred_rate": 85.00,
            "minimum_rate": 70.00,
            "currency": "USD",
            "availability": 15,
            "should_qualify": False,
            "qualification_reason": "Availability <20 hrs/wk"
        },
        {
            "name": "Raj Patel",
            "email": "raj.patel@example.com",
            "location": "Bangalore, India",
            "linkedin": "https://linkedin.com/in/rajpatel",
            "work_history": [
                {
                    "company": "Airbnb",
                    "title": "Software Engineer",
                    "start": "2020-10-25",
                    "end": "2024-10-25",
                    "technologies": "React, Ruby on Rails, PostgreSQL, Redis"
                }
            ],
            "preferred_rate": 75.00,
            "minimum_rate": 65.00,
            "currency": "USD",
            "availability": 30,
            "should_qualify": True,
            "qualification_reason": "Tier-1 company (Airbnb) + exactly 4 years (edge case)"
        },
        {
            "name": "Emma Schmidt",
            "email": "emma.schmidt@example.com",
            "location": "Sydney, Australia",
            "linkedin": "https://linkedin.com/in/emmaschmidt",
            "work_history": [
                {
                    "company": "Australian Tech Co",
                    "title": "Senior Developer",
                    "start": "2019-01-01",
                    "end": "2024-10-25",
                    "technologies": "Java, Spring Boot, Microservices"
                },
                {
                    "company": "Digital Agency",
                    "title": "Developer",
                    "start": "2018-06-01",
                    "end": "2018-12-31",
                    "technologies": "PHP, Laravel, MySQL"
                }
            ],
            "preferred_rate": 90.00,
            "minimum_rate": 75.00,
            "currency": "USD",
            "availability": 25,
            "should_qualify": False,
            "qualification_reason": "Location not in approved list (Australia)"
        },
        {
            "name": "David Kim",
            "email": "david.kim@example.com",
            "location": "Seattle, WA, USA",
            "linkedin": "https://linkedin.com/in/davidkim",
            "work_history": [
                {
                    "company": "Netflix",
                    "title": "Senior Software Engineer",
                    "start": "2022-06-01",
                    "end": "2024-10-25",
                    "technologies": "Java, Microservices, Streaming Infrastructure"
                },
                {
                    "company": "Tesla",
                    "title": "Software Engineer",
                    "start": "2020-01-01",
                    "end": "2022-05-31",
                    "technologies": "Python, Embedded Systems, Automation"
                },
                {
                    "company": "Apple",
                    "title": "Junior Engineer",
                    "start": "2019-06-01",
                    "end": "2019-12-31",
                    "technologies": "Swift, iOS Development, macOS"
                }
            ],
            "preferred_rate": 98.00,
            "minimum_rate": 85.00,
            "currency": "USD",
            "availability": 28,
            "should_qualify": True,
            "qualification_reason": "Multiple tier-1 companies (Netflix, Tesla, Apple)"
        },
        {
            "name": "Sofia Martinez",
            "email": "sofia.martinez@example.com",
            "location": "Toronto, Canada",
            "linkedin": "https://linkedin.com/in/sofiamartinez",
            "work_history": [
                {
                    "company": "Startup Innovations",
                    "title": "Developer",
                    "start": "2022-01-01",
                    "end": "2024-10-25",
                    "technologies": "TypeScript, Vue.js, Firebase"
                },
                {
                    "company": "WebDev Agency",
                    "title": "Junior Developer",
                    "start": "2021-06-01",
                    "end": "2021-12-31",
                    "technologies": "HTML, CSS, JavaScript, WordPress"
                }
            ],
            "preferred_rate": 80.00,
            "minimum_rate": 65.00,
            "currency": "USD",
            "availability": 30,
            "should_qualify": False,
            "qualification_reason": "Only 3 years experience + no tier-1 company"
        }
    ]

    print("=" * 70)
    print("Creating 10 Test Applicants")
    print("=" * 70)
    print()

    # Query max existing Applicant ID to continue sequence
    print("Finding max existing Applicant ID...")
    existing_applicants = applicants_table.all()
    max_id = 0
    for record in existing_applicants:
        current_id = record['fields'].get('Applicant ID', 0)
        if current_id and current_id > max_id:
            max_id = current_id

    next_id = max_id + 1
    print(f"✓ Starting from Applicant ID: {next_id}")
    print()

    created_count = 0
    qualified_count = 0

    for idx, applicant_data in enumerate(test_applicants, 1):
        print(f"[{idx}/10] Creating {applicant_data['name']}...")

        try:
            # Step 1: Create Applicants record with managed ID
            applicant_record = applicants_table.create({
                "Applicant ID": next_id
            })
            applicant_id = applicant_record['id']
            print(f"  ✓ Applicants record created: {applicant_id} (Applicant ID: {next_id})")
            next_id += 1  # Increment for next applicant

            # Step 2: Create Personal Details record
            personal_record = personal_details_table.create({
                "Full Name": applicant_data['name'],
                "Email": applicant_data['email'],
                "Location": applicant_data['location'],
                "LinkedIn": applicant_data['linkedin'],
                "Applicant ID": [applicant_id]
            })
            print(f"  ✓ Personal Details created: {personal_record['id']}")

            # Step 3: Create Work Experience records
            for work in applicant_data['work_history']:
                work_record = work_experience_table.create({
                    "Company": work['company'],
                    "Title": work['title'],
                    "Start": work['start'],
                    "End": work['end'],
                    "Technologies": work['technologies'],
                    "Applicant ID": [applicant_id]
                })
                print(f"  ✓ Work Experience created: {work['company']} ({work_record['id']})")

            # Step 4: Create Salary Preferences record
            salary_record = salary_preferences_table.create({
                "Preferred Rate": applicant_data['preferred_rate'],
                "Minimum Rate": applicant_data['minimum_rate'],
                "Currency": applicant_data['currency'],
                "Availability (hrs/wk)": applicant_data['availability'],
                "Applicant ID": [applicant_id]
            })
            print(f"  ✓ Salary Preferences created: {salary_record['id']}")

            # Show qualification status
            if applicant_data['should_qualify']:
                print(f"  ✓ Should QUALIFY: {applicant_data['qualification_reason']}")
                qualified_count += 1
            else:
                print(f"  ✗ Should NOT qualify: {applicant_data['qualification_reason']}")

            created_count += 1
            print()

        except Exception as e:
            print(f"  ERROR: Failed to create {applicant_data['name']}: {e}")
            print()

    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total applicants created: {created_count}/10")
    print(f"Should qualify for shortlist: {qualified_count}")
    print(f"Should NOT qualify: {created_count - qualified_count}")
    print()
    print("Test Coverage:")
    print("  ✓ Tier-1 company qualification (Google, Meta, Amazon, Airbnb, Netflix, Tesla, Apple)")
    print("  ✓ Years of experience qualification (4+ years)")
    print("  ✓ Edge cases (exactly $100/hr, exactly 4 years)")
    print("  ✓ Failure cases (rate too high, availability too low, wrong location, insufficient experience)")
    print("  ✓ Diverse locations (USA, Canada, UK, Germany, India, Australia)")
    print("  ✓ Multiple work experiences per applicant (1-3 jobs each)")
    print()
    print("Next steps:")
    print("  1. View your base: https://airtable.com/{base_id}")
    print("  2. Run compress_data.py to test JSON compression")
    print("  3. Run shortlist_evaluator.py to test qualification logic")
    print("  4. Run llm_evaluator.py to test LLM enrichment")
    print()

if __name__ == "__main__":
    main()
