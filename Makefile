.PHONY: format lint build clean publish test help

# Default Python interpreter
PYTHON ?= python3

# The lint and format tools are pinned in .pre-commit-config.yaml; pre-commit
# provisions each one in its own environment, so no global install is needed.
PRECOMMIT ?= pre-commit

# Package name
PACKAGE = pymtml

help:
	@echo "Available targets:"
	@echo "  format    - Format the tree with the pinned pre-commit hooks"
	@echo "  lint      - Run the read-only checks (flake8, codespell, ast)"
	@echo "  test      - Run tests"
	@echo "  build     - Build wheel package"
	@echo "  clean     - Clean build artifacts"
	@echo "  publish   - Upload wheel to PyPI"
	@echo "  all       - Format, lint, test, build"

# Format the tree (isort, black, whitespace and end-of-file hooks)
format:
	$(PRECOMMIT) run --all-files

# Read-only checks: lint, spelling and syntax, the same hooks the gate runs
lint:
	$(PRECOMMIT) run flake8 --all-files
	$(PRECOMMIT) run codespell --all-files
	$(PRECOMMIT) run check-ast --all-files

# Run tests
test:
	$(PYTHON) -m pytest test_*.py -v

# Build wheel package
build: clean
	$(PYTHON) setup.py bdist_wheel

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ __pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# Publish to PyPI
publish: build
	$(PYTHON) -m twine upload --repository pypi dist/*.whl

# Run all checks and build
all: format lint test build
