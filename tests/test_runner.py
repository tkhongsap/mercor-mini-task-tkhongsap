#!/usr/bin/env python3
"""
Test Runner for Airtable Schema Setup Tests

Runs all unit tests and provides detailed reporting.

Usage:
    python tests/test_runner.py
    python tests/test_runner.py --verbose
"""

import sys
import unittest
from io import StringIO


def run_tests(verbose=False):
    """
    Run all schema setup tests and return results

    Args:
        verbose: If True, print detailed test output

    Returns:
        tuple: (success: bool, results: TestResult)
    """
    # Discover and load tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_schema_setup.py')

    # Run tests with custom verbosity
    verbosity = 2 if verbose or '--verbose' in sys.argv else 1
    runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)

    print("=" * 70)
    print("Airtable Schema Setup - Unit Test Suite")
    print("=" * 70)
    print()

    result = runner.run(suite)

    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print()

    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED - Schema is 100% PRD compliant!")
        print()
        print("Your Airtable schema is correctly configured and ready for:")
        print("  1. Creating Airtable forms for data collection")
        print("  2. Building Python compression/decompression scripts")
        print("  3. Building shortlist evaluator")
        print("  4. Building LLM evaluator")
    else:
        print("✗ TESTS FAILED - Schema has issues that need attention")
        print()

        if result.failures:
            print("Failed Tests:")
            for test, traceback in result.failures:
                print(f"  - {test}")

        if result.errors:
            print("Test Errors:")
            for test, traceback in result.errors:
                print(f"  - {test}")

    print()
    print("=" * 70)

    return result.wasSuccessful(), result


def main():
    """Main entry point"""
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    success, result = run_tests(verbose=verbose)

    # Exit with appropriate code for CI/CD
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
