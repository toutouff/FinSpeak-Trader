# Architecture Research

**Domain:** Financial analysis platform combining NLP corporate text analysis with technical trading indicators
**Researched:** 2026-02-09
**Confidence:** MEDIUM-HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  React + Vite Frontend                                        │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │ │
│  │  │ Chart Panel  │  │ Translation  │  │  RQI + Entry Panel   │ │ │
│  │  │ (Lightweight │  │    Panel     │  │  (Score + Tiers)     │ │ │
│  │  │   Charts)    │  │  (Plain Eng) │  │                      │ │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘ │ │
│  └─────────┼─────────────────┼──────────────────────┼────────────┘ │
│            │    HTTP / REST   │                      │              │
├────────────┴─────────────────┴──────────────────────┴──────────────┤
│                      API GATEWAY LAYER                              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  FastAPI Backend                                               │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │ │
│  │  │ /market-data │  │  /translate  │  │     /analysis        │ │ │
│  │  │   router     │  │    router    │  │      router          │ │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘ │ │
│  └─────────┼─────────────────┼──────────────────────┼────────────┘ │
├────────────┴─────────────────┴──────────────────────┴──────────────┤
│                     SERVICES LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Market Data  │  │  NLP/LLM     │  │  Analysis Engine         │  │
│  │  Service     │  │  Service     │  │  (VP + RQI + Entries)    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────────┘  │
│         │                 │                      │                  │
├─────────┴─────────────────┴──────────────────────┴──────────────────┤
│                   DATA / INTEGRATION LAYER                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ InfluxDB │  │  Ollama   │  │  Alpha   │  │  FMP / SEC       │   │
│  │ (OHLCV)  │  │  (Local   │  │ Vantage  │  │  Edgar           │   │
│  │          │  │   LLM)    │  │  (Prices)│  │  (Earnings/News) │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **React Frontend** | Render dashboard UI, display charts, show translations, present RQI scores and entry recommendations | React + Vite, Lightweight Charts for price visualization, component-per-panel layout |
| **FastAPI Backend** | Expose REST endpoints, orchestrate data retrieval and analysis, aggregate results | FastAPI with routers per domain, Pydantic models for request/response validation |
| **Market Data Service** | Query InfluxDB for OHLCV data, format for charting and analysis consumption | Python service wrapping InfluxDB client, Flux queries, pandas DataFrame transforms |
| **NLP/LLM Service** | Send corporate text to Ollama, parse structured sentiment + translation output | HTTP client to Ollama REST API, prompt engineering for financial text, response parsing |
| **Analysis Engine** | Compute Volume Profile, calculate RQI with dynamic weighting, generate multi-tier entry points | numpy/pandas calculations, convergence detection across multiple technical methods |
| **Data Ingestion Pipeline** | Populate InfluxDB from Alpha Vantage, fetch corporate text from FMP/SEC Edgar | Existing Python script (extended), new corporate data fetcher |

## Recommended Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app creation, CORS, router includes
│   ├── config.py               # Settings via pydantic-settings (env vars)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── market_data.py      # GET /api/market-data/{ticker}
│   │   ├── translate.py        # POST /api/translate (corporate text → plain English)
│   │   └── analysis.py         # GET /api/analysis/{ticker} (VP + RQI + entries)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── influx_service.py   # InfluxDB read operations (queries, formatting)
│   │   ├── ollama_service.py   # Ollama HTTP client (prompt, parse response)
│   │   ├── corporate_data.py   # FMP/SEC Edgar API fetcher
│   │   ├── volume_profile.py   # Volume Profile calculation engine
│   │   ├── rqi.py              # Risk Quantification Index (dynamic weighting)
│   │   └── entry_builder.py    # Multi-tier DCA entry point generator
│   ├── models/
│   │   ├── __init__.py
│   │   ├── market.py           # Pydantic models for OHLCV data
│   │   ├── translation.py      # Pydantic models for LLM translation output
│   │   └── analysis.py         # Pydantic models for VP, RQI, entry results
│   └── utils/
│       ├── __init__.py
│       └── calculations.py     # Shared math utilities (convergence detection, etc.)
├── scripts/
│   └── influx-populate-script.py  # Existing data population (moved here)
├── requirements.txt
└── .env

