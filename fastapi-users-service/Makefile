.PHONY: test test-unit test-integration test-cov test-cov-html test-cov-report clean-test install-test

# Install test dependencies
install-test:
	pip install -r requirements.txt

# Run all tests
test:
	pytest

# Run only unit tests
test-unit:
	pytest -m unit

# Run only integration tests
test-integration:
	pytest -m integration

# Run tests with coverage (terminal output)
test-cov:
	pytest --cov=app --cov-report=term-missing

# Run tests with HTML coverage report
test-cov-html:
	pytest --cov=app --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

# Run tests with XML coverage report (for CI)
test-cov-xml:
	pytest --cov=app --cov-report=xml

# Run tests with all coverage reports
test-cov-report:
	pytest --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml

# Run specific test file
test-file:
	@echo "Usage: make test-file FILE=tests/unit/test_crud_user.py"
	pytest $(FILE) -v

# Run tests in parallel (requires pytest-xdist)
test-parallel:
	pytest -n auto

# Run tests with verbose output
test-verbose:
	pytest -vvs

# Run failed tests only
test-failed:
	pytest --lf

# Clean test artifacts
clean-test:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf test.db
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Quick test - run tests without coverage
test-quick:
	pytest --no-cov -q

# Watch mode (requires pytest-watch)
test-watch:
	ptw -- --testmon

# Help
help:
	@echo "Available commands:"
	@echo "  make test              - Run all tests"
	@echo "  make test-unit         - Run unit tests only"
	@echo "  make test-integration  - Run integration tests only"
	@echo "  make test-cov          - Run tests with coverage (terminal)"
	@echo "  make test-cov-html     - Run tests with HTML coverage report"
	@echo "  make test-cov-xml      - Run tests with XML coverage report"
	@echo "  make test-cov-report   - Run tests with all coverage reports"
	@echo "  make test-verbose      - Run tests with verbose output"
	@echo "  make test-failed       - Re-run only failed tests"
	@echo "  make test-quick        - Quick test run without coverage"
	@echo "  make clean-test        - Clean test artifacts"
	@echo "  make install-test      - Install test dependencies"

