#!/bin/bash

# Run all tests
make test
# or: pytest

# Run only unit tests
make test-unit

# Run only integration tests  
make test-integration

# Run with coverage (terminal output)
make test-cov

# Run with HTML coverage report
make test-cov-html
# Opens htmlcov/index.html

# Run with all coverage formats (CI-friendly)
make test-cov-report