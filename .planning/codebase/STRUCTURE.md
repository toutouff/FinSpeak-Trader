# Codebase Structure

**Analysis Date:** 2026-02-09

## Directory Layout

```
FinSpeak_Trader_Project/
├── frontend/                          # React frontend application (empty, awaiting implementation)
├── backend/                           # Node.js/Express backend and Python utilities
│   └── influx-populate-script.py     # Data ingestion script for InfluxDB population
├── shared/                            # Shared code between frontend and backend (empty, planned)
├── .planning/                         # Documentation and planning artifacts
│   └── codebase/                      # Analysis documents (STACK.md, ARCHITECTURE.md, etc.)
├── .git/                              # Git repository metadata
├── package.json                       # Root npm configuration and dev dependencies
├── package-lock.json                  # Locked dependency versions for reproducibility
├── eslint.config.mjs                  # ESLint configuration (flat config format)
├── .prettierrc                        # Prettier code formatting rules
├── .gitignore                         # Git ignore patterns
├── README.md                          # Project overview and goals
└── STRUCTURE.md                       # High-level structure documentation (existing)
```

## Directory Purposes

**`frontend/`:**
- Purpose: React-based user interface for trading analysis platform
- Contains: React components, pages, hooks, styles, assets
- Status: Empty (planned), awaiting implementation
- Key files: (To be created)

**`backend/`:**
- Purpose: API server and data processing utilities
- Contains: Express API routes, middleware, service layer, data scripts
- Key files: `influx-populate-script.py` - Batch data ingestion from Alpha Vantage to InfluxDB

**`shared/`:**
- Purpose: Shared code between frontend and backend
- Contains: TypeScript types, interfaces, validation schemas, utility functions
- Status: Empty (planned), no shared code yet
- Guidelines: Keep dependency-free, use for types and utilities only

**`.planning/`:**
- Purpose: Project planning and analysis documents
- Contains: Codebase analysis (STACK.md, ARCHITECTURE.md, STRUCTURE.md, etc.)
- Key files: `.planning/codebase/` holds analysis documents consumed by other GSD commands

## Key File Locations

**Entry Points:**

- `package.json`: Root npm configuration - defines dev scripts, dependencies, project metadata
- `backend/influx-populate-script.py`: Data pipeline entry point - executable script for batch data ingestion
- `frontend/` (future): React application entry point (typically `index.tsx` or Next.js `page.tsx`)
- `backend/` (future): Express API server entry point (typically `index.ts`, `server.ts`, or `app.ts`)

**Configuration:**

- `eslint.config.mjs`: ESLint rules using flat config format, covers JS/TS/JSX/TSX files
- `.prettierrc`: Prettier formatting config (single quotes, no semicolons, ES5 trailing commas)
- `package.json`: Dev dependencies (ESLint, Prettier, TypeScript-ESLint)
- `.gitignore`: Version control exclusions
- `tsconfig.json` (missing): TypeScript configuration should be added before implementing TypeScript code

**Core Logic:**

- `backend/influx-populate-script.py`:
  - Lines 42-94: `get_stock_data()` - Fetch historical data from Alpha Vantage API
  - Lines 96-181: `store_in_influxdb()` - Write data to InfluxDB with batching and retry logic
  - Lines 183-225: `read_from_influxdb()` - Query stored market data
  - Lines 227-294: `verify_data_integrity()` - Validate data completeness
  - Lines 298-362: `main()` - Orchestration of data pipeline for multiple tickers

**Testing:**

- No test files present (test script in `package.json` shows "no test specified")
- Future test locations (recommended):
  - Frontend tests: `frontend/__tests__/` or `frontend/**/*.test.tsx`
  - Backend tests: `backend/__tests__/` or `backend/**/*.test.ts`

**Documentation:**

- `README.md`: Project overview, features, success metrics, MVP scope
- `STRUCTURE.md`: High-level directory layout (existing, minimal)
- `.planning/codebase/`: Detailed analysis documents (STACK.md, ARCHITECTURE.md, etc.)

## Naming Conventions

**Files:**

- Python scripts: snake_case with descriptive names (e.g., `influx-populate-script.py`)
- Configuration files: lowercase with hyphens or dots (e.g., `.prettierrc`, `eslint.config.mjs`)
- React components: PascalCase (e.g., `UserProfile.tsx`, `TradeAnalysis.tsx`)
- Utilities/services: camelCase (e.g., `dataTransform.ts`, `apiClient.ts`)

