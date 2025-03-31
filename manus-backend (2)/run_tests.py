#!/usr/bin/env python3
"""
Test runner script for Manus Backend.
"""

import os
import sys
import pytest
import argparse
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("manus-backend.test_runner")

def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Manus Backend Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Default to running all tests if no specific tests are requested
    if not any([args.unit, args.integration, args.all]):
        args.all = True
    
    # Set verbosity
    verbosity = 2 if args.verbose else 1
    
    # Determine which tests to run
    test_paths = []
    
    if args.unit or args.all:
        logger.info("Running unit tests")
        test_paths.append("tests/")
    
    if args.integration or args.all:
        logger.info("Running integration tests")
        # Integration tests are run separately using the integration test script
        os.system("python src/integration/test_integration.py")
    
    # Run pytest for unit tests
    if test_paths:
        exit_code = pytest.main(["-v"] if args.verbose else [] + test_paths)
        sys.exit(exit_code)

if __name__ == "__main__":
    main()
