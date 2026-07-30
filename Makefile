PYTHON := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python; fi)

.PHONY: lock install check test lint format compile governance-demo governance-check

lock:
	uv pip compile requirements.in -o requirements.lock

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.lock
	$(PYTHON) -m pip install -e ".[dev]"

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m black --check .
	$(PYTHON) -m mypy .

test:
	$(PYTHON) -m pytest -q

compile:
	$(PYTHON) -m compileall master_orchestrator.py models.py src runtime_agent tests

governance-demo:
	PYTHONPATH=. $(PYTHON) scripts/generate_governance_demo.py

governance-check:
	PYTHONPATH=. $(PYTHON) scripts/check_governance_demo.py

check: lint test compile governance-check

format:
	$(PYTHON) -m ruff check --fix .
	$(PYTHON) -m black .
