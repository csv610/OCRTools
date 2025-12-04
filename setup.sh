#!/bin/bash

##############################################################################
# PDFTools Setup Script
#
# This script automates the setup and build process for PDFTools, including:
# - Virtual environment setup
# - Dependency installation
# - Code quality checks
# - Testing
# - Package building
#
# Usage:
#   ./setup.sh [command]
#
# Commands:
#   setup       - Create virtual environment and install dependencies
#   install     - Install runtime dependencies
#   dev         - Install development dependencies
#   test        - Run tests with coverage
#   lint        - Run code quality checks
#   format      - Format code
#   build       - Build the package
#   all         - Run all tasks (setup, lint, test, build)
#   clean       - Clean build artifacts
#   help        - Show this help message
#
##############################################################################

set -e  # Exit on error

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
VENV_NAME="ocrenv"
VENV_BIN="${VENV_NAME}/bin"
PYTHON="${VENV_BIN}/python"
PIP="${VENV_BIN}/pip"
PROJECT_NAME="pdftools"
PYTHON_VERSION="3.8"

# Helper functions
log_info() {
    echo -e "${BLUE}$1${NC}"
}

log_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    log_success "Python 3 found: $(python3 --version)"
}

create_venv() {
    if [ -d "$VENV_NAME" ]; then
        log_warning "Virtual environment '$VENV_NAME' already exists"
        return
    fi

    log_info "Creating virtual environment '$VENV_NAME'..."
    python3 -m venv "$VENV_NAME"
    log_success "Virtual environment created"
}

upgrade_pip() {
    log_info "Upgrading pip, setuptools, and wheel..."
    "$PIP" install --upgrade pip setuptools wheel
    log_success "pip, setuptools, and wheel upgraded"
}

install_requirements() {
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt not found"
        exit 1
    fi

    log_info "Installing runtime dependencies from requirements.txt..."
    "$PIP" install -r requirements.txt
    log_success "Runtime dependencies installed"
}

install_dev() {
    log_info "Installing development dependencies..."
    "$PIP" install -e ".[dev]" --no-build-isolation --no-deps || {
        # If that fails, try installing dev deps without the package
        "$PIP" install pytest>=7.4.0 pytest-cov>=4.1.0 black>=23.9.0 flake8>=6.0.0 mypy>=1.5.0 isort>=5.12.0 ruff>=0.10.0
    }
    log_success "Development dependencies installed"
}

install_package() {
    log_info "Installing package in editable mode..."
    "$PIP" install -e .
    log_success "Package installed"
}

run_linters() {
    log_info "Running code quality checks..."

    if ! command -v "$PYTHON" &> /dev/null; then
        log_error "Virtual environment not found. Run './setup.sh setup' first."
        exit 1
    fi

    log_info "  • flake8..."
    "$PYTHON" -m flake8 ocr/ --max-line-length=100 --max-complexity=10 || {
        log_error "flake8 checks failed"
        exit 1
    }

    log_info "  • black (checking)..."
    "$PYTHON" -m black ocr/ --check --line-length=100 || {
        log_error "black formatting check failed. Run './setup.sh format' to fix."
        exit 1
    }

    log_info "  • isort (checking)..."
    "$PYTHON" -m isort ocr/ --check-only --profile=black || {
        log_error "isort check failed. Run './setup.sh format' to fix."
        exit 1
    }

    log_info "  • mypy..."
    "$PYTHON" -m mypy ocr/ --ignore-missing-imports || {
        log_error "mypy type checking failed"
        exit 1
    }

    log_success "All code quality checks passed"
}

run_formatters() {
    log_info "Formatting code..."

    log_info "  • black..."
    "$PYTHON" -m black ocr/ --line-length=100

    log_info "  • isort..."
    "$PYTHON" -m isort ocr/ --profile=black

    log_success "Code formatted"
}

run_tests() {
    if [ ! -d "tests" ]; then
        log_warning "tests/ directory not found. Skipping tests."
        return
    fi

    log_info "Running tests with coverage..."
    "$PYTHON" -m pytest tests/ \
        --cov="${PROJECT_NAME}" \
        --cov-report=html \
        --cov-report=term-missing \
        || {
        log_error "Tests failed"
        exit 1
    }

    log_success "Tests passed! Coverage report in htmlcov/index.html"
}

build_package() {
    log_info "Building package..."

    "$PYTHON" -m build || {
        log_error "Build failed"
        exit 1
    }

    log_success "Package built successfully"
    log_info "Distribution artifacts:"
    ls -lh dist/
}

clean_artifacts() {
    log_info "Cleaning build artifacts..."

    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    rm -rf build/ dist/ .coverage htmlcov/ .mypy_cache/ .pytest_cache/

    log_success "Artifacts cleaned"
}

show_help() {
    head -22 "$0" | tail -21
}

# Main script logic
main() {
    local command="${1:-setup}"

    case "$command" in
        setup)
            log_info "Setting up PDFTools..."
            check_python
            create_venv
            upgrade_pip
            install_requirements
            install_dev
            log_success "Setup complete!"
            echo ""
            log_info "To activate the virtual environment, run:"
            echo "  source ${VENV_BIN}/activate"
            ;;
        install)
            check_python
            create_venv
            upgrade_pip
            install_requirements
            install_package
            log_success "Installation complete!"
            ;;
        dev)
            log_info "Installing development dependencies..."
            if [ ! -d "$VENV_NAME" ]; then
                log_error "Virtual environment not found. Run './setup.sh setup' first."
                exit 1
            fi
            install_dev
            log_success "Development dependencies installed!"
            ;;
        test)
            if [ ! -d "$VENV_NAME" ]; then
                log_error "Virtual environment not found. Run './setup.sh setup' first."
                exit 1
            fi
            run_tests
            ;;
        lint)
            if [ ! -d "$VENV_NAME" ]; then
                log_error "Virtual environment not found. Run './setup.sh setup' first."
                exit 1
            fi
            run_linters
            ;;
        format)
            if [ ! -d "$VENV_NAME" ]; then
                log_error "Virtual environment not found. Run './setup.sh setup' first."
                exit 1
            fi
            run_formatters
            ;;
        build)
            if [ ! -d "$VENV_NAME" ]; then
                log_error "Virtual environment not found. Run './setup.sh setup' first."
                exit 1
            fi
            clean_artifacts
            build_package
            ;;
        clean)
            clean_artifacts
            log_info "To remove the virtual environment, run: rm -rf ${VENV_NAME}"
            ;;
        all)
            log_info "Running full setup and build pipeline..."
            check_python
            create_venv
            upgrade_pip
            install_requirements
            install_dev
            run_linters
            run_tests
            clean_artifacts
            build_package
            log_success "Full setup and build pipeline complete!"
            ;;
        help)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
