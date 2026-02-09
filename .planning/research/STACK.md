# Stack Research

**Domain:** Financial analysis platform with NLP-powered corporate communication analysis
**Researched:** 2026-02-09
**Confidence:** MEDIUM-HIGH (most versions verified via official sources; a few via WebSearch only)

---

## Recommended Stack

### Backend — Core Framework

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| FastAPI | ^0.128.5 | REST API framework | Already decided. Python-native reuses existing pandas/influxdb pipeline code. Async-first, automatic OpenAPI docs, Pydantic validation built-in. Fastest Python web framework by benchmarks. | HIGH |
| Uvicorn | ^0.40.0 | ASGI server | Standard production server for FastAPI. Built on uvloop for high concurrency. Installed automatically with `pip install "fastapi[standard]"`. | HIGH |
| Pydantic | ^2.12.5 | Data validation & serialization | Ships with FastAPI. V2 uses Rust core (pydantic-core) for 5-50x speedup over V1. Defines all API request/response schemas. Do NOT use Pydantic V1 — it is deprecated in FastAPI. | HIGH |
| Python | >=3.11, <3.14 | Runtime | 3.11+ for performance gains (10-60% faster than 3.10). Avoid 3.14 — too new, some dependencies lack support. Existing script uses 3.x already. | HIGH |

### Backend — Data & Computation

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| pandas | ^2.2.x (or 3.0.0 if stable) | DataFrame operations | Already in use for OHLCV data. Standard for financial data manipulation. Volume profile calculations will use pandas groupby + numpy histograms. Pin to 2.2.x unless 3.0.0 is confirmed stable with all dependencies. | MEDIUM |
| numpy | ^2.4.2 | Numerical computation | Required by pandas. Volume profile histograms, support/resistance clustering, statistical calculations for RQI scoring all use numpy. | HIGH |
| scipy | ^1.17.0 | Scientific algorithms | Signal processing for peak detection (support/resistance via `scipy.signal.argrelextrema`). KDE (kernel density estimation) for volume profile smoothing. AgglomerativeClustering alternative lives here. | MEDIUM |
| scikit-learn | ^1.6.x | Clustering algorithms | `sklearn.cluster.AgglomerativeClustering` for grouping price levels into support/resistance zones. KMeans for price level clustering. Not a heavy dependency — only the cluster module is needed. | MEDIUM |
| influxdb-client | ^1.46.0 | InfluxDB 2.x client | Already in use. Provides Flux query API, batch writes, DataFrame integration. Pin the version — this library is in maintenance mode (last release May 2025). | HIGH |
| httpx | ^0.28.1 | Async HTTP client | Replace `requests` for async API calls to Alpha Vantage and FMP. Native async/await, HTTP/2 support, connection pooling. FastAPI's recommended HTTP client. Do NOT use `requests` in async FastAPI routes — it blocks the event loop. | HIGH |

### Backend — LLM Integration

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| ollama (Python) | ^0.4.x | Ollama REST client | Official Python SDK. Simple `ollama.chat()` / `ollama.generate()` API. Handles streaming, model management. Lighter than LangChain for a direct Ollama integration. | MEDIUM |
| Ollama (server) | latest | Local LLM inference server | Already decided. Runs models locally, zero API cost. REST API on localhost:11434. | HIGH |
| Llama 3.1 8B Instruct | — | Corporate text analysis model | Outperforms Mistral 7B on MMLU (66.7% vs 60.1%). 128K context window handles full earnings transcripts (vs 32K for Mistral). Better multilingual support. Best accuracy/speed ratio for 8B class. Pull via `ollama pull llama3.1:8b-instruct-q4_K_M` (quantized, ~5GB). | MEDIUM |

**Do NOT use LangChain** unless you need chains/agents/RAG later. For this MVP, direct `ollama.generate()` calls with prompt templates are simpler, faster to implement, and easier to debug. LangChain adds significant abstraction overhead for what is essentially: send prompt, get response.

**Fallback model:** If Llama 3.1 8B is too slow on available hardware, use `mistral:7b-instruct-q4_K_M` (~4.4GB). Faster inference, lower accuracy. Test both during setup.

### Backend — Corporate Data

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| Financial Modeling Prep API | free tier | Earnings transcripts, financial news, company data | Free tier: 250 requests/day. Provides earnings call transcripts, press releases, stock news, financial statements. Sufficient for hackathon (single ticker demo). REST API with JSON responses. Sign up at financialmodelingprep.com. | HIGH |
| edgartools | ^5.13.0 | SEC EDGAR filings (backup) | Free, no API key needed (uses SEC public API). Parses 10-K, 10-Q, 8-K filings. Use as backup/supplement if FMP free tier is too limited. MIT licensed. | MEDIUM |

