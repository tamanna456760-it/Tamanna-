# Simple Makefile for running auto-fix and build tasks
.PHONY: fix build test

fix:
	@echo "Running auto fix-and-build script..."
	@bash scripts/auto_build_and_fix.sh

build: test
	@echo "Build step complete (tests ran)."

test:
	@echo "Running tests..."
	@if [ -f requirements.txt ]; then python -m pip install -r requirements.txt; fi
	@if [ -f pytest.ini ] || [ -d tests ]; then python -m pytest -q; else echo "No pytest tests detected"; fi
