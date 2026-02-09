# Technology Stack

**Analysis Date:** 2026-02-09

## Languages

**Primary:**
- JavaScript/TypeScript - Frontend and backend application code
- Python 3.x - Data pipeline and database population scripts

**Secondary:**
- JSON - Configuration files

## Runtime

**Environment:**
- Node.js (version not specified in configuration)

**Package Manager:**
- npm
- Lockfile: `package-lock.json` present

## Frameworks

**Core:**
- React (implied from eslint-plugin-react configuration) - Frontend UI framework

**Testing:**
- Not configured - test script in `package.json` shows: `"test": "echo \"Error: no test specified\" && exit 1"`

**Build/Dev:**
- ESLint (v9.27.0) - Code linting
- Prettier (v3.5.3) - Code formatting
- TypeScript ESLint (v8.32.1) - TypeScript linting support

## Key Dependencies

**Dev Dependencies:**
- `@eslint/js` (^9.27.0) - ESLint JavaScript rules
- `eslint` (^9.27.0) - Linter for code quality
- `eslint-plugin-react` (^7.37.5) - React-specific ESLint rules
- `globals` (^16.1.0) - Global variable definitions for ESLint
- `prettier` (^3.5.3) - Code formatter
- `typescript-eslint` (^8.32.1) - TypeScript support for ESLint

**Production Dependencies:**
- No production dependencies currently specified in `package.json`

**Python Dependencies (Backend):**
- `requests` - HTTP client library for API calls
- `pandas` - Data manipulation and DataFrame operations
- `influxdb-client` - InfluxDB Python client for time-series data operations
- `python-dotenv` - Environment variable loading from `.env` files

## Configuration

**Environment:**
- Environment variables loaded via `python-dotenv` in backend scripts
- No TypeScript configuration file detected (no `tsconfig.json`)
- Configuration files present:
  - `.prettierrc` - Prettier formatting configuration
  - `eslint.config.mjs` - ESLint configuration using flat config format

**Build:**
- ESLint flat config file: `eslint.config.mjs`
- Prettier config: `.prettierrc` with settings:
  - Single quotes enabled
  - No semicolons
  - Trailing commas in ES5 format

## Platform Requirements

**Development:**
- Node.js with npm for JavaScript/TypeScript development
- Python 3.x with pip for backend scripts
- Git for version control

**Production:**
- Deployment target not yet determined
- Project references InfluxDB as time-series database backend
- Project references Alpha Vantage API for stock market data

## External Services Integration Points

**Market Data:**
- Alpha Vantage API - Provides historical stock price data

**Data Storage:**
- InfluxDB - Time-series database for stock market data storage

---

*Stack analysis: 2026-02-09*
