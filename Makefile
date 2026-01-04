.PHONY: format lint build clean publish test help

# Default Python interpreter
PYTHON ?= python3

# Package name
PACKAGE = pymtml

help:
	@echo "Available targets:"
	@echo "  format    - Format code with isort + black"
	@echo "  lint      - Run linter (flake8)"
	@echo "  test      - Run tests"
	@echo "  build     - Build wheel package"
	@echo "  clean     - Clean build artifacts"
	@echo "  publish   - Upload wheel to PyPI"
	@echo "  all       - Format, lint, test, build"

# Format code using isort + black
format:
	$(PYTHON) -m isort $(PACKAGE).py example.py test_*.py
	$(PYTHON) -m black $(PACKAGE).py example.py test_*.py

# Lint code using flake8
lint:
	$(PYTHON) -m flake8 $(PACKAGE).py example.py --max-line-length=120 --ignore=E501,W503

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

