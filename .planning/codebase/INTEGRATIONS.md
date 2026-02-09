# External Integrations

**Analysis Date:** 2026-02-09

## APIs & External Services

**Market Data:**
- Alpha Vantage - Historical stock price data retrieval
  - SDK/Client: `requests` (Python HTTP library)
  - Auth: Environment variable `ALPHA_API_KEY`
  - Usage: `influx-populate-script.py` fetches daily OHLCV data for stock tickers via REST API
  - Endpoint: `https://www.alphavantage.co/query`
  - Rate limiting: 5-15 second delays between requests to respect API rate limits

## Data Storage

**Databases:**
- InfluxDB - Time-series database for market data
  - Connection: Environment variables:
    - `INFLUXDB_URL` (default: `http://localhost:8086`)
    - `INFLUXDB_TOKEN` (authentication token)
    - `INFLUXDB_ORG` (default: `finspeak`)
    - `INFLUXDB_BUCKET` (default: `market_data`)
  - Client: `influxdb-client` Python SDK
  - Usage: Stores daily OHLCV (Open, High, Low, Close, Volume) data for stock symbols with daily timeframe tags
  - Operations: Write with batch processing (500 points per batch), read with Flux queries, integrity verification

**File Storage:**
- Local filesystem only - No cloud file storage integration detected

**Caching:**
- None detected

## Authentication & Identity

**Auth Provider:**
- Custom API key authentication
  - Alpha Vantage API key passed as query parameter
  - InfluxDB token-based authentication via Bearer token

**User Authentication:**
- Not yet implemented - MVP scope focuses on core functionality

## Monitoring & Observability

**Error Tracking:**
- None detected - No Sentry, Rollbar, or similar integration

**Logs:**
- Python logging module with dual handlers:
  - File output: `influx_populate.log`
  - Console output (StreamHandler)
  - Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
  - Usage: Located in `backend/influx-populate-script.py`

## CI/CD & Deployment

**Hosting:**
- Not yet specified in configuration
- Development environment: Local machine

**CI Pipeline:**
- Not detected - No GitHub Actions, GitLab CI, or similar configuration files

## Environment Configuration

**Required Environment Variables:**
- `ALPHA_API_KEY` - Alpha Vantage API key for market data (critical)
- `INFLUXDB_TOKEN` - InfluxDB authentication token (critical)
- `INFLUXDB_URL` - InfluxDB server URL (optional, default: `http://localhost:8086`)
- `INFLUXDB_ORG` - InfluxDB organization name (optional, default: `finspeak`)
- `INFLUXDB_BUCKET` - InfluxDB bucket for market data (optional, default: `market_data`)

**Secrets Location:**
- Environment variables stored in `.env` file (loaded via `python-dotenv`)
- `.env` file location: Project root directory
- Note: `.env` file is not committed to version control (listed in `.gitignore`)

## Webhooks & Callbacks

**Incoming:**
- Not implemented

**Outgoing:**
- Not implemented

## Data Flow

**Population Flow:**
1. Backend script `influx-populate-script.py` executes on schedule or manually
2. Fetches historical stock data from Alpha Vantage API for configured tickers (AAPL, MSFT, GOOGL, NVDA)
3. Processes data with pandas DataFrames (cleaning, type conversion, sorting)
4. Writes data to InfluxDB in batches of 500 points
5. Implements retry logic (3 attempts, 5-second delays) for resilience
6. Verifies data integrity post-write with count and date range queries

**Query Flow:**
- InfluxDB Flux queries retrieve data with filtering:
  - By measurement: `stock_price`
  - By symbol tag
  - By time range (e.g., last 30 days, last 7 days)
  - By field (OHLCV values)
  - Pivot queries for DataFrame-friendly format

## Known Integration Limitations

**Alpha Vantage:**
- Free tier rate limits: 5 API calls per minute, 500 per day
- Implemented workarounds: 15-second delays between ticker requests
- Returns error/Note messages when rate limits exceeded - handled with logging and retry logic

**InfluxDB:**
- Connection timeout: 60 seconds for write operations, 30 seconds for read operations
- Bucket auto-creation implemented if not present
- Batch writes to prevent timeout on large datasets

---

*Integration audit: 2026-02-09*
