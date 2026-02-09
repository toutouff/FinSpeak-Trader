# Testing Patterns

**Analysis Date:** 2026-02-09

## Test Framework

**Status:** Not yet implemented

**Configured but not in use:**
- ESLint: `^9.27.0` (for code quality checks)
- Test script in `package.json` (line 7): currently returns error placeholder
  ```
  "test": "echo \"Error: no test specified\" && exit 1"
  ```

**Runner:**
- Not detected (Jest, Vitest, or pytest not yet configured)
- `package.json` has no test dependencies installed

**Assertion Library:**
- Not detected in current setup

**Run Commands:**
```bash
npm test              # Currently returns error - no tests defined
```

## Test File Organization

**Current State:**
- No test files found in codebase
- No test directories established
- Backend contains only `backend/influx-populate-script.py` (production code)
- `frontend/` and `shared/` directories are empty (contain only `.gitkeep` files)

**Recommended Structure (when tests are added):**
- Python tests: `backend/tests/` or `backend/test_*.py` alongside modules
- JavaScript/TypeScript tests: `frontend/__tests__/` or `frontend/*.test.tsx`

## Test Structure

**Python Testing Pattern Needed:**
When Python tests are implemented, use pytest or unittest. Recommended structure:
```python
import pytest
from backend.influx_populate_script import get_stock_data, store_in_influxdb

class TestDataRetrieval:
    def test_get_stock_data_valid_ticker(self):
        # Test implementation
        pass

    def test_get_stock_data_invalid_api_key(self):
        # Test implementation
        pass
```

**JavaScript/TypeScript Pattern Needed:**
When frontend tests are implemented:
```typescript
import { render, screen } from '@testing-library/react'
import { MyComponent } from './MyComponent'

describe('MyComponent', () => {
  test('renders correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('expected')).toBeInTheDocument()
  })
})
```

## Mocking

**Framework:** Not yet selected

**Patterns:** Not yet established

**What to Mock (when implemented):**
- External API calls (Alpha Vantage API in `get_stock_data`)
- InfluxDB connections (in `store_in_influxdb`, `read_from_influxdb`)
- File I/O operations (logging to `influx_populate.log`)
- Environment variables for configuration

**What NOT to Mock:**
- Pure data transformation logic (DataFrame operations)
- Validation logic
- Logging framework itself (may stub output capture instead)

## Fixtures and Factories

**Test Data:** Not yet established

**Recommended approach for Python** (from `backend/influx-populate-script.py` context):
```python
@pytest.fixture
def sample_stock_data():
    """Mock DataFrame matching Alpha Vantage structure"""
    return pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=5),
        'open': [100.0, 101.0, 102.0, 103.0, 104.0],
        'high': [102.0, 103.0, 104.0, 105.0, 106.0],
        'low': [99.0, 100.0, 101.0, 102.0, 103.0],
        'close': [101.0, 102.0, 103.0, 104.0, 105.0],
        'volume': [1000000, 1100000, 1200000, 1300000, 1400000]
    })
```

**Location:**
- Should be in `backend/tests/conftest.py` (pytest convention)
- Or in `backend/tests/fixtures/` subdirectory

## Coverage

**Requirements:** Not enforced

**View Coverage:** No coverage tool configured yet

**Recommended setup:**
```bash
# For Python
pip install pytest-cov
pytest --cov=backend backend/tests/

# For JavaScript/TypeScript
npm install --save-dev @vitest/ui
npm test -- --coverage
```

## Test Types

**Unit Tests:** Not yet implemented
- Should test individual functions: `get_stock_data()`, `store_in_influxdb()`, `verify_data_integrity()`
- Mock external dependencies (API calls, database connections)
- Test error handling paths (invalid API response, timeout, network error)

**Integration Tests:** Not yet implemented
- Would test interaction between components
- Example: Test full flow from API fetch → DataFrame transformation → InfluxDB write
- Requires real or stubbed InfluxDB instance

**E2E Tests:** Not yet implemented
- Could test complete workflow with real external services (recommended only in CI environment with test credentials)
- Not recommended for local development due to API rate limits and external service dependency

## Data Processing Tests (Python-specific)

When testing `backend/influx-populate-script.py`, focus areas:

**Alpha Vantage API response handling** (lines 42-94):
- Test parsing of valid time series data
- Test handling of error messages (`"Error Message"` in response)
- Test handling of API rate limit notes (`"Note"` in response)
- Test handling of unexpected response formats

**DataFrame transformations** (lines 69-84):
- Test column name cleaning: `df.columns = [col.split(". ")[1] for col in df.columns]`
- Test numeric type conversion for OHLCV data
- Test date parsing and sorting
- Test handling of empty DataFrames

**InfluxDB batch writing** (lines 126-168):
- Test batch size splitting logic
- Test retry mechanism (currently 3 retries with 5-second delay)
- Test Point object creation with proper tags and fields
- Test success counting across batches
- Test proper client closure on both success and error

**Data integrity verification** (lines 227-294):
- Test count query execution
- Test date range validation
- Test handling of empty result sets
- Test logging of data statistics

## Async Testing

**Not yet applicable** (Python script is synchronous)

When frontend is implemented with async operations, use:
```typescript
// Vitest/Jest async pattern
test('async operation completes', async () => {
  const result = await asyncFunction()
  expect(result).toBeDefined()
})
```

## Error Testing

**Current Python error paths** (from `influx-populate-script.py`):

Should test the following error conditions:
- Missing environment variables (lines 302-308)
- Network timeouts (line 55, timeout=30)
- Invalid API responses (lines 59-66)
- InfluxDB connection failures (lines 316-327)
- Batch write failures with retry logic (lines 153-164)

Example test structure:
```python
def test_store_in_influxdb_retries_on_failure(mocker):
    # Mock the write API to fail twice, succeed on third attempt
    write_mock = mocker.Mock()
    write_mock.side_effect = [Exception("Connection error"), Exception("Timeout"), None]

    # Verify retry behavior and eventual success
    assert store_in_influxdb(sample_data, "AAPL") == True
```

---

*Testing analysis: 2026-02-09*
