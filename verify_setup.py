#!/usr/bin/env python3
"""
Setup verification script for Airtable Contractor Application System.
Checks that all prerequisites are properly configured.
"""

import sys
import os
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def check_env_file():
    """Check if .env file exists."""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Create it from template: cp env.template .env")
        return False
    print("✓ .env file exists")
    return True


def check_dependencies():
    """Check if required Python packages are installed."""
    required_packages = ['pyairtable', 'openai', 'dotenv', 'requests']
    missing = []
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"❌ {package} not installed")
            missing.append(package)
    
    if missing:
        print(f"\n   Install missing packages: pip install -r requirements.txt")
        return False
    return True


def check_env_variables():
    """Check if required environment variables are set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['AIRTABLE_PAT', 'AIRTABLE_BASE_ID', 'OPENAI_API_KEY']
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or 'your_' in value or 'XXXX' in value:
            print(f"❌ {var} not configured")
            missing.append(var)
        else:
            # Show partial value for verification
            if var == 'AIRTABLE_PAT':
                masked = value[:10] + "..." if len(value) > 10 else value
            elif var == 'AIRTABLE_BASE_ID':
                masked = value[:10] + "..." if len(value) > 10 else value
            elif var == 'OPENAI_API_KEY':
                masked = value[:8] + "..." if len(value) > 8 else value
            else:
                masked = value
            print(f"✓ {var} configured ({masked})")
    
    if missing:
        print(f"\n   Configure missing variables in .env file")
        return False
    return True


def check_airtable_connection():
    """Check if Airtable connection works."""
    try:
        from src.config import get_config
        from src.airtable_client import AirtableClient
        
        print("  Attempting to connect to Airtable...")
        config = get_config()
        client = AirtableClient(config.airtable_pat, config.airtable_base_id)
        
        # Try to get applicants table
        applicants = client.get_all_records("Applicants")
        print(f"✓ Connected to Airtable successfully")
        print(f"  Found {len(applicants)} applicant(s) in the base")
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Airtable: {e}")
        print("   Check your AIRTABLE_PAT and AIRTABLE_BASE_ID")
        return False


def check_openai_key():
    """Check if OpenAI API key is valid."""
    try:
        from src.config import get_config
        config = get_config()
        
        if not config.openai_api_key.startswith('sk-'):
            print(f"❌ OpenAI API key format invalid (should start with 'sk-')")
            return False
        
        print(f"✓ OpenAI API key format looks correct")
        print(f"  Note: Actual validity will be tested on first API call")
        return True
        
    except Exception as e:
        print(f"❌ Error checking OpenAI key: {e}")
        return False


def check_project_structure():
    """Check if all required files and directories exist."""
    required_paths = [
        'src/__init__.py',
        'src/config.py',
        'src/airtable_client.py',
        'src/json_compressor.py',
        'src/json_decompressor.py',
        'src/shortlist_evaluator.py',
        'src/llm_evaluator.py',
        'scripts/compress_data.py',
        'scripts/decompress_data.py',
        'scripts/evaluate_candidates.py',
        'cli.py',
        'requirements.txt',
        'README.md',
        'AIRTABLE_SETUP.md'
    ]
    
    all_exist = True
    for path in required_paths:
        if Path(path).exists():
            print(f"✓ {path}")
        else:
            print(f"❌ {path} missing")
            all_exist = False
    
    return all_exist


def main():
    """Run all verification checks."""
    print_header("Airtable Contractor Application System")
    print("Setup Verification")
    
    checks = [
        ("Project Structure", check_project_structure),
        ("Python Dependencies", check_dependencies),
        (".env File", check_env_file),
        ("Environment Variables", check_env_variables),
        ("OpenAI API Key", check_openai_key),
        ("Airtable Connection", check_airtable_connection),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print_header(check_name)
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            results.append((check_name, False))
    
    # Summary
    print_header("Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nChecks passed: {passed}/{total}\n")
    
    for check_name, result in results:
        status = "✓" if result else "❌"
        print(f"{status} {check_name}")
    
    if passed == total:
        print("\n🎉 All checks passed! Your setup is ready.")
        print("\nNext steps:")
        print("  1. Add test applicants via Airtable forms")
        print("  2. Run: python cli.py process-all")
        print("  3. Check results in your Airtable base")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nFor help, see:")
        print("  - AIRTABLE_SETUP.md for Airtable configuration")
        print("  - README.md for general setup")
        print("  - env.template for environment variables")
        return 1


if __name__ == "__main__":
    sys.exit(main())