**Directories:**

- Monorepo top-level: lowercase plural nouns (e.g., `frontend`, `backend`, `shared`, `.planning`)
- Feature directories: lowercase descriptive names (e.g., `components`, `services`, `utils`, `pages`)
- Test directories: `__tests__` or co-located with source files as `*.test.ts`

**Code Style (Enforced):**

- No semicolons (Prettier default: `semi: false`)
- Single quotes for strings (Prettier default: `singleQuote: true`)
- Trailing commas in ES5 format (Prettier default: `trailingComma: "es5"`)
- ESLint rules: JavaScript recommended + React recommended + TypeScript recommended
- Languages: JavaScript/TypeScript for frontend and backend APIs, Python for data scripts

## Where to Add New Code

**New Frontend Feature:**

- Components: Create in `frontend/src/components/[FeatureName]/`
- Pages/Routes: Create in `frontend/src/pages/` (if Next.js) or within `frontend/src/`
- Tests: Co-locate with component as `[ComponentName].test.tsx`
- Styles: Co-locate CSS/SCSS with component or in `frontend/src/styles/`
- Types: Define in component file or in `shared/types/` if cross-module

**New Backend API Endpoint:**

- Route handlers: Create in `backend/src/routes/` (e.g., `backend/src/routes/analysis.ts`)
- Business logic: Implement in `backend/src/services/` (e.g., `backend/src/services/technicalAnalysis.ts`)
- Controllers: Create in `backend/src/controllers/` to bridge routes and services
- Tests: Create in `backend/__tests__/` with matching path structure
- Database queries: Implement in `backend/src/db/` or within service layer

**New Data Processing Script:**

- Location: `backend/scripts/` or `backend/` (top-level if critical/frequent use)
- Pattern: Follow `influx-populate-script.py` structure with logging, error handling, retry logic
- Naming: descriptive action + target (e.g., `populate-influx.py`, `fetch-earnings.py`)
- Configuration: Use environment variables for API keys, database URLs, credentials

**Shared Utilities/Types:**

- Types: `shared/types/` (e.g., `shared/types/market.ts`, `shared/types/analysis.ts`)
- Utilities: `shared/utils/` (e.g., `shared/utils/calculations.ts`, `shared/utils/formatting.ts`)
- Validation: `shared/validators/` or `shared/schemas/` (e.g., Zod, Joi schemas)
- Constants: `shared/constants/` (e.g., ticker lists, calculation constants)

## Special Directories

**`.planning/codebase/`:**
- Purpose: Stores analysis documents generated by GSD mapping and planning commands
- Generated: Yes (created by GSD agents)
- Committed: Yes (should be committed to git for team reference)
- Contents: STACK.md, ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, CONCERNS.md, INTEGRATIONS.md

**`node_modules/`:**
- Purpose: npm installed dependencies (should NOT be committed)
- Generated: Yes (by `npm install`)
- Committed: No (excluded via .gitignore)

**`.git/`:**
- Purpose: Git repository metadata and history
- Generated: Yes (by `git init` or clone)
- Committed: Not applicable (version control data)

## Repository Setup Notes

**Development Prerequisites:**

1. Node.js and npm installed (version check: `npm -v`)
2. Python 3.x installed (for backend data scripts)
3. `.env` file configured with:
   - `ALPHA_API_KEY`: Alpha Vantage API key
   - `INFLUXDB_URL`: InfluxDB server URL
   - `INFLUXDB_TOKEN`: InfluxDB authentication token
   - `INFLUXDB_ORG`: InfluxDB organization name
   - `INFLUXDB_BUCKET`: InfluxDB bucket name (default: "market_data")

**Installation Steps:**

1. Clone repository: `git clone <repo-url>`
2. Install npm dependencies: `npm install` (in project root)
3. Install Python dependencies: `pip install -r backend/requirements.txt` (when created)
4. Configure `.env` file with appropriate API keys and database URLs
5. Run ESLint/Prettier: `npm run lint` / `npm run format` (when scripts added)

**Monorepo Structure Benefits:**

- Shared types between frontend and backend reduce duplication
- Unified ESLint/Prettier configuration across all TypeScript code
- Single package-lock.json ensures consistent dependency versions
- Simplified CI/CD pipeline (one lint, one test suite)

---

*Structure analysis: 2026-02-09*
