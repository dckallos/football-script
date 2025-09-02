# Contributing to football-script

Thanks for helping build a Python‑first programming language! By participating, you agree to abide by our [Code of Conduct](./CODE_OF_CONDUCT.md).

## Quick start (local)

- **Python**: 3.11+ recommended.
- **Tools** (choose one workflow):
    - **Hatch** for builds/dev envs (`pip install hatch`) – modern PEP 517/518/621 flow.
    - **pipx** to install CLIs in isolated venvs (`pipx install hatch`).
    - **uv** for super‑fast Python/packaging (optional).

### Setup

```bash
# clone your fork
git clone https://github.com/porchanalytics/football-script.git
cd football-script

# dev deps (from pyproject once added)
python -m pip install -U pip
pip install -e ".[dev]"

# or with Hatch
pip install hatch
hatch env create

# install pre-commit hooks (after .pre-commit-config.yaml is added)
pip install pre-commit
pre-commit install
```

### Test & coverage

```bash
pytest -q
pytest --cov=football_script --cov-report=term --cov-report=xml
```

### Lint/format/type-check

```bash
ruff check --fix .
ruff format .
black .             # if you prefer Black; Ruff format also available
isort .
mypy .
```

### Branch & PR

- Work on feature branches off `main`.
- Write concise commits; include tests when adding features/fixes.
- PR checklist: tests green, coverage unchanged or better, linters clean.

### Releasing (later)

- We’ll use Hatch to build wheels (`hatch build`) and standard PyPI publishing.
