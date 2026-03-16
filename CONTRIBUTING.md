# Contributing to Legacy AI

Thank you for your interest in contributing to the Legacy AI platform. This guide covers how to set up your development environment, coding standards, and the process for submitting changes.

## Code of Conduct

Be respectful, inclusive, and constructive. This project deals with deeply personal human experiences — treat every contribution with the care and sensitivity that reflects the platform's purpose.

## Development Setup

### Prerequisites

- Python 3.9+
- Docker 20.10+ and Docker Compose v2
- Git

### Local Setup

```bash
# Clone the repo
git clone https://github.com/ali919191/legacyai.git
cd legacyai

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install all dependencies including dev tools
pip install -r backend/requirements.txt

# Copy environment template
cp .env.example .env
```

### Running the Application

```bash
# Start all services with Docker Compose
docker-compose up --build

# Or run the backend directly (requires PostgreSQL running locally)
cd backend
python app.py
```

## Code Standards

All Python code must pass the following checks before a pull request can be merged.

### Formatting

```bash
# Auto-format code with Black
black backend/app backend/tests
```

### Linting

```bash
# Check for code quality issues
ruff check backend/app backend/tests
```

### Type Checking

```bash
# Run static type analysis
mypy backend/app backend/tests
```

### Running Tests

```bash
# Run the full test suite
PYTHONPATH=backend pytest backend/tests -v

# Or using Make
make test
```

All checks are also run automatically by the CI pipeline on every push and pull request.

## Pre-commit Hooks

Install pre-commit hooks to catch issues before committing:

```bash
pip install pre-commit
pre-commit install
```

Hooks are configured in `.pre-commit-config.yaml` and run Black and Ruff automatically on staged files.

## Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable, production-ready code |
| `develop` | Integration branch for features |
| `feature/<name>` | Individual feature branches |
| `fix/<name>` | Bug fix branches |

### Workflow

1. Fork the repository and create a feature branch from `develop`
2. Write code with tests
3. Ensure all CI checks pass locally
4. Open a pull request targeting `develop`
5. Request a code review
6. Merge after approval

## Writing Tests

- Place tests in `backend/tests/` following the naming pattern `test_<service_name>.py`
- Use the `test_logger` utility to log test results to `tests.log`
- Each test class should inherit from `unittest.TestCase`
- Aim for at least one test per public method

### Test Logger Usage

```python
from utils.test_logger import test_logger

test_logger.log_test_result(
    test_name="ServiceName.method_being_tested",
    input_params={"key": "value"},
    expected_result={"key": "expected"},
    actual_result={"key": "actual"},
    status="PASS",  # or "FAIL"
)
```

## Submitting a Pull Request

1. Ensure all tests pass: `make test`
2. Ensure linting passes: `make lint`
3. Ensure formatting is correct: `make format-check`
4. Update `README.md` if you added a new service, endpoint, or changed the architecture
5. Add a clear description to your PR explaining what changed and why

## Reporting Issues

Use GitHub Issues to report bugs or request features. Include:

- A clear description of the problem
- Steps to reproduce
- Expected vs. actual behaviour
- Python version and OS

## Questions

Open a GitHub Discussion for general questions or design discussions.