frontend/
├── src/
│   ├── main.tsx                # Vite entry point
│   ├── App.tsx                 # Layout + routing shell
│   ├── api/
│   │   └── client.ts           # Fetch wrapper for FastAPI endpoints
│   ├── components/
│   │   ├── Chart/
│   │   │   ├── PriceChart.tsx          # Lightweight Charts candlestick
│   │   │   └── VolumeProfileOverlay.tsx # VP visualization on chart
│   │   ├── Translation/
│   │   │   ├── TranslationPanel.tsx     # Plain English translation display
│   │   │   └── SentimentBadge.tsx       # Sentiment score indicator
│   │   ├── Analysis/
│   │   │   ├── RQIGauge.tsx            # Risk Quantification Index display
│   │   │   ├── EntryTiers.tsx          # Multi-tier entry recommendation
│   │   │   └── ConfidenceBreakdown.tsx # Weight breakdown (technical vs sentiment)
│   │   └── Dashboard/
│   │       ├── TickerSelector.tsx       # Ticker input/selection
│   │       └── DashboardLayout.tsx      # Main grid layout
│   ├── hooks/
│   │   ├── useMarketData.ts    # Fetch + cache market data
│   │   ├── useTranslation.ts   # Fetch translation results
│   │   └── useAnalysis.ts      # Fetch analysis results
│   └── types/
│       └── index.ts            # Shared TypeScript interfaces
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

### Structure Rationale

- **`backend/app/routers/`:** FastAPI convention. One router per API domain keeps endpoints discoverable and independently testable. Each router maps to one frontend panel.
- **`backend/app/services/`:** Business logic lives here, not in routers. Routers are thin orchestrators that call services. This enables reuse (e.g., `influx_service` used by both `market_data` router and `analysis` router).
- **`backend/app/models/`:** Pydantic models define API contracts. Shared between routers and services. Act as documentation of what flows between components.
- **`frontend/src/components/`:** Organized by dashboard panel (Chart, Translation, Analysis, Dashboard). Each panel is self-contained. Matches the three data flows in the system.
- **`frontend/src/hooks/`:** Custom hooks encapsulate data fetching. Each hook corresponds to one API endpoint. Components remain pure presentation.
- **`frontend/src/api/`:** Single fetch wrapper prevents scattered `fetch()` calls. Centralizes base URL, error handling, and response parsing.

## Architectural Patterns

### Pattern 1: Service-Orchestrated API Endpoints

**What:** Routers are thin HTTP handlers that delegate to service functions. Business logic never lives in the router.
**When to use:** Always. Every endpoint should follow this.
**Trade-offs:** Slight over-engineering for trivial endpoints, but pays off immediately when logic needs reuse or testing.

**Example:**
```python
# routers/analysis.py — thin orchestrator
@router.get("/api/analysis/{ticker}")
async def get_analysis(ticker: str):
    market_data = await influx_service.get_ohlcv(ticker, period="6m")
    corporate_text = await corporate_data.get_latest_earnings(ticker)

    translation = await ollama_service.translate(corporate_text)
    volume_profile = volume_profile_service.calculate(market_data)

    rqi_score = rqi_service.calculate(
        technical_confidence=volume_profile.confidence,
        sentiment_confidence=translation.confidence,
        volume_profile=volume_profile,
        sentiment=translation.sentiment
    )

    entries = entry_builder.generate_tiers(
        volume_profile=volume_profile,
        rqi=rqi_score
    )

    return AnalysisResponse(
        translation=translation,
        volume_profile=volume_profile,
        rqi=rqi_score,
        entry_tiers=entries
    )
```

