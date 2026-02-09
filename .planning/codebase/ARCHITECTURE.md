# Architecture

**Analysis Date:** 2026-02-09

## Pattern Overview

**Overall:** Monorepo with separate frontend and backend layers, currently in early-stage development with infrastructure setup phase complete. Data-driven financial analysis platform designed to integrate communication analysis with technical trading strategies.

**Key Characteristics:**
- Monorepo structure with frontend, backend, and shared code isolation
- Python backend for data ingestion and processing (batch/script-based)
- JavaScript/TypeScript frontend framework (React) for UI presentation
- Time-series database (InfluxDB) as primary data store
- External API integration (Alpha Vantage) for market data sourcing
- Modular separation of concerns with planned shared utilities layer

## Layers

**Frontend:**
- Purpose: User interface for displaying trading analysis, communication translation, and technical recommendations
- Location: `frontend/`
- Contains: React components, pages, styles, and frontend-specific business logic
- Depends on: Shared types/utilities, potentially API calls to backend
- Used by: End users accessing the trading analysis platform

**Backend Services:**
- Purpose: API endpoints, business logic, and data processing orchestration
- Location: `backend/`
- Contains: Express/Node.js API servers, route handlers, middleware, service layer
- Depends on: Shared types, InfluxDB, external APIs (Alpha Vantage, communication analysis APIs)
- Used by: Frontend application, data population scripts

**Data Pipeline/Scripting:**
- Purpose: Batch data ingestion and database population
- Location: `backend/influx-populate-script.py`
- Contains: ETL logic for market data sourcing and time-series database updates
- Depends on: Alpha Vantage API, InfluxDB client, pandas for data transformation
- Used by: DevOps/scheduled jobs during development and deployment phases

**Shared Layer:**
- Purpose: Common types, utilities, and interfaces used across frontend and backend
- Location: `shared/`
- Contains: TypeScript type definitions, validation schemas, utility functions
- Depends on: None (should be dependency-free)
- Used by: Both frontend and backend modules

## Data Flow

**Market Data Ingestion:**

1. Alpha Vantage API provides historical daily OHLCV (Open-High-Low-Close-Volume) data
2. `influx-populate-script.py` fetches time-series data via HTTP requests
3. Pandas DataFrames transform raw API response into normalized tabular format
4. Data validated for completeness and cleaned (column naming, type conversion)
5. InfluxDB batch writer stores normalized points using InfluxDB Point API
6. Retry logic with exponential backoff handles transient API/database failures

**Application Data Flow (Expected):**

1. Frontend requests analysis for a specific ticker/company
2. Backend API retrieves stored market data from InfluxDB
3. Backend fetches corporate communication/earnings data from external source
4. AI/NLP processing generates communication translation and risk analysis
5. Technical analysis engine calculates volume profiles and entry points
6. Backend aggregates results with RQI (Risk Quantification Index) calculations
7. Frontend renders unified view of communication analysis + technical recommendations

**State Management:**
- Market data: Immutable time-series records in InfluxDB (source of truth)
- Application state: Expected to be managed in React (frontend) with backend API as single source of truth
- Processing state: Python scripts use logging for state tracking during batch operations

## Key Abstractions

**Market Data Points:**
- Purpose: Represent OHLCV candle data with metadata
- Examples: `backend/influx-populate-script.py` lines 138-146
- Pattern: Point objects tagged with symbol/timeframe, fields for OHLCV, timestamp for ordering

**Data Transformation Pipelines:**
- Purpose: ETL abstraction for extracting, cleaning, and loading data
- Examples: `influx-populate-script.py` functions `get_stock_data()` and `store_in_influxdb()`
- Pattern: Functional pipelines with error handling, retry logic, and logging at each stage

**API Integration Pattern:**
- Purpose: Abstract external service calls (Alpha Vantage, InfluxDB)
- Examples: `backend/influx-populate-script.py` uses requests library for HTTP, InfluxDBClient for database
- Pattern: Client initialization with config, request/response handling, timeout management, error recovery

## Entry Points

**Development Environment Setup:**
- Location: Root `package.json` scripts, `eslint.config.mjs`
- Triggers: Developer running `npm install` or linting/formatting
- Responsibilities: Configure linting rules (ESLint), formatting rules (Prettier), dependency management

**Data Population Script:**
- Location: `backend/influx-populate-script.py`
- Triggers: Manual execution or scheduled job (intended for CI/CD pipeline)
- Responsibilities: Fetch stock data from Alpha Vantage, populate InfluxDB buckets, verify data integrity

**Frontend Application (Future):**
- Location: `frontend/` (to be implemented)
- Triggers: User navigation to application URL
- Responsibilities: Render UI, handle user interactions, request data from backend API

**Backend API Server (Future):**
- Location: `backend/` (to be implemented)
- Triggers: Server startup, HTTP requests from frontend or external clients
- Responsibilities: Route requests, process business logic, interface with InfluxDB and external APIs

## Error Handling

**Strategy:** Layered error handling with logging, graceful degradation, and retry mechanisms.

**Patterns:**
- Python Scripts: Try-catch blocks around API calls and database operations, logged errors with context
  - Example: `backend/influx-populate-script.py` lines 154-164 implement retry logic with delays
  - Failures logged but don't prevent processing of other tickers (graceful degradation)
- HTTP Requests: Timeout management (30-60 seconds), response validation before processing
  - Example: `backend/influx-populate-script.py` line 56 checks HTTP status, lines 59-65 validate response format
- Database Operations: Batch processing with partial success tracking
  - Example: `backend/influx-populate-script.py` lines 150-157 retry individual batches, track success count

## Cross-Cutting Concerns

**Logging:**
- Implementation: Python `logging` module in backend scripts
- Configuration: File + console output, INFO level by default
- Location: `influx_populate.log` for batch operations
- Pattern: Structured logging with timestamps, component names, and severity levels

**Validation:**
- Implementation: Response schema validation before processing (check for expected keys/format)
- Location: Data transformation functions in `backend/influx-populate-script.py`
- Pattern: Fail early with informative error messages, prevent corrupt data from entering system

**Configuration Management:**
- Implementation: Environment variables via `python-dotenv` in Python, expected `.env` file or similar for Node.js
- Pattern: External configuration for API keys, database URLs, credentials (never hardcoded except for dev defaults)

**Authentication:**
- Currently: API keys (Alpha Vantage, InfluxDB tokens) managed via environment variables
- Future: Expected to implement user authentication in frontend, service-to-service auth in backend APIs

---

*Architecture analysis: 2026-02-09*
