# Safe validation and build targets for Tamanna AI.
.PHONY: fix build test setup-env

fix:
	@bash scripts/auto_build_and_fix.sh

setup-env:
	@bash scripts/setup_env.sh

build: test
	@echo "Build validation complete."

test:
	@python -m pytest -q