### Pattern 2: Prompt-and-Parse for LLM Integration

**What:** Send a structured prompt to Ollama with explicit output format instructions. Parse the LLM response into a typed Pydantic model. Never trust raw LLM output for downstream computation.
**When to use:** Every interaction with Ollama.
**Trade-offs:** Requires careful prompt engineering. LLM output is non-deterministic so parsing must be resilient to format variations.

**Example:**
```python
# services/ollama_service.py
import httpx
from models.translation import TranslationResult

OLLAMA_URL = "http://localhost:11434/api/generate"

async def translate(corporate_text: str) -> TranslationResult:
    prompt = f"""Analyze this corporate communication. Return JSON with:
    - "plain_english": rewrite in plain English (2-3 sentences)
    - "sentiment": "bullish" | "bearish" | "neutral"
    - "sentiment_score": float from -1.0 (very bearish) to 1.0 (very bullish)
    - "confidence": float from 0.0 to 1.0 (how confident in sentiment)
    - "key_facts": list of 3-5 key factual takeaways
    - "red_flags": list of concerning items (empty if none)

    Text: {corporate_text}

    JSON:"""

    async with httpx.AsyncClient() as client:
        response = await client.post(OLLAMA_URL, json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        })

    raw = response.json()["response"]
    return parse_llm_json(raw, TranslationResult)
```

### Pattern 3: Convergence-Based Confidence Scoring

**What:** Calculate the same analysis metric using multiple independent methods. When methods agree (converge), confidence is high. When they disagree, confidence is low. Use this confidence to dynamically weight components in the RQI.
**When to use:** Volume Profile key level identification and composite scoring.
**Trade-offs:** More computation per analysis. But convergence is the core differentiator of this product.

**Example concept:**
```python
# services/volume_profile.py
def calculate(ohlcv_data: pd.DataFrame) -> VolumeProfileResult:
    # Method 1: Fixed-range volume profile (price buckets)
    fixed_levels = fixed_range_vp(ohlcv_data)

    # Method 2: VWAP-based levels
    vwap_levels = vwap_analysis(ohlcv_data)

    # Method 3: Point of Control + Value Area
    poc_va = poc_value_area(ohlcv_data)

    # Convergence: levels that appear in 2+ methods
    key_levels = find_convergent_levels(fixed_levels, vwap_levels, poc_va, tolerance=0.02)

    # Confidence = ratio of convergent vs total unique levels
    confidence = len(key_levels) / max(len(set(fixed_levels + vwap_levels + poc_va)), 1)

    return VolumeProfileResult(
        key_levels=key_levels,
        poc=poc_va.poc,
        value_area_high=poc_va.vah,
        value_area_low=poc_va.val,
        confidence=min(confidence, 1.0)
    )
```

## Data Flow

### Flow 1: Market Data (Chart Rendering)

```
[User selects ticker]
    |
    v
[React] --GET /api/market-data/AAPL--> [FastAPI market_data router]
    |                                          |
    |                                   [influx_service.get_ohlcv()]
    |                                          |
    |                                   [InfluxDB Flux query]
    |                                          |
    |                                   [pandas DataFrame → JSON]
    |                                          |
    v                                          v
[Lightweight Charts renders candlestick] <-- [OHLCV JSON response]
```

**Notes:** This is the simplest flow. Data already exists in InfluxDB. FastAPI queries, transforms to JSON-serializable format, returns. Frontend renders.

### Flow 2: Corporate Text Translation

```
[User triggers analysis]
    |
    v
[React] --POST /api/translate {ticker}--> [FastAPI translate router]
    |                                              |
    |                                       [corporate_data.get_latest_earnings(ticker)]
    |                                              |
    |                                       [FMP API or SEC Edgar] --> raw earnings text
    |                                              |
    |                                       [ollama_service.translate(text)]
    |                                              |
    |                                       [Ollama HTTP API] --> LLM inference
    |                                              |
    |                                       [parse_llm_json() → TranslationResult]
    |                                              |
    v                                              v
[Translation Panel renders]              <-- [TranslationResult JSON]
  - Plain English text
  - Sentiment badge (bullish/bearish/neutral)
  - Key facts list
  - Red flags list
```

