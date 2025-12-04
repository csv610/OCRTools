# Contributing to PDFTools

Thank you for your interest in contributing to PDFTools! We welcome contributions of all kinds, including bug reports, feature requests, documentation improvements, and code changes.

## Code of Conduct

This project is committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

## Getting Started

### 1. Fork the Repository

Click the "Fork" button on GitHub to create your own copy of the repository.

### 2. Clone Your Fork

```bash
git clone https://github.com/yourusername/PDFTools.git
cd PDFTools
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs PDFTools in editable mode with all development tools including:
- `pytest` - Testing framework
- `black` - Code formatter
- `flake8` - Linter
- `mypy` - Type checker
- `isort` - Import sorter

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/bug-description
```

Use descriptive branch names:
- `feature/` for new features
- `fix/` for bug fixes
- `docs/` for documentation changes
- `refactor/` for code refactoring
- `test/` for test improvements

### 2. Make Your Changes

Write clean, well-documented code:

```python
def process_document(file_path: str, output_dir: str) -> Dict[str, Any]:
    """
    Process a document and extract content.

    Args:
        file_path: Path to the input document
        output_dir: Directory to save processed output

    Returns:
        Dictionary containing processing results

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If file format is not supported
    """
    # Implementation here
```

### 3. Format Your Code

```bash
# Format with black
black ocr/

# Sort imports with isort
isort ocr/

# Check with flake8
flake8 ocr/

# Type checking with mypy
mypy ocr/
```

Or use the convenient all-in-one command:

```bash
black ocr/ && isort ocr/ && flake8 ocr/ && mypy ocr/
```

### 4. Write or Update Tests

Add tests for new functionality:

```bash
pytest tests/
pytest tests/ -v  # Verbose output
pytest tests/ --cov=pdftools  # With coverage report
```

### 5. Run All Checks

Before committing, ensure all checks pass:

```bash
pytest tests/ --cov=pdftools
black --check ocr/
isort --check ocr/
flake8 ocr/
mypy ocr/
```

### 6. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: describe your change concisely

- Point 1: Explain the why and what
- Point 2: Include any relevant context
- Point 3: Reference issue numbers if applicable (#123)"
```

Good commit message examples:
- ✅ `Add retry logic to API requests with exponential backoff`
- ✅ `Fix memory leak in image processing pipeline`
- ✅ `Improve error messages for invalid PDF files`
- ❌ `Fix bug` (too vague)
- ❌ `Update code` (doesn't explain what or why)

### 7. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 8. Create a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill in the PR description with:
   - Summary of changes
   - Why these changes are needed
   - Any breaking changes
   - Screenshots/examples if relevant
5. Submit the PR

## Pull Request Guidelines

### PR Title Format

Use clear, descriptive titles:
- ✅ `Add support for batch PDF processing`
- ✅ `Fix OCR timeout on large files`
- ✅ `Improve error messages for API failures`

### PR Description Template

```markdown
## Summary
Brief description of your changes.

## Motivation and Context
Why is this change needed? What problem does it solve?

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Point 1
- Point 2
- Point 3

## Testing
How have you tested these changes?
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] All tests passing

## Screenshots (if applicable)
Add screenshots or examples here.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
- [ ] All tests passing
```

## Code Style Guidelines

### Python Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) and use [Black](https://github.com/psf/black) for formatting.

**Key Points:**
- Use type hints: `def process(file: str, timeout: int) -> Dict[str, Any]:`
- Use docstrings for all public functions/classes (Google style)
- Maximum line length: 100 characters
- Use meaningful variable names
- Keep functions focused and concise

### Example Function

```python
def extract_text_from_pdf(
    pdf_path: str,
    max_pages: Optional[int] = None,
) -> str:
    """
    Extract text content from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        max_pages: Maximum number of pages to process (None for all)

    Returns:
        Extracted text content

    Raises:
        FileNotFoundError: If PDF file not found
        ValueError: If PDF is invalid or corrupted

    Example:
        >>> text = extract_text_from_pdf("document.pdf", max_pages=10)
        >>> print(len(text))
        45230
    """
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Implementation
    return extracted_text
```

## Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_mistral_ocr.py
├── test_olma_ocr.py
└── test_streamlit_viewer.py
```

### Writing Tests

```python
import pytest
from pathlib import Path

def test_process_valid_pdf(tmp_path):
    """Test processing a valid PDF file."""
    # Arrange
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_text("test content")

    # Act
    result = process_pdf(str(pdf_path))

    # Assert
    assert result is not None
    assert isinstance(result, dict)

def test_process_missing_pdf():
    """Test handling of missing PDF file."""
    with pytest.raises(FileNotFoundError):
        process_pdf("nonexistent.pdf")
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_mistral_ocr.py::test_process_valid_pdf

# Run with coverage
pytest --cov=pdftools --cov-report=html

# Run in verbose mode
pytest -v

# Stop on first failure
pytest -x
```

## Documentation

### Adding Documentation

1. Update docstrings for public APIs
2. Update README.md for usage examples
3. Create inline comments for complex logic
4. Update CHANGELOG if making significant changes

### Docstring Format

We use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    One-line summary of the function.

    Longer description explaining the function's purpose,
    behavior, and any important details.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When validation fails
        TypeError: When type is incorrect

    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
```

## Reporting Bugs

When reporting a bug, include:

1. **Description**: Clear summary of the issue
2. **Steps to Reproduce**: Exact steps to trigger the bug
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**:
   - Python version
   - OS and version
   - Relevant dependencies
6. **Logs/Error Messages**: Full error traces
7. **Screenshots**: If visually relevant

Example:

```
Title: PDF processing fails with non-ASCII filenames

Steps to reproduce:
1. Create a PDF with filename containing Chinese characters
2. Run: python ocr/mistral_ocr.py "文件.pdf"
3. Observe the error

Expected: PDF should be processed successfully
Actual: UnicodeDecodeError: 'utf-8' codec can't decode byte...

Environment:
- Python 3.10.5
- macOS 13.2
- mistralai==0.1.5
```

## Feature Requests

When suggesting a feature, explain:

1. **Use Case**: What problem does this solve?
2. **Proposed Solution**: How would it work?
3. **Alternatives**: Are there other approaches?
4. **Examples**: Usage examples would be helpful

## Review Process

1. Maintainers will review your PR
2. Changes may be requested
3. Update your PR based on feedback
4. Once approved, your PR will be merged
5. Your contribution will be credited

## Maintenance Notes

### For Maintainers

- Use semantic versioning
- Update CHANGELOG.md
- Tag releases on GitHub
- Update PyPI package
- Acknowledge contributors

## Questions?

- Check existing issues and discussions
- Review the README.md and documentation
- Open a GitHub Discussion for questions
- Create an issue for bugs and features

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to PDFTools! 🎉
