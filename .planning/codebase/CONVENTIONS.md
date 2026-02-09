# Coding Conventions

**Analysis Date:** 2026-02-09

## Naming Patterns

**Files:**
- Python scripts: lowercase with hyphens (e.g., `influx-populate-script.py`)
- Config files: specific naming (`.prettierrc`, `eslint.config.mjs`)

**Functions:**
- Python: snake_case (e.g., `get_stock_data`, `store_in_influxdb`, `verify_data_integrity`)
- Follows PEP 8 conventions

**Variables:**
- Python: snake_case for all variables (e.g., `ALPHA_VANTAGE_API_KEY`, `INFLUXDB_URL`, `batch_size`)
- Constants: UPPERCASE with underscores (e.g., `ALPHA_VANTAGE_API_KEY`, `INFLUXDB_BUCKET`)
- Local variables: lowercase (e.g., `ticker`, `df`, `client`)

**Types:**
- Python: No type hints observed in current codebase
- TypeScript/JavaScript: To be defined when code is implemented

## Code Style

**Formatting:**
- Prettier: `^3.5.3`
- Config file: `.prettierrc`
- Settings:
  - Single quotes: enabled
  - Semicolons: disabled
  - Trailing commas: ES5 style

**Linting:**
- ESLint: `^9.27.0`
- Config file: `eslint.config.mjs`
- Configurations:
  - JavaScript/TypeScript: `@eslint/js` recommended
  - TypeScript: `typescript-eslint` recommended
  - React: `eslint-plugin-react` recommended
- Files checked: `**/*.{js,mjs,cjs,ts,jsx,tsx}`
- Browser globals enabled

## Import Organization

**Python pattern** (from `influx-populate-script.py`):
1. Standard library imports (`import requests`, `import os`, `import logging`)
2. Third-party library imports (`import pandas`, `import dotenv`, `from influxdb_client`)
3. Separated with blank lines between groups

**JavaScript/TypeScript pattern** (to be established):
- Path aliases: To be configured (not yet present)
- Barrel files: Not yet in use

## Error Handling

**Python patterns:**
- Try-except blocks for network operations (`requests.exceptions.RequestException`)
- Specific exception handling for different error types (`ValueError`, `KeyError`)
- Graceful degradation with `None` returns on error
- Error logging before returning error state

Example from `influx-populate-script.py`:
```python
try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "Time Series (Daily)" not in data:
        if "Error Message" in data:
            logger.error(f"Erreur Alpha Vantage: {data['Error Message']}")
        # ... handle various error states
        return None

except requests.exceptions.RequestException as e:
    logger.error(f"Erreur lors de la requête pour {ticker}: {e}")
    return None
except (ValueError, KeyError) as e:
    logger.error(f"Erreur lors du traitement des données pour {ticker}: {e}")
    return None
```

## Logging

**Framework:** Python `logging` module

**Configuration** (from `influx-populate-script.py`):
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("influx_populate.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("influx_populate")
```

**Patterns:**
- Logger named after module purpose: `logger = logging.getLogger("influx_populate")`
- Info level for process flow: `logger.info(f"Récupération des données pour {ticker}...")`
- Warning level for recoverable issues: `logger.warning(f"Le bucket {INFLUXDB_BUCKET} n'existe pas...")`
- Error level for failures: `logger.error(f"Erreur lors de la requête pour {ticker}: {e}")`
- Both file and console output via handlers
- F-strings for message formatting

**Logging locations in code:**
- `backend/influx-populate-script.py`: Lines 44, 61-65, 86, 90, 93, 102, 119-121, 133, 160-164, 175, 185, 220, etc.

## Comments

**When to Comment:**
- High-level section markers: `# --- CONFIGURATION ---`, `# --- FONCTIONS PRINCIPALES ---`, `# --- EXÉCUTION PRINCIPALE ---`
- Docstrings for functions: Used sparingly but present

Example from `backend/influx-populate-script.py` (line 42-43):
```python
def get_stock_data(ticker):
    """Fonction simple pour récupérer les données historiques d'un titre."""
```

**JSDoc/TSDoc:**
- Not yet in use (TypeScript implementation pending)

## Function Design

**Size:**
- Functions range from 10-50 lines for data retrieval/transformation
- Longer functions (70-100 lines) used for batched operations with retry logic

Example: `store_in_influxdb` function (lines 96-181) handles connection, batching, retries, and cleanup in one function.

**Parameters:**
- Clear parameter names: `get_stock_data(ticker)`, `store_in_influxdb(df, ticker, batch_size=500)`
- Default parameters used appropriately: `read_from_influxdb(ticker, start_time="-30d")`

**Return Values:**
- Functions return data directly (DataFrames, query results) or `None` on error
- Boolean returns for success/failure operations: `return success_count > 0`

## Module Design

**Exports:**
- Python: No explicit exports pattern yet (single entry point via `if __name__ == "__main__"`)

**Configuration as Globals:**
- All configuration loaded from environment at module level (lines 31-38)
- Ticker list as module constant: `TICKERS = ["AAPL", "MSFT", "GOOGL", "NVDA"]`

## Data Processing Patterns

**DataFrame manipulation:**
- Column renaming via comprehension: `df.columns = [col.split(". ")[1] for col in df.columns]`
- Type conversion in loop: `for col in df.columns: df[col] = pd.to_numeric(df[col])`
- Date sorting: `df = df.sort_values("date", ascending=False)`

---

*Convention analysis: 2026-02-09*