**Notes:** This flow involves Ollama inference, which is the slowest operation (5-30 seconds depending on model and hardware). Consider returning a loading state to the frontend immediately and using polling or SSE for the result.

### Flow 3: Full Analysis (VP + RQI + Entries)

```
[User triggers analysis] (may share trigger with Flow 2)
    |
    v
[FastAPI analysis router]
    |
    ├── [influx_service.get_ohlcv(ticker, "6m")]  --> OHLCV data (6 months)
    |
    ├── [corporate_data + ollama_service]  --> TranslationResult (sentiment + confidence)
    |       (can reuse Flow 2 result if already computed)
    |
    ├── [volume_profile_service.calculate(ohlcv)]
    |       |
    |       ├── fixed_range_vp()        --> price levels
    |       ├── vwap_analysis()         --> VWAP levels
    |       └── poc_value_area()        --> POC + Value Area
    |       |
    |       └── find_convergent_levels() --> key_levels + confidence
    |
    ├── [rqi_service.calculate()]
    |       |
    |       ├── technical_weight = f(volume_profile.confidence)
    |       ├── sentiment_weight = f(translation.confidence)
    |       └── rqi_score = weighted_composite(technical, sentiment)
    |
    └── [entry_builder.generate_tiers()]
            |
            ├── tier_1: POC level (highest conviction)
            ├── tier_2: Value Area Low (secondary)
            └── tier_3: Extended level (if convergent)
            |
            └── position_sizes based on RQI score
    |
    v
[AnalysisResponse JSON] --> [React Analysis Panel renders]
  - RQI gauge (0-100 score with color)
  - Confidence breakdown (pie: technical % vs sentiment %)
  - Entry tiers (table: level, size, rationale)
  - Volume Profile overlay on chart
```

**Notes:** This is the core orchestration endpoint. It calls multiple services and assembles the composite result. The RQI dynamic weighting is the key innovation: if the LLM sentiment confidence is low (e.g., vague earnings text), technical analysis gets more weight, and vice versa.

### Flow 4: Data Population (Background/Scheduled)

```
[Manual trigger or cron]
    |
    v
[influx-populate-script.py]  (existing, works)
    |
    ├── Alpha Vantage API --> OHLCV daily data
    ├── pandas transforms
    └── InfluxDB batch writes

[corporate-data-fetcher.py]  (new, similar pattern)
    |
    ├── FMP API --> earnings transcripts
    └── Store locally (file or lightweight DB)
```

**Notes:** Data population runs separately from the API server. For the hackathon, manual trigger before demo is fine. Corporate text can be cached locally (JSON files or SQLite) since it changes infrequently.

### Key Data Flows Summary

1. **Market Data flow:** InfluxDB → FastAPI → React chart. Read-only, fast, simple.
2. **Translation flow:** FMP API → FastAPI → Ollama → React panel. Slowest path (LLM inference). Cache aggressively.
3. **Analysis flow:** Orchestrates flows 1+2 plus computation. The "money endpoint."
4. **Population flow:** External APIs → local storage. Runs independently of the web app.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Hackathon demo (1-5 users) | Monolith is perfect. Single FastAPI process, local Ollama, local InfluxDB. No caching needed beyond LLM response caching. |
| Post-hackathon (10-100 users) | Add Redis for LLM response caching (same earnings text = same translation). Add background task queue (Celery or FastAPI BackgroundTasks) for LLM inference so API doesn't block. |
| Production (1000+ users) | Ollama becomes bottleneck. Options: multiple Ollama instances behind load balancer, switch to cloud LLM API (OpenAI/Anthropic), or pre-compute translations on earnings release schedule. Separate InfluxDB read replicas for query load. |

