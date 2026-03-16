.PHONY: help install test lint format format-check type-check quality build up down logs clean

PYTHONPATH := backend
PYTHON     := python
PYTEST     := $(PYTHON) -m pytest

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ── Dependencies ──────────────────────────────────────────────────────────────

install:  ## Install Python dependencies
	pip install -r backend/requirements.txt

install-dev:  ## Install dev / quality-check dependencies
	pip install -r backend/requirements.txt
	pip install black ruff mypy pre-commit

# ── Testing ───────────────────────────────────────────────────────────────────

test:  ## Run all tests with verbose output
	PYTHONPATH=$(PYTHONPATH) $(PYTEST) backend/tests -v

test-cov:  ## Run tests with coverage report
	PYTHONPATH=$(PYTHONPATH) $(PYTEST) backend/tests -v --cov=backend/app --cov-report=term-missing

# ── Code quality ──────────────────────────────────────────────────────────────

format:  ## Auto-format code with black + ruff (writes files)
	black backend/ --line-length 100
	ruff check backend/ --fix

format-check:  ## Check formatting without writing files (CI mode)
	black backend/ --line-length 100 --check
	ruff check backend/

lint: format-check  ## Alias for format-check

type-check:  ## Run mypy static-type checks
	PYTHONPATH=$(PYTHONPATH) mypy backend/app --ignore-missing-imports

quality: format-check type-check test  ## Run all quality gates (lint + types + tests)

# ── Docker ────────────────────────────────────────────────────────────────────

build:  ## Build Docker images (no cache)
	docker compose build --no-cache

up:  ## Start all services in detached mode
	docker compose up -d

down:  ## Stop and remove containers
	docker compose down

logs:  ## Follow logs for all services
	docker compose logs -f

restart:  ## Restart all containers
	docker compose restart

# ── Utilities ─────────────────────────────────────────────────────────────────

clean:  ## Remove Python cache artifacts and coverage data
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc"     -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache"   -exec rm -rf {} + 2>/dev/null || true
	@echo "Cache artifacts removed."
