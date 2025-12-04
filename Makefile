.PHONY: help venv setup install install-dev test lint format type-check clean clean-venv build dist run-ocr run-viewer act all

# Colors for output
YELLOW := \033[0;33m
GREEN := \033[0;32m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Python and virtualenv settings
PYTHON := python3
VENV_NAME := ocrenv
VENV_BIN := $(VENV_NAME)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip
VENV_ACTIVATE := source $(VENV_BIN)/activate

help:
	@echo "$(BLUE)PDFTools Makefile$(NC)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(NC)"
	@echo "  $(GREEN)venv$(NC)          - Create virtual environment only"
	@echo "  $(GREEN)setup$(NC)         - Create virtual environment and install dependencies"
	@echo "  $(GREEN)install$(NC)       - Install runtime dependencies"
	@echo "  $(GREEN)install-dev$(NC)   - Install development dependencies"
	@echo "  $(GREEN)test$(NC)          - Run unit tests with coverage"
	@echo "  $(GREEN)lint$(NC)          - Run code quality checks (flake8, black, isort, mypy)"
	@echo "  $(GREEN)format$(NC)        - Format code with black and isort"
	@echo "  $(GREEN)type-check$(NC)    - Run type checking with mypy"
	@echo "  $(GREEN)clean$(NC)         - Remove build artifacts and cache"
	@echo "  $(GREEN)clean-venv$(NC)    - Remove virtual environment"
	@echo "  $(GREEN)build$(NC)         - Build the Python package"
	@echo "  $(GREEN)dist$(NC)          - Build distributions (tarball and wheel)"
	@echo "  $(GREEN)run-ocr$(NC)       - Run PDF to Markdown on a PDF (usage: make run-ocr PDF=path/to/file.pdf)"
	@echo "  $(GREEN)run-viewer$(NC)    - Run Streamlit markdown viewer"
	@echo "  $(GREEN)act$(NC)           - Activate the virtual environment"
	@echo "  $(GREEN)all$(NC)           - Run setup, lint, test, and build"
	@echo ""

.venv-check:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(YELLOW)Virtual environment not found. Run 'make setup' first.$(NC)"; \
		exit 1; \
	fi

venv:
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV_NAME)
	$(VENV_PIP) install --upgrade pip setuptools wheel
	@echo "$(GREEN)✓ Virtual environment created at $(VENV_NAME)/$(NC)"
	@echo "$(YELLOW)To activate the environment, run:$(NC)"
	@echo "  source $(VENV_BIN)/activate"

setup:
	@echo "$(BLUE)Setting up virtual environment and dependencies...$(NC)"
	$(PYTHON) -m venv $(VENV_NAME)
	$(VENV_PIP) install --upgrade pip setuptools wheel
	$(VENV_PIP) install -r requirements.txt
	$(VENV_PIP) install -e ".[dev]"
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo "$(YELLOW)To activate the environment, run:$(NC)"
	@echo "  source $(VENV_BIN)/activate"

install: .venv-check
	@echo "$(BLUE)Installing runtime dependencies...$(NC)"
	$(VENV_PIP) install -r requirements.txt
	$(VENV_PIP) install .
	@echo "$(GREEN)✓ Installation complete!$(NC)"

install-dev: .venv-check
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(VENV_PIP) install -e ".[dev]"
	@echo "$(GREEN)✓ Development dependencies installed!$(NC)"

test: .venv-check
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(VENV_PYTHON) -m pytest tests/ --cov=pdftools --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Tests complete! Coverage report in htmlcov/index.html$(NC)"

lint: .venv-check
	@echo "$(BLUE)Running code quality checks...$(NC)"
	@echo "  Flake8..."
	$(VENV_PYTHON) -m flake8 ocr/ --max-line-length=100 --max-complexity=10
	@echo "  Black..."
	$(VENV_PYTHON) -m black ocr/ --check --line-length=100
	@echo "  isort..."
	$(VENV_PYTHON) -m isort ocr/ --check-only --profile=black
	@echo "  mypy..."
	$(VENV_PYTHON) -m mypy ocr/ --ignore-missing-imports
	@echo "$(GREEN)✓ All checks passed!$(NC)"

format: .venv-check
	@echo "$(BLUE)Formatting code...$(NC)"
	@echo "  Black..."
	$(VENV_PYTHON) -m black ocr/ --line-length=100
	@echo "  isort..."
	$(VENV_PYTHON) -m isort ocr/ --profile=black
	@echo "$(GREEN)✓ Code formatted!$(NC)"

type-check: .venv-check
	@echo "$(BLUE)Running type checks with mypy...$(NC)"
	$(VENV_PYTHON) -m mypy ocr/ --ignore-missing-imports
	@echo "$(GREEN)✓ Type checking complete!$(NC)"

clean:
	@echo "$(BLUE)Cleaning up build artifacts...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .mypy_cache/ .pytest_cache/
	@echo "$(GREEN)✓ Cleaned!$(NC)"

clean-venv:
	@echo "$(BLUE)Removing virtual environment...$(NC)"
	rm -rf $(VENV_NAME)
	@echo "$(GREEN)✓ Virtual environment removed!$(NC)"

build: .venv-check
	@echo "$(BLUE)Building package...$(NC)"
	$(VENV_PYTHON) -m build
	@echo "$(GREEN)✓ Build complete!$(NC)"

dist: build
	@echo "$(BLUE)Distribution artifacts created in dist/:$(NC)"
	ls -lh dist/
	@echo "$(GREEN)✓ Ready for distribution!$(NC)"

run-ocr: .venv-check
	@if [ -z "$(PDF)" ]; then \
		echo "$(YELLOW)Error: PDF file not specified$(NC)"; \
		echo "Usage: make run-ocr PDF=path/to/document.pdf"; \
		exit 1; \
	fi
	@echo "$(BLUE)Running PDF to Markdown on $(PDF)...$(NC)"
	$(VENV_PYTHON) ocr/mistral_ocr.py "$(PDF)"

run-viewer: .venv-check
	@echo "$(BLUE)Starting Streamlit markdown viewer...$(NC)"
	@echo "$(YELLOW)Open http://localhost:8501 in your browser$(NC)"
	$(VENV_BIN)/streamlit run ocr/sl_mdviewer.py

act: .venv-check
	@echo "$(BLUE)Run this to activate:$(NC)"
	@echo "  source $(VENV_BIN)/activate"

all: setup
	@echo "$(GREEN)✓ Setup complete! Use 'make lint', 'make test', and 'make build' separately.$(NC)"