### Scaling Priorities

1. **First bottleneck: Ollama inference latency.** LLM inference takes 5-30 seconds. For hackathon, this is fine with a loading spinner. Post-hackathon, cache translations per earnings-report (they don't change) and move inference to background tasks.
2. **Second bottleneck: Alpha Vantage rate limits.** 5 calls/minute on free tier. For multi-ticker support, implement a queue. For hackathon (AAPL only), not an issue.

## Anti-Patterns

### Anti-Pattern 1: Putting Analysis Logic in the Router

**What people do:** Write Volume Profile calculations, RQI scoring, and entry generation directly inside the FastAPI route handler.
**Why it's wrong:** Creates a 200-line endpoint function. Impossible to test VP calculation without spinning up the HTTP server. Cannot reuse logic.
**Do this instead:** Router calls `volume_profile_service.calculate()`, `rqi_service.calculate()`, `entry_builder.generate_tiers()`. Each service is independently testable.

### Anti-Pattern 2: Treating LLM Output as Structured Data

**What people do:** Parse Ollama JSON response directly into application logic without validation. Assume the LLM always returns valid JSON with correct field names and types.
**Why it's wrong:** LLMs are non-deterministic. They may add commentary around JSON, use slightly different field names, or return malformed output. This causes runtime crashes in production.
**Do this instead:** Wrap LLM response parsing in a resilient parser. Use regex to extract JSON from surrounding text. Validate with Pydantic. Have fallback defaults for missing fields. Log parse failures for prompt improvement.

### Anti-Pattern 3: Synchronous Ollama Calls Blocking the Event Loop

**What people do:** Use `requests.post()` (synchronous) to call Ollama from an async FastAPI endpoint.
**Why it's wrong:** Blocks the entire FastAPI event loop for 5-30 seconds during LLM inference. All other requests queue behind it.
**Do this instead:** Use `httpx.AsyncClient` for Ollama HTTP calls, or run synchronous calls in a thread pool via `asyncio.to_thread()`. FastAPI async endpoints must never block.

### Anti-Pattern 4: Hardcoding RQI Weights

**What people do:** Set technical_weight=0.6 and sentiment_weight=0.4 as constants.
**Why it's wrong:** Defeats the core value proposition. If the LLM returns low-confidence sentiment (e.g., vague earnings text), a fixed 40% weight for sentiment dilutes the reliable technical signal.
**Do this instead:** RQI weights are functions of confidence. High sentiment confidence → sentiment gets more weight. Low sentiment confidence → technical analysis dominates. The formula should be explicit and documented.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **Alpha Vantage** | REST API via `requests` (existing script) | Free tier: 5/min, 500/day. 15s delay between calls. Returns JSON OHLCV. |
| **InfluxDB** | `influxdb-client` Python SDK, Flux queries | Running locally on port 8086. Bucket: `market_data`. Measurement: `stock_price`. |
| **Ollama** | HTTP REST API at `localhost:11434` | `/api/generate` endpoint. Model loaded in memory. First call slower (model load). |
| **FMP (Financial Modeling Prep)** | REST API via `httpx` | Free tier available. Provides earnings transcripts for 8000+ US companies. JSON responses. |
| **SEC Edgar** | REST API (backup for FMP) | Free, no key required but needs User-Agent header. Slower to parse (XBRL/HTML). Use as fallback. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Frontend ↔ Backend | REST JSON over HTTP (port 8000) | CORS must be configured. All data flows through 3 endpoints: `/market-data`, `/translate`, `/analysis` |
| Backend routers ↔ Services | Direct Python function calls | No network boundary. Services are imported modules. Keeps hackathon simple. |
| Backend ↔ InfluxDB | InfluxDB Python client (Flux queries) | Connection pooling recommended. Use context managers for client lifecycle. |
| Backend ↔ Ollama | HTTP (localhost:11434) | Use `httpx.AsyncClient` to avoid blocking. Timeout should be generous (60s+ for large models). |
| Backend ↔ FMP/SEC | HTTP REST | Cache responses locally. Earnings don't change after release. |

## Build Order (Dependency Chain)

The components have clear dependencies that dictate build sequence:

### Phase 1: Foundation (backend skeleton + data serving)
**Build:** FastAPI app skeleton, `influx_service`, `market_data` router
**Why first:** Proves the backend can serve existing InfluxDB data. Frontend charting depends on this.
**Dependency:** InfluxDB data already exists (population script is done).

### Phase 2: Frontend shell + chart
**Build:** React + Vite setup, `PriceChart` component, `DashboardLayout`, `useMarketData` hook
**Why second:** Proves end-to-end data flow from InfluxDB → FastAPI → React chart. Visual progress for demo.
**Dependency:** Requires Phase 1 (API endpoint to fetch from).

### Phase 3: Corporate data + LLM translation
**Build:** `corporate_data` service (FMP fetcher), `ollama_service`, `translate` router, `TranslationPanel` frontend
**Why third:** Independent from technical analysis. Can be built in parallel with Phase 4 if resources allow.
**Dependency:** Requires Ollama model installed and running. Requires FMP API key.

### Phase 4: Technical analysis engine
**Build:** `volume_profile` service, `entry_builder` service
**Why fourth:** Pure computation on existing data. No new external dependencies.
**Dependency:** Requires `influx_service` from Phase 1 for input data.

### Phase 5: RQI + orchestration
**Build:** `rqi` service, `analysis` router (orchestration endpoint), `RQIGauge` + `EntryTiers` + `ConfidenceBreakdown` frontend components
**Why last:** Depends on all previous phases. The RQI combines technical (Phase 4) and sentiment (Phase 3) outputs.
**Dependency:** Requires Phases 3 and 4 complete.

### Parallel Opportunities
- Phases 3 and 4 can be built in parallel (independent inputs).
- Frontend components for each phase can be built alongside their backend counterpart.
- Data population (existing script) and new corporate data fetcher can be run anytime.

## Sources

- [FastAPI + Ollama integration pattern](https://mljourney.com/how-to-serve-local-llms-as-an-api-fastapi-ollama/) — MEDIUM confidence
- [Financial Sentiment Analysis with NLP + FastAPI](https://medium.com/@vanmeeganathanharini/building-a-financial-sentiment-analysis-api-using-nlp-fastapi-6340b4f84fde) — MEDIUM confidence
- [Volume Profile in Python (py-market-profile)](https://github.com/bfolkens/py-market-profile) — HIGH confidence (library exists, actively maintained)
- [Volume Profile calculation approaches](https://medium.com/swlh/how-to-analyze-volume-profiles-with-python-3166bb10ff24) — MEDIUM confidence
- [FastAPI project structure best practices](https://github.com/zhanymkanov/fastapi-best-practices) — HIGH confidence
- [TradingView Lightweight Charts React integration](https://tradingview.github.io/lightweight-charts/tutorials/react/simple) — HIGH confidence (official docs)
- [FMP Earnings Transcript API](https://site.financialmodelingprep.com/developer/docs/earning-call-transcript-api) — HIGH confidence (official docs)
- [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) — HIGH confidence (official)
- [Ollama financial analysis patterns](https://www.both.org/?p=7918) — LOW confidence (single source)
- [Sentiment + technical indicators composite scoring (academic)](https://www.mdpi.com/2079-9292/14/4/773) — MEDIUM confidence (peer-reviewed)
- [FastAPI for microservices patterns 2025](https://talent500.com/blog/fastapi-microservices-python-api-design-patterns-2025/) — MEDIUM confidence
- [InfluxDB + FastAPI data API](https://community.influxdata.com/t/building-a-data-api-with-influxdb-and-fastapi/20963) — MEDIUM confidence

---
*Architecture research for: FinSpeak Trader — financial NLP + technical trading analysis platform*
*Researched: 2026-02-09*
