# Unit Tests

This directory contains unit tests for the raster thumbnail generator package.

## Running Tests

### Simple tests (no external dependencies):
```bash
python tests/test_simple.py
```

### Full test suite (requires pytest):
```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=raster_thumbnail

# Run specific test file
pytest tests/test_raster_thumbnail.py -v
```

## Test Structure

- `test_simple.py` - Basic unit tests that don't require pytest
- `test_raster_thumbnail.py` - Complete test suite with pytest
- `requirements.txt` - Test dependencies
- `pytest.ini` - Pytest configuration

## Test Categories

1. **Configuration Tests** - Test config loading and raster type detection
2. **Core Processing Tests** - Test raster reading and processing functions
3. **Thumbnail Generation Tests** - Test thumbnail creation
4. **Directory Processing Tests** - Test batch processing functionality
5. **Integration Tests** - End-to-end workflow tests

## Adding New Tests

When adding new functionality:

1. Add unit tests in `test_raster_thumbnail.py`
2. Add simple tests in `test_simple.py` for basic functionality
3. Follow the naming convention: `test_[function_name]_[scenario]`
4. Use descriptive test names and docstrings

## Test Data

Tests use temporary files and mock data to avoid requiring real raster files in the repository. This keeps the tests fast and the repository clean.

## CI/CD Integration

These tests are designed to run in continuous integration environments:

```yaml
# Example GitHub Actions step
- name: Run tests
  run: |
    pip install -r tests/requirements.txt
    pytest tests/ --cov=raster_thumbnail
```
