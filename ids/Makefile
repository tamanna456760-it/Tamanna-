.PHONY: help test test-verbose coverage config health report
PYTHON ?= python3
help:
	@echo "Tamanna AI IDS - Available Commands"
	@echo "  make test         Run IDS unit tests"
	@echo "  make test-verbose Run tests with detailed output"
	@echo "  make coverage     Run tests with coverage report"
	@echo "  make config       Validate and display IDS configuration"
	@echo "  make health       Run IDS health check"
	@echo "  make report       Generate IDS status report"
test:
	$(PYTHON) -m unittest discover -s ids/tests -p "test_*.py"
test-verbose:
	$(PYTHON) -m unittest discover -s ids/tests -p "test_*.py" -v
coverage:
	$(PYTHON) -m pytest ids/tests --cov=ids --cov-report=term-missing
config:
	$(PYTHON) -m ids.ids_cli config
health:
	$(PYTHON) -m ids.ids_cli health
report:
	$(PYTHON) -m ids.ids_cli report