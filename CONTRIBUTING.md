# Contributing to Raster Thumbnail Generator

Thank you for your interest in contributing! This document provides guidelines for developers.

## Development Setup

### 1. Clone and Install for Development

```bash
git clone https://github.com/GNSSP-AgroHub/raster-thumbnail.git
cd raster-thumbnail
pip install -e .  # Install in development mode
```

### 2. Set Up Development Environment

```bash
# Install development dependencies (includes pre-commit, black, flake8, mypy)
pip install -e ".[dev]"

# Install test dependencies
pip install -r tests/requirements.txt

# Set up pre-commit hooks (REQUIRED)
pre-commit install

# Run tests to verify setup
python tests/test_simple.py
pytest tests/
```

### 3. Create Your Test Workspace

```bash
mkdir test_workspace
cd test_workspace
# Add your test .tif files to test_workspace/data/
# This folder is gitignored for personal experimentation
```

## Testing

### Run Simple Tests (no external dependencies):
```bash
python tests/test_simple.py
```

### Run Full Test Suite:
**Note: Always run pytest from the project root directory, not from the tests/ directory**

```bash
# All tests (from project root)
pytest

# All tests with verbose output
pytest -v

# With coverage report
pytest --cov=raster_thumbnail

# Specific test file
pytest tests/test_raster_thumbnail.py -v
```

### Test Structure
- `tests/test_simple.py` - Basic unit tests, no external dependencies
- `tests/test_raster_thumbnail.py` - Full test suite with pytest
- `tests/README.md` - Detailed testing documentation

## Code Quality & Style

This project uses automated code quality tools that run before every commit:

### Pre-commit Hooks (REQUIRED)
**All commits must pass these checks:**

```bash
# Install pre-commit hooks (one-time setup)
pre-commit install

# Run manually on all files (optional)
pre-commit run --all-files
```

### Code Quality Tools

1. **Black** - Code formatting (line length: 90)
2. **Flake8** - Style and syntax linting
3. **MyPy** - Static type checking
4. **isort** - Import sorting
5. **General hooks** - Trailing whitespace, file endings, YAML validation

### Manual Quality Checks

```bash
# Type checking
mypy raster_thumbnail/

# Linting
flake8 raster_thumbnail/

# Formatting (will modify files)
black raster_thumbnail/

# Import sorting (will modify files)
isort raster_thumbnail/
```

### Style Guidelines

- Follow PEP 8 style guidelines (enforced by flake8)
- Use type hints for all function parameters and return values (checked by mypy)
- Add docstrings to public functions
- Keep functions focused and testable
- Line length: 90 characters (enforced by black)

## Adding New Features

1. **Write tests first** - Add tests in `tests/test_raster_thumbnail.py`
2. **Implement feature** - Add functionality to appropriate module
3. **Update documentation** - Update docstrings and README if needed
4. **Test thoroughly** - Run full test suite

## Project Structure

```
raster-thumbnail/
├── raster_thumbnail/           # Main package
│   ├── __init__.py
│   ├── core.py                # Core processing functions
│   ├── utils.py               # High-level API functions
│   ├── logging_config.py      # Logging utilities
│   └── raster_config.json     # Raster type configuration
├── tests/                     # Unit tests (in git)
│   ├── test_simple.py
│   ├── test_raster_thumbnail.py
│   └── requirements.txt
├── test_workspace/            # Personal testing (gitignored)
│   ├── data/                  # Your test raster files
│   ├── output/                # Generated thumbnails
│   └── logs/                  # Log files
├── README.md                  # User documentation
├── CONTRIBUTING.md            # This file
└── pyproject.toml            # Package configuration
```

## Git Workflow

1. **Set up pre-commit hooks**: `pre-commit install` (one-time setup)
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. **Pre-commit hooks automatically run** on `git commit` (will block commits that fail)
5. Run tests: `pytest tests/`
6. Commit with clear messages (hooks ensure code quality)
7. Push and create a pull request

### ⚠️ Important: Commits will be rejected if they fail code quality checks!

If pre-commit hooks fail:
- Fix the issues reported by the tools
- Stage your fixes: `git add .`
- Retry the commit: `git commit`

## Adding New Raster Types

To support a new raster type:

1. **Edit `raster_config.json`**:
   ```json
   {
     "raster_types": {
       "new_type": {
         "name": "New Raster Type",
         "unit": "units",
         "colormap": "viridis",
          "visualization": {
           "use_percentile": false,
           "min_value": 0,
           "max_value": 100,
           "percentile_range": [2, 98] // use when use_percentile=true
         },
         "metadata_detection": {
           "filename_patterns": ["*new_type*"]
         }
       }
     }
   }
   ```

2. **Note about type detection**: The library now uses `selected_types` lists for type detection rather than a global priority list. When using the detection functions directly, specify which types should be considered.

3. **Add tests** for the new type in `tests/test_raster_thumbnail.py`
4. **Test with real data** in your `test_workspace/`

## Performance Considerations

- Use numpy operations for array processing
- Minimize memory usage for large rasters
- Consider chunked processing for very large files
- Profile performance-critical sections

## Debugging

Enable debug logging to troubleshoot issues:

```python
from raster_thumbnail.logging_config import setup_basic_logging
logger = setup_basic_logging(level=logging.DEBUG)
```

## Questions?

- Check existing issues on GitHub
- Review the tests for usage examples
- Look at `test_workspace/` examples for real usage patterns

## Pull Request Checklist

- [ ] **Pre-commit hooks installed and passing**: `pre-commit install`
- [ ] **All code quality checks pass**: `pre-commit run --all-files`
- [ ] **Type checking passes**: `mypy raster_thumbnail/`
- [ ] **Tests pass**: `pytest tests/`
- [ ] New features have tests
- [ ] Documentation updated if needed
- [ ] Commit messages are clear
- [ ] No personal files in `test_workspace/` committed

### Quick Quality Check Command
```bash
# Run all quality checks manually
pre-commit run --all-files && mypy raster_thumbnail/ && pytest tests/
```
