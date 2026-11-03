# Safe validation and build targets for Tamanna AI.
.PHONY: fix build test setup-env run-server

fix:
	@bash scripts/auto_build_and_fix.sh

run-server:
	@python3 run_server.py

setup-env:
	@bash scripts/setup_env.sh

build: test
	@echo "Build validation complete."

test:
	@python -m pytest -q