**Why FMP over SEC EDGAR as primary:** FMP provides pre-formatted earnings transcripts (plain text, structured JSON). SEC EDGAR requires parsing HTML/XBRL filings — significantly more complex for a 1-week hackathon. FMP also provides news and press releases that EDGAR does not.

**Why NOT Alpha Vantage for corporate data:** Alpha Vantage free tier is already being used for OHLCV (5 calls/min, 500/day). Using the same key for corporate data would exhaust the rate limit. Keep market data and corporate data on separate APIs.

### Backend — Sentiment Analysis (Supplementary)

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| vaderSentiment | ^3.3.2 | Rule-based sentiment scoring | Fast, no model loading. Use as a quick pre-filter before LLM analysis. 63.3% accuracy on financial text (vs TextBlob's 41.3%). Good for scoring news headlines where LLM is overkill. Supplements Ollama analysis, not replaces it. | MEDIUM |

**Strategy:** Use VADER for quick sentiment polarity on news headlines (fast, batch-friendly). Use Ollama/Llama for deep analysis of earnings transcripts (nuanced, context-aware). Combine both scores into the RQI sentiment component.

### Frontend — Core

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| React | ^19.x | UI framework | Already decided. Component model, massive ecosystem, good for data-heavy dashboards. v19 is stable as of early 2026. | HIGH |
| Vite | ^7.3.1 | Build tool & dev server | Already decided. Sub-300ms dev server start, native ESM, HMR. CRA is officially deprecated. Requires Node.js 20.19+ or 22.12+. | HIGH |
| TypeScript | ^5.7.x | Type safety | ESLint TypeScript plugin already configured. Add `tsconfig.json` (currently missing). Non-negotiable for a project with complex data types (OHLCV, RQI scores, analysis results). | HIGH |
| React Router | ^7.12.0 | Client-side routing | v7 merges React Router + Remix. Import everything from `"react-router"` (no more `react-router-dom`). Needed for multi-page layout (dashboard, analysis detail, settings). | HIGH |

### Frontend — State Management & Data Fetching

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| @tanstack/react-query | ^5.90.x | Server state management | Handles caching, background refetching, loading/error states for all FastAPI calls. Eliminates 80% of manual state management. Essential for financial data that updates. | HIGH |
| zustand | ^5.0.11 | Client state management | ~1KB gzipped. Selective subscriptions minimize re-renders (critical for chart-heavy dashboards). Use for UI state: selected ticker, active timeframe, chart settings, sidebar state. Do NOT put server data here — that goes in TanStack Query. | HIGH |

**Do NOT use Redux.** Zustand + TanStack Query covers the same ground with less boilerplate, smaller bundle, and better DX. Redux is overkill for this scope.

### Frontend — Charting

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| lightweight-charts | ^5.1.0 | Financial charting (candlestick, volume) | Already decided. 45KB bundle, HTML5 canvas, TradingView-quality rendering. Supports candlestick series, volume histogram, line series (for support/resistance overlays). | HIGH |

**Do NOT use a React wrapper library** (kaktana-react-lightweight-charts, etc.). They are all unmaintained (last update 5+ years ago) and lag behind the v5 API. Instead, follow TradingView's official React integration tutorial — wrap the imperative API in a custom React hook/component. This is ~50 lines of code and gives you full control.

**Volume profile overlay:** Lightweight Charts does not have a built-in volume profile. Implement as a custom series or overlay using the histogram series type rotated/positioned at price levels. The calculation happens in the backend (numpy); the frontend just renders the pre-computed levels.

### Frontend — Styling

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| Tailwind CSS | ^4.1.18 | Utility-first CSS framework | v4 Oxide engine: 5x faster full builds, 100x faster incremental. Setup is just `@import "tailwindcss"` — zero config file needed. Perfect for rapid prototyping in a hackathon. Modern fintech look (Robinhood/Revolut style) is achievable with utilities alone. | HIGH |

**Do NOT use a component library** (MUI, Ant Design, Chakra). They add massive bundle weight, fight with Tailwind, and impose design constraints that conflict with the custom fintech aesthetic. For a 1-week hackathon with a specific design vision, raw Tailwind is faster.

### Frontend — HTTP Client

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| Native fetch API | built-in | HTTP requests to FastAPI | Zero bundle cost. TanStack Query wraps fetch calls anyway. Axios adds 11.7KB for features you won't use (interceptors, request cancellation — TanStack Query handles these). | HIGH |

**Do NOT use Axios.** With TanStack Query managing caching, retries, and error states, Axios provides no meaningful benefit over native fetch. Save the 11.7KB.

### Development Tools

| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| ESLint | ^9.27.0 (existing) | JS/TS linting | Already configured with flat config. Add React hooks plugin. |
| Prettier | ^3.5.3 (existing) | Code formatting | Already configured (single quotes, no semicolons, trailing commas ES5). |
| typescript-eslint | ^8.32.1 (existing) | TypeScript linting | Already installed. Needs tsconfig.json to function properly. |
| pytest | ^8.x | Python testing | Standard Python test framework. Use for backend API tests + analysis logic tests. |
| ruff | ^0.9.x | Python linting + formatting | Replaces flake8 + black + isort. Written in Rust, 10-100x faster. Single tool for all Python code quality. |

### Infrastructure

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| InfluxDB | 2.x (existing) | Time-series database | Already running, already populated with OHLCV data. Keep using for market data. Do NOT add another database for the hackathon. | HIGH |
| Docker Compose | latest | Local development orchestration | Run InfluxDB + Ollama + FastAPI in containers. Single `docker compose up` for the entire backend. Essential for reproducible setup. | MEDIUM |
| Node.js | >=20.19 or >=22.12 | Frontend runtime | Required by Vite 7.x. Use LTS version (22.x recommended). | HIGH |

---

## Installation

### Backend (Python)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Core
pip install "fastapi[standard]" pydantic uvicorn

# Data & computation
pip install pandas numpy scipy scikit-learn influxdb-client httpx

# LLM integration
pip install ollama

# Corporate data
pip install edgartools

# Sentiment
pip install vaderSentiment

# Dev tools
pip install pytest ruff python-dotenv

# Freeze
pip freeze > requirements.txt
```

### Frontend (npm)

```bash
# Scaffold (from project root)
npm create vite@latest frontend -- --template react-ts

# Navigate and install
cd frontend
npm install

# Core dependencies
npm install lightweight-charts @tanstack/react-query zustand react-router

# Styling
npm install -D tailwindcss @tailwindcss/vite

# Dev dependencies (move from root package.json)
npm install -D @types/react @types/react-dom typescript
```

### Ollama Model

```bash
# Pull recommended model (quantized, ~5GB)
ollama pull llama3.1:8b-instruct-q4_K_M

# Fallback if hardware is limited
ollama pull mistral:7b-instruct-q4_K_M

# Test
ollama run llama3.1:8b-instruct-q4_K_M "Summarize this in plain English: Revenue increased 15% YoY driven by strong cloud adoption"
```

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not Alternative |
|----------|-------------|-------------|---------------------|
| Python web framework | FastAPI | Django REST | Django is heavier, synchronous by default, ORM-centric. FastAPI's async + Pydantic is better for API-only backend with external data sources. |
| Python web framework | FastAPI | Flask | Flask lacks built-in validation, OpenAPI generation, async support. FastAPI provides all three out of the box. |
| LLM integration | ollama (direct) | LangChain | LangChain adds abstraction layers (chains, agents, memory) not needed for simple prompt-in/text-out. Adds ~50MB of dependencies. Use only if adding RAG or multi-step reasoning later. |
| LLM model | Llama 3.1 8B | Mistral 7B | Llama 3.1 scores higher on MMLU (66.7 vs 60.1), has 4x context window (128K vs 32K). Mistral is faster inference — keep as fallback. |
| LLM model | Llama 3.1 8B | Finance-Llama-8B | Finance-specific fine-tune, but less tested, smaller community, may hallucinate on general tasks. Test against base Llama 3.1 before committing. |
| Corporate data API | FMP (free) | SEC EDGAR (direct) | EDGAR requires HTML/XBRL parsing. FMP provides structured JSON. For a hackathon, structured > raw. |
| Corporate data API | FMP (free) | Alpha Vantage News | Would share rate limit with existing OHLCV pipeline (500 calls/day total). Keep APIs separate. |
| State management | Zustand + TanStack Query | Redux Toolkit | Redux adds boilerplate (slices, reducers, selectors). Zustand achieves same with ~1/5 the code. RTK Query overlaps with TanStack Query. |
| State management | Zustand | Jotai | Both are excellent. Zustand's store pattern is more familiar for this use case (dashboard with related state). Jotai's atomic model is better for deeply nested, independent state atoms. |
| CSS | Tailwind v4 | CSS Modules | Tailwind is faster for prototyping (no switching files). v4's zero-config setup removes the main objection. |
| CSS | Tailwind v4 | MUI / Ant Design | Component libraries impose design language. The spec calls for custom Robinhood/Revolut aesthetic — component libs fight this. |
| Charts | Lightweight Charts | Recharts | Recharts is general-purpose. Lightweight Charts is purpose-built for financial data (candlestick, OHLCV, crosshair). 45KB vs 200KB+. |
| Charts | Lightweight Charts | D3.js | D3 is low-level — building candlestick charts from scratch takes days. Lightweight Charts provides financial primitives. |
| HTTP client (Python) | httpx | requests | `requests` is synchronous — blocks FastAPI's async event loop. httpx supports async natively and has the same API surface. |
| HTTP client (Frontend) | Native fetch | Axios | TanStack Query handles retries, caching, cancellation. Axios's value-adds become redundant. Save 11.7KB. |
| Python test framework | pytest | unittest | pytest has cleaner syntax, fixtures, parametrize. De facto standard in 2026. |
| Python linter | ruff | flake8 + black | ruff replaces both in a single tool, 10-100x faster (Rust). One config, one command. |
| Build tool | Vite | Webpack | Webpack is legacy for new projects. Vite starts in <300ms, HMR is near-instant. CRA (Webpack) is officially deprecated. |
| Sentiment | VADER + Ollama | TextBlob | VADER has 63.3% vs TextBlob's 41.3% accuracy on financial text. TextBlob's sentiment model is too generic for financial language. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| LangChain (for MVP) | Massive dependency tree (~50MB), abstraction overhead for simple prompt/response. Debugging through chain abstractions wastes hackathon time. | Direct `ollama.generate()` with f-string prompt templates |
| requests (in async code) | Blocks the FastAPI async event loop. A single slow API call blocks ALL concurrent requests. | httpx (async client) |
| Pydantic V1 | Deprecated in FastAPI, no longer maintained, missing Rust-based performance gains. | Pydantic V2 (^2.12.5) |
| Create React App (CRA) | Officially deprecated Feb 2025. Webpack-based, slow builds, no HMR. | Vite (^7.3.1) |
| Redux / Redux Toolkit | Excessive boilerplate for this scope. 3 files per feature (slice, selectors, thunks) vs Zustand's 1. | Zustand + TanStack Query |
| Axios | TanStack Query handles everything Axios adds over fetch. 11.7KB wasted. | Native fetch API |
| MUI / Ant Design / Chakra | Fights custom design vision, massive bundle (MUI tree-shaken is still 80KB+), themes are hard to customize to match fintech aesthetic. | Tailwind CSS v4 |
| React wrapper libs for Lightweight Charts | All unmaintained (last updates 2019-2021), incompatible with v5 API, add bugs not features. | Custom React hook wrapping imperative API (~50 lines) |
| TA-Lib (C library) | Requires C compilation, platform-specific binary builds, Windows installation is painful. | numpy + scipy + custom Python for volume profile and S/R calculations |
| pandas-ta | Original repo removed from GitHub (author deleted it). Forks exist but are community-maintained with uncertain future. | numpy + scipy directly, or ta library (bukosabino/ta) as lightweight alternative |

---

## Stack Patterns by Variant

**If Llama 3.1 8B is too slow on available hardware:**
- Use `mistral:7b-instruct-q4_K_M` (~4.4GB, faster inference)
- Or use `llama3.1:8b-instruct-q4_0` (smaller quantization, ~4GB, faster but lower quality)
- Because: Local hardware varies. 4-bit quantized Mistral runs on 8GB RAM machines.

**If FMP free tier (250 req/day) is exhausted during development:**
- Cache all FMP responses to local JSON files after first fetch
- Use edgartools for SEC filing data as supplement
- Because: 250/day is enough for demo but not for iterative development. Cache aggressively.

**If volume profile needs real-time updates (post-hackathon):**
- Move calculation from backend to WebSocket stream
- Use InfluxDB continuous queries for pre-aggregation
- Because: MVP computes on request (acceptable latency). Real-time requires push architecture.

**If the frontend needs server-side rendering (post-hackathon):**
- React Router v7 supports SSR via its Remix-inherited capabilities
- Because: Not needed for hackathon demo (local SPA is fine), but the migration path exists.

---

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| FastAPI ^0.128.5 | Pydantic ^2.12.5 | FastAPI now requires Pydantic V2. V1 support deprecated. |
| FastAPI ^0.128.5 | Starlette >=0.40.0, <1.0.0 | Auto-installed. Do not pin separately. |
| FastAPI ^0.128.5 | Python >=3.9 | We target >=3.11 for performance. |
| Vite ^7.3.1 | Node.js >=20.19 or >=22.12 | Node 18 is NOT supported by Vite 7. |
| React ^19.x | React Router ^7.12.0 | v7 requires React 18+ (19 is fine). |
| @tanstack/react-query ^5.x | React ^18 or ^19 | Uses useSyncExternalStore (React 18+). |
| Tailwind ^4.1.18 | Vite ^7.x | Use `@tailwindcss/vite` plugin. No `tailwind.config.js` needed in v4. |
| lightweight-charts ^5.1.0 | Any modern browser | Pure canvas, no React dependency. Wrap manually. |
| pandas ^2.2.x | numpy ^2.4.x | Check compatibility if jumping to pandas 3.0.0. |
| influxdb-client ^1.46.0 | InfluxDB 2.x | Library is in maintenance mode. Works but no new features expected. |
| ollama (Python) ^0.4.x | Ollama server latest | Client auto-discovers localhost:11434. |

---

## Sources

- [FastAPI PyPI](https://pypi.org/project/fastapi/) — Version 0.128.5 confirmed (HIGH)
- [FastAPI Release Notes](https://fastapi.tiangolo.com/release-notes/) — Pydantic V1 deprecation, Starlette version range (HIGH)
- [Vite Releases](https://vite.dev/releases) — Version 7.3.1 confirmed, Node.js requirements (HIGH)
- [Vite 8 Beta Announcement](https://vite.dev/blog/announcing-vite8-beta) — v8 beta exists but not recommended for production (MEDIUM)
- [lightweight-charts npm](https://www.npmjs.com/package/lightweight-charts) — Version 5.1.0 confirmed (HIGH)
- [lightweight-charts GitHub](https://github.com/tradingview/lightweight-charts) — React integration tutorials (HIGH)
- [TanStack Query npm](https://www.npmjs.com/package/@tanstack/react-query) — Version 5.90.20 confirmed (HIGH)
- [Zustand npm](https://www.npmjs.com/package/zustand) — Version 5.0.11 confirmed (HIGH)
- [React Router npm](https://www.npmjs.com/package/react-router) — Version 7.12.0 confirmed (HIGH)
- [Tailwind CSS Releases](https://github.com/tailwindlabs/tailwindcss/releases) — Version 4.1.18 confirmed (HIGH)
- [Ollama Python PyPI](https://pypi.org/project/ollama/) — Python client available (MEDIUM)
- [Pydantic PyPI](https://pypi.org/project/pydantic/) — Version 2.12.5 confirmed (HIGH)
- [httpx PyPI](https://pypi.org/project/httpx/) — Version 0.28.1 confirmed (HIGH)
- [edgartools PyPI](https://pypi.org/project/edgartools/) — Version 5.13.0 confirmed (MEDIUM)
- [Financial Modeling Prep](https://site.financialmodelingprep.com/developer/docs) — Free tier 250 req/day (HIGH)
- [FMP Pricing](https://site.financialmodelingprep.com/pricing-plans) — Free tier details (HIGH)
- [NumPy News](https://numpy.org/news/) — Version 2.4.2, Feb 2026 (HIGH)
- [SciPy](https://scipy.org/) — Version 1.17.0, Jan 2026 (HIGH)
- [pandas PyPI](https://pypi.org/project/pandas/) — Version 2.2.x / 3.0.0 (MEDIUM)
- [influxdb-client PyPI](https://pypi.org/project/influxdb-client/) — Last release May 2025, maintenance mode (HIGH)
- [Llama 3.1 8B vs Mistral 7B comparison](https://www.prompthackers.co/compare/llama-3.1-8b/mistral-7b) — MMLU benchmarks, context window (MEDIUM)
- [Finance-Llama-8B](https://ollama.com/martain7r/finance-llama-8b) — Finance-specific model option (LOW)
- [Volume Profile in Python](https://letian-wang.medium.com/market-profile-and-volume-profile-in-python-139cb636ece) — Implementation patterns (MEDIUM)
- [Support/Resistance Algorithms](https://medium.com/@crisvelasquez/algorithmically-identifying-stock-price-support-resistance-in-python-b9095f9aa279) — Clustering approaches (MEDIUM)
- [VADER vs TextBlob Financial Text](https://www.analyticsvidhya.com/blog/2021/01/sentiment-analysis-vader-or-textblob/) — Accuracy comparison 63.3% vs 41.3% (MEDIUM)
- [React State Management 2025](https://www.developerway.com/posts/react-state-management-2025) — Zustand + TanStack Query pattern (MEDIUM)
- [Best Local LLMs 2026](https://iproyal.com/blog/best-local-llms/) — Model comparison (MEDIUM)

---
*Stack research for: FinSpeak Trader — financial analysis platform with NLP corporate communication analysis*
*Researched: 2026-02-09*
