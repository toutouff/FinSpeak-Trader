# Project Research Summary

**Project:** FinSpeak Trader - Financial Analysis Platform with NLP-Powered Corporate Communication Translation
**Domain:** Financial analysis platform combining natural language processing for corporate communication decoding with technical trading intelligence
**Researched:** 2026-02-09
**Confidence:** MEDIUM-HIGH

## Executive Summary

FinSpeak Trader occupies a unique niche: no competitor currently translates corporate jargon into plain English AND connects those translations to technical entry recommendations with a unified confidence score. The product combines Ollama-powered local LLM analysis of earnings transcripts with Volume Profile-based technical analysis, unified through a Risk Quantification Index (RQI) that dynamically weighs signals based on confidence levels. The recommended architecture is a FastAPI backend orchestrating InfluxDB market data, Ollama LLM inference, and computational analysis services, with a React frontend featuring TradingView Lightweight Charts for visualization.

The critical success path is a working vertical slice: one ticker (AAPL), one earnings release, demonstrating end-to-end flow from corporate text to actionable entry recommendations within the 1-week hackathon timeline. The biggest risks are: (1) LLM hallucination of financial numbers requiring strict prompt engineering and validation, (2) Volume Profile approximation from daily data producing misleading support/resistance levels, (3) Ollama inference latency (5-30 seconds) blocking the API without proper async architecture, and (4) scope creep preventing any feature from reaching demo-ready state.

The research strongly recommends building in vertical slices (complete features end-to-end) rather than horizontal layers, with ruthless prioritization: the plain English translation is the core differentiator and must be protected. Technical features can be simplified if needed. Pre-cache all LLM results for the demo as a backup while demonstrating live inference capability. The project is technically feasible but requires disciplined scope management and daily go/no-go checkpoints.

## Key Findings

### Recommended Stack

The stack leverages Python's financial computation ecosystem on the backend with modern async-first patterns, paired with React's component model on the frontend. FastAPI with Pydantic V2 provides type-safe API contracts and automatic OpenAPI documentation. The local Ollama + Llama 3.1 8B approach eliminates API costs and latency concerns of cloud LLMs while requiring careful async handling to prevent blocking. TradingView Lightweight Charts (45KB) provides production-quality financial charting without the bloat of general-purpose libraries.

**Core technologies:**
- **FastAPI ^0.128.5**: Async-first REST API framework - reuses existing pandas/InfluxDB pipeline code, built-in validation via Pydantic, fastest Python web framework
- **Ollama + Llama 3.1 8B Instruct**: Local LLM for corporate text analysis - zero API cost, 128K context for full earnings transcripts, outperforms Mistral 7B (66.7% vs 60.1% MMLU)
- **React ^19 + Vite ^7.3.1**: UI framework with sub-300ms dev server - component model fits data-heavy dashboards, CRA deprecated, requires Node 20.19+
- **lightweight-charts ^5.1.0**: Financial charting - purpose-built for OHLCV data, 45KB bundle, supports custom plugins for Volume Profile overlay
- **pandas ^2.2.x + numpy ^2.4.2 + scipy ^1.17.0**: Data computation stack - Volume Profile calculations, support/resistance clustering, already in use for OHLCV pipeline
- **@tanstack/react-query ^5.90.x + zustand ^5.0.11**: State management - TanStack Query for server state (caching, refetch), Zustand for UI state, eliminates Redux boilerplate
- **Tailwind CSS ^4.1.18**: Utility-first CSS - v4 Oxide engine 5x faster builds, zero-config setup, perfect for rapid hackathon prototyping
- **Financial Modeling Prep API**: Corporate data source - free tier 250 req/day, structured earnings transcripts as JSON, supplemented by edgartools for SEC filings

**Critical version requirements:**
- Python >=3.11, <3.14 (3.11+ for 10-60% performance gain, avoid 3.14 - too new)
- Node.js >=20.19 or >=22.12 (Vite 7.x requirement)
- Pydantic V2 (V1 deprecated in FastAPI, 5-50x speedup from Rust core)
- Use httpx (async) NOT requests (blocks event loop) for all HTTP calls in FastAPI

**What NOT to use:**
- LangChain (MVP) - massive dependency tree, abstraction overhead wastes hackathon time
- Redux - Zustand + TanStack Query achieves same with 1/5 the code
- Axios - TanStack Query makes it redundant, saves 11.7KB
- MUI/Ant Design - fights custom fintech aesthetic, 80KB+ even tree-shaken
- React wrapper libs for Lightweight Charts - all unmaintained since 2019-2021

### Expected Features

FinSpeak's differentiation comes from connecting corporate communication analysis to trading intelligence. AlphaSense dominates the NLP space but targets institutional analysts at $10K+/year and doesn't provide entry recommendations. Danelfin provides AI scoring (1-10) but doesn't analyze corporate text. TradingView provides charts but no NLP. The combination of plain English translation + technical entry zones + unified confidence scoring is genuinely novel in the market.

**Must have (table stakes):**
- **Interactive price chart (AAPL)** - visual anchor, first thing judges see, every financial platform has one
- **Corporate text display** - show original alongside translation, users need to verify the decoding
- **Plain English translation** - THE core promise, LLM-powered jargon decoding defines product identity
- **Sentiment indicator** - bullish/bearish/neutral with score, color-coded, every competitor has this
- **Volume Profile entry zones** - VPOC + Value Area overlay on chart, minimum technical analysis requirement
- **RQI score** - combined technical + sentiment confidence with visual display, key differentiator
- **Loading states** - LLM takes 5-30 seconds, users must see progress not frozen screens
- **Ticker selector** - UI affordance even if AAPL is hardcoded, shows extensibility

**Should have (competitive advantage):**
- **Multi-tier DCA position plan** - distribute allocation across 3-5 levels with percentages, how professionals actually trade
- **Source-quality weighted sentiment** - earnings calls > press releases > news, encodes domain expertise generic NLP misses
- **Jargon-to-meaning annotations** - inline tooltips for specific phrases, micro-level decoding enhances wow factor
- **Analysis narrative** - 2-3 paragraph synthesis tying sentiment + technical + RQI, differentiates from disconnected widgets
- **Explainable scoring breakdown** - show which indicators converged, which sources contributed, transparency builds trust

**Defer (v2+):**
- **Multi-ticker support** - requires scaling all pipelines, post-hackathon priority #1
- **Historical sentiment tracking** - needs quarters of data collection first
- **Backtesting framework** - months of historical RQI data required
- **Trade execution integration** - brokerage APIs add regulatory complexity
- **Real-time streaming data** - WebSocket infrastructure massive overkill for daily-timeframe analysis

**Anti-features (commonly requested but problematic):**
- Real-time streaming data - Alpha Vantage free tier can't support it, analysis is daily-timeframe anyway
- User accounts/persistence - auth system adds zero demo value, PROJECT.md explicitly excludes this
- Social/community features - entirely different product category, distracts from analytical value

### Architecture Approach

The architecture follows a service-orchestrated pattern: thin FastAPI routers delegate to domain services (market data, NLP/LLM, analysis engine) which handle business logic and can be independently tested. The three primary data flows are: (1) Market Data (InfluxDB → FastAPI → React chart), (2) Corporate Text Translation (FMP API → Ollama → React panel), and (3) Full Analysis (orchestrates flows 1+2 plus Volume Profile + RQI computation). This modular structure allows parallel development once interfaces are defined.

**Major components:**
1. **FastAPI Backend (API Gateway)** - three routers (/market-data, /translate, /analysis), thin orchestrators calling services, Pydantic models define contracts
2. **Market Data Service** - InfluxDB queries for OHLCV, pandas DataFrame transforms, JSON serialization for frontend
3. **NLP/LLM Service** - prompt-and-parse pattern, structured JSON output from Ollama, Pydantic validation, never trust raw LLM output
4. **Analysis Engine** - Volume Profile calculation using convergence-based confidence (multiple independent methods agree = higher confidence), RQI dynamic weighting algorithm, multi-tier entry builder
5. **React Frontend** - component-per-panel (Chart, Translation, Analysis), custom hooks for data fetching, Lightweight Charts imperative API wrapped in React

**Critical patterns:**
- **Service-Orchestrated API Endpoints**: Routers never contain business logic, always delegate to services. Enables reuse and testing.
- **Prompt-and-Parse for LLM**: Structured output instructions in prompt, resilient parsing with Pydantic validation, explicit confidence fields in responses
- **Convergence-Based Confidence**: Calculate same metric via multiple methods (fixed-range VP, VWAP, POC+Value Area), convergence = high confidence, feeds RQI dynamic weighting
- **Async All The Way**: httpx.AsyncClient for Ollama calls, never requests (blocks event loop), pre-warm model on startup, streaming responses for UX

**Project structure:**
```
backend/app/
  routers/ - thin HTTP handlers
  services/ - business logic (influx, ollama, corporate_data, volume_profile, rqi, entry_builder)
  models/ - Pydantic schemas
frontend/src/
  components/ - Chart, Translation, Analysis, Dashboard panels
  hooks/ - data fetching (useMarketData, useTranslation, useAnalysis)
  api/ - centralized fetch wrapper
```

### Critical Pitfalls

Research identified six critical pitfalls that will sink the project if not addressed proactively. The LLM hallucination risk is severe because fabricated financial numbers look authoritative and corrupt downstream RQI calculations. Volume Profile from daily data is fundamentally limited but can be mitigated by supplementing with conventional support/resistance and clear labeling. The async architecture must be correct from day 1 because retrofitting is painful. Scope creep is the silent killer - each feature has hidden depth that doubles time estimates.

1. **LLM Hallucination of Financial Numbers** - Models generate plausible but fabricated figures (e.g., "revenue grew 12.3%" when actually 8.7%). Prevention: never use LLM to extract numbers, parse programmatically from structured data. Constrain output with JSON schema forcing categorical answers. Include confidence fields, treat low-confidence as "unable to determine." Validate against 5-10 known earnings excerpts before connecting to pipeline. Phase to address: Phase 1 (LLM integration).

2. **Volume Profile from Daily OHLCV Produces Misleading Levels** - Real VP requires intraday tick/minute data showing where volume actually traded. Daily bars force uniform distribution across H-L range, creating phantom support/resistance. Prevention: label as "estimated value areas" not "confirmed support," use triangular distribution weighted toward typical price, supplement with conventional S/R for cross-validation. Acknowledge limitation explicitly in UI. Phase to address: Phase 2 (Technical Analysis).

3. **Alpha Vantage Free Tier Bottleneck** - 25 requests/day exhausted in minutes during development. Prevention: cache aggressively from day 1, pre-populate all demo data on days 1-2, use SEC EDGAR for corporate filings (no quota), verify demo works offline. Phase to address: Phase 0 (Infrastructure).

4. **Ollama Response Time Blocks FastAPI** - Local LLM inference takes 5-60 seconds. Synchronous calls block entire server, no concurrent requests served, users see 30-second spinner and assume failure. Prevention: use httpx.AsyncClient (not requests), implement streaming responses so users see tokens within 1-2 seconds, set keepalive to prevent model unloading, pre-warm on startup, pre-compute results for demo. Phase to address: Phase 1 (Backend API).

5. **Scope Creep Kills 1-Week Timeline** - Each feature has hidden domain complexity. RQI alone requires research before implementation. Attempting all features results in nothing demo-ready. Prevention: ruthless MVP definition (one ticker, one earnings release, one complete flow), build vertical slices not horizontal layers, timebox features to 1 day, hard-code what you can, protect LLM integration time (the differentiator). Daily checkpoints: day 3 must show one working end-to-end flow or cut features. Phase to address: Every phase.

6. **RQI Score Without Calibration Is Meaningless** - Composite score without validation against known outcomes is an arbitrary number. Users ask "what does 72 mean?" and "how accurate is it?" Prevention: start with simple transparent formula (0.5 technical + 0.5 sentiment), map ranges to categories (0-30 High Risk, 31-60 Moderate, 61-100 Low Risk), use confidence as display modifier not weighting for v1, pre-validate against 3-5 historical AAPL events for demo. Phase to address: Phase 3 (Integration).

## Implications for Roadmap

Based on dependency analysis from architecture research and risk prioritization from pitfalls research, the optimal phase structure follows a vertical-slice approach building demonstrable value incrementally. The LLM integration and technical analysis streams can be developed in parallel after foundation is laid, then unified in the RQI scoring phase. Each phase must produce a demo-able artifact to maintain momentum and enable early de-risking of the critical LLM hallucination and async architecture concerns.

### Phase 0: Infrastructure & Data Pipeline (Days 1-2)
**Rationale:** Must solve data sourcing and caching before any development. Alpha Vantage free tier (25 req/day) is too limited for iterative development. Existing InfluxDB population script needs hardening with aggressive caching. Corporate data fetching (FMP API or SEC EDGAR) is entirely new and must be proven.

**Delivers:**
- InfluxDB confirmed populated with AAPL 6-month daily OHLCV (already exists, verify)
- Corporate data fetcher working (FMP API or edgartools for SEC filings)
- At least 1 AAPL earnings transcript cached locally
- All data access wrapped in cache-first pattern
- Demo works offline (critical for reliability)

**Addresses:**
- Alpha Vantage rate limit pitfall (cache everything)
- Data freshness indicator (table stakes feature)

**Stack:** influxdb-client, pandas, httpx for async API calls, Financial Modeling Prep free tier, edgartools as backup

**Avoids:** Pitfall #3 (API quota exhaustion mid-demo)

**Research Flag:** Standard pattern - existing script shows the way, extending for corporate data is mechanical

### Phase 1: Backend API Foundation + LLM Integration (Days 2-3)
**Rationale:** The async architecture must be correct from the start. LLM hallucination validation cannot be deferred. This phase proves the core differentiator (plain English translation) works before building anything on top of it. Parallel to Phase 2 after day 2.

**Delivers:**
- FastAPI app skeleton with CORS configured
- `/api/market-data/{ticker}` router returning cached OHLCV as JSON
- `/api/translate` router orchestrating corporate data fetch + Ollama inference
- Ollama service with async httpx client, structured prompt templates
- TranslationResult Pydantic model with confidence scoring
- Test suite: 5-10 known earnings excerpts with expected interpretations
- Ollama model pre-warmed on startup, keepalive configured

**Addresses:**
- Plain English translation (table stakes, core promise)
- Sentiment indicator (table stakes)
- Loading states (async streaming responses)

**Stack:** FastAPI, Pydantic V2, httpx (async), ollama Python client, Llama 3.1 8B Instruct quantized

**Avoids:**
- Pitfall #1 (LLM hallucination - validation test suite catches this)
- Pitfall #4 (blocking async - httpx.AsyncClient from day 1)

**Research Flag:** NEEDS DEEPER RESEARCH - prompt engineering for financial text is domain-specific, LLM output parsing needs resilience patterns. Consider `/gsd:research-phase` on "Financial LLM Prompt Engineering" if validation suite shows hallucination issues.

### Phase 2: Technical Analysis Engine (Days 3-4, parallel with Phase 1)
**Rationale:** Pure computation on existing InfluxDB data, no external dependencies beyond Phase 0. Can be developed in parallel with LLM integration once data pipeline is proven. Volume Profile convergence calculation is the second major innovation area.

**Delivers:**
- Volume Profile service calculating VPOC, Value Area High/Low
- Convergence detection across multiple methods (fixed-range VP, VWAP, POC+Value Area)
- Technical confidence scoring (number of convergent signals)
- Support/resistance identification supplementing VP
- Entry point identification at key levels
- `/api/analysis/{ticker}` router (partial - technical analysis only, no sentiment yet)

**Addresses:**
- Volume Profile entry zones (table stakes)
- Convergence-based confidence (differentiator)

**Stack:** pandas, numpy, scipy (signal processing for peak detection, KDE for smoothing), scikit-learn (AgglomerativeClustering for price level grouping)

**Avoids:** Pitfall #2 (VP from daily data - supplement with conventional S/R, label clearly as "estimated")

**Research Flag:** MODERATE RESEARCH NEEDED - Volume Profile algorithms have variations (fixed-range vs session-based vs visible-range). Standard libraries exist (py-market-profile) but daily data adaptation is custom. Consider quick research spike on VP calculation approaches if not confident.

### Phase 3: Frontend Shell + Chart Integration (Day 4)
**Rationale:** Proves end-to-end data flow, provides visual feedback on progress, unblocks UI development for later phases. Lightweight Charts integration has known patterns but the Volume Profile overlay is custom (plugin system).

**Delivers:**
- React + Vite scaffolded with TypeScript + Tailwind CSS v4
- DashboardLayout component with ticker selector (AAPL hardcoded)
- PriceChart component wrapping Lightweight Charts imperative API
- useMarketData hook fetching from `/api/market-data/AAPL`
- Candlestick + volume histogram rendering
- Volume Profile overlay plugin (histogram series type at price levels)
- Responsive layout (mobile-friendly)

**Addresses:**
- Interactive price chart (table stakes)
- Ticker selector (table stakes)
- Mobile-responsive layout (table stakes)

**Stack:** React 19, Vite 7.3.1, TypeScript 5.7.x, Tailwind CSS 4.1.18, lightweight-charts 5.1.0, @tanstack/react-query 5.90.x, zustand 5.0.11

**Avoids:** Common mistake - creating chart in render cycle (use useRef + useEffect)

**Research Flag:** Well-documented pattern - TradingView has official React integration tutorials, though VP plugin is custom. Standard patterns apply.

### Phase 4: RQI Scoring + Full Analysis Integration (Day 5)
**Rationale:** Combines Phase 1 (sentiment) and Phase 2 (technical) outputs. The dynamic weighting algorithm is the key innovation - if LLM confidence is low, technical gets more weight. This phase unifies the two parallel development streams.

**Delivers:**
- RQI service calculating dynamic-weighted composite score
- Weighting algorithm: confidence-based (high sentiment confidence → sentiment weighted more)
- Entry builder service generating multi-tier DCA position plan
- `/api/analysis/{ticker}` completed (orchestrates market data + translation + VP + RQI)
- TranslationPanel React component displaying plain English + sentiment
- RQIGauge component showing 0-100 score with color-coding + categorical label
- EntryTiers component displaying multi-tier DCA recommendations
- ConfidenceBreakdown component showing technical vs sentiment weight split

**Addresses:**
- RQI score (differentiator)
- Multi-tier DCA plan (differentiator)
- Corporate text display (table stakes)
- Explainable scoring (differentiator)

**Stack:** Backend orchestration logic, frontend React components with TanStack Query for data fetching

**Avoids:**
- Pitfall #6 (meaningless score - start with simple formula, map to categories)
- Pitfall #4 (anti-pattern - no analysis logic in router, all in services)

**Research Flag:** LOW - combination logic, not new techniques. Formula calibration is iterative but can start simple.

### Phase 5: Polish + Demo Hardening (Days 6-7)
**Rationale:** All core features complete. This phase adds the storytelling layer and ensures reliability for live demo. Pre-compute LLM results as backup while showing live inference capability.

**Delivers:**
- Analysis narrative generation (LLM synthesis of all outputs)
- Jargon-to-meaning annotations (inline tooltips)
- Source-quality weighted sentiment (if multiple sources available)
- Error handling for all failure modes (Ollama down, InfluxDB disconnected, invalid ticker)
- Pre-computed LLM results for AAPL cached, served with "cached" indicator
- Live inference demonstrated on secondary example
- Loading states with progress indicators
- Data freshness timestamps on all displays
- Disclaimer text ("for educational purposes, not financial advice")

**Addresses:**
- Analysis narrative (differentiator)
- Jargon annotations (differentiator)
- Source-quality weighting (differentiator)
- All UX polish items from pitfalls research

**Stack:** LLM for narrative generation, frontend polish components

**Avoids:** Pitfall #5 (scope creep - these are enhancements, not core features, can be cut if behind)

**Research Flag:** No additional research - polish work

### Phase Ordering Rationale

- **Phase 0 before all:** Data availability blocks everything. Cache-first pattern prevents demo-day API failures.
- **Phases 1 and 2 parallel after Phase 0:** LLM integration and technical analysis have no interdependencies until Phase 4. Parallelizing accelerates delivery.
- **Phase 3 after Phase 1 starts:** Frontend needs `/api/market-data` endpoint (simple, completed early in Phase 1), can proceed while LLM integration completes.
- **Phase 4 integrates Phases 1 + 2:** RQI cannot be built until both sentiment and technical outputs exist. This is the convergence point.
- **Phase 5 last:** Polish depends on core features existing. Can be cut if timeline slips.

**Critical path:** Phase 0 → Phase 1 (LLM) → Phase 4 (RQI). If this path works, you have a demo. Phase 2 (technical analysis) strengthens the demo but RQI can degrade gracefully to sentiment-only scoring if VP fails. Phase 3 (frontend) and Phase 5 (polish) add UX but don't change the analytical value.

**Daily checkpoints:**
- **Day 2 EOD:** Phase 0 complete, all data cached, can demo offline
- **Day 3 EOD:** Phase 1 LLM validation suite passing, no hallucinations detected
- **Day 4 EOD:** Phase 3 chart rendering real data from backend
- **Day 5 EOD:** Phase 4 RQI showing scores end-to-end for AAPL, GO/NO-GO for feature cuts
- **Day 6 EOD:** Full demo flow rehearsed, backup cached results tested

### Research Flags

**Phases needing deeper research during planning:**
- **Phase 1 (LLM Integration):** Financial prompt engineering is domain-specific, hallucination mitigation patterns need validation. If validation suite shows issues, run `/gsd:research-phase` on "LLM Financial Hallucination Prevention" before proceeding to Phase 4.
- **Phase 2 (Volume Profile):** VP from daily data has known limitations. If initial implementation produces nonsensical levels, research spike on "Volume Profile Daily Bar Approximation Methods" may be needed. py-market-profile library exists but may need adaptation.

**Phases with standard patterns (skip research-phase):**
- **Phase 0 (Data Pipeline):** Existing InfluxDB script shows the pattern, extending for corporate data is mechanical HTTP + caching.
- **Phase 3 (Frontend + Chart):** TradingView Lightweight Charts has official React tutorials, TanStack Query is well-documented. Volume Profile overlay uses plugin system (documented).
- **Phase 4 (RQI Integration):** Orchestration logic, no new techniques. Formula may need iterative tuning but doesn't require research.
- **Phase 5 (Polish):** Standard frontend work, no novel patterns.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Most versions verified via official sources (FastAPI, React, Vite, npm packages all confirmed). Ollama + Llama 3.1 recommended based on benchmarks (MMLU 66.7% vs Mistral 60.1%). Minor packages (influxdb-client, edgartools) confirmed via PyPI. |
| Features | MEDIUM-HIGH | Competitive analysis shows FinSpeak's combination is genuinely novel (no competitor does plain English translation + technical entry recommendations + unified scoring). Feature dependencies mapped clearly. MVP vs v2 split is defensible. Anti-features identified based on hackathon timeline. |
| Architecture | MEDIUM-HIGH | Service-orchestrated pattern is FastAPI best practice (verified multiple sources). Convergence-based confidence scoring is novel but algorithmically straightforward. Frontend patterns (TanStack Query + Zustand) are community-standard for 2026. Project structure follows FastAPI conventions. |
| Pitfalls | MEDIUM-HIGH | LLM hallucination in finance is well-documented (academic papers, industry governance frameworks). VP from daily data limitation is known in trading education. Alpha Vantage rate limits verified. Ollama async patterns confirmed in community tutorials. Scope creep is universal hackathon risk. |

**Overall confidence:** MEDIUM-HIGH

The stack and architecture recommendations are solidly grounded in official documentation and community best practices. The feature differentiation is validated against real competitors. The pitfalls are domain-specific but well-researched. The main uncertainty is LLM prompt engineering for financial text - this is newer territory (Llama 3.1 released 2024, financial fine-tunes are less mature). The Volume Profile calculation from daily data has known limitations that are mitigable but not eliminable.

### Gaps to Address

**LLM Prompt Engineering for Financial Text:** Research shows general patterns (structured output, confidence scoring) but optimal prompts for earnings transcript analysis are domain-specific. Gap: need to iterate on prompt templates during Phase 1 with validation suite. If validation shows persistent hallucination, may need to research financial prompt engineering best practices or consider fine-tuned models (Finance-Llama-8B as alternative). **Mitigation:** Build 5-10 test case validation suite immediately in Phase 1, iterate prompts until zero fabricated numbers appear.

**Volume Profile Daily Bar Distribution Method:** Research identifies the limitation (daily data lacks intraday price distribution) but doesn't conclusively recommend one approximation method over another (uniform vs triangular vs close-weighted). Gap: empirical testing needed to see which produces more meaningful levels for AAPL. **Mitigation:** Start with triangular distribution weighted toward typical price ((H+L+C)/3), supplement with conventional S/R, label clearly as "estimated value areas." If levels are nonsensical, pivot to conventional S/R only and drop VP.

**RQI Formula Calibration:** Research recommends starting simple (0.5 technical + 0.5 sentiment) but doesn't provide empirically validated weighting. Gap: no ground truth for what weighting produces predictive scores. **Mitigation:** Accept that v1 will be a demonstration metric, not validated. Map to human-readable categories, show formula transparently, pre-validate against 3-5 historical AAPL events for directional correctness. Defer true backtesting to v2.

**FMP Free Tier Sufficiency:** Research confirms 250 req/day free tier exists but doesn't validate whether earnings transcript coverage for AAPL is complete or if response format is parseable. Gap: won't know until trying. **Mitigation:** Phase 0 day 1, fetch AAPL earnings transcript and inspect. If FMP fails, edgartools (SEC EDGAR) is backup but requires HTML parsing (more complex). Build FMP fetcher with edgartools fallback.

**Ollama Inference Time on Target Hardware:** Research cites 5-60 seconds depending on hardware but doesn't know what hardware will be used. 7B quantized models should run on 8GB RAM but inference time is uncertain. Gap: won't know until running. **Mitigation:** Phase 1 day 1, benchmark Ollama on actual hardware. If >30 seconds per request, consider smaller quantization (q4_0 instead of q4_K_M) or Mistral 7B (faster inference). Pre-warm model and use streaming responses regardless.

## Sources

### Primary (HIGH confidence)
- FastAPI, Pydantic, Vite, React, npm package versions verified via official PyPI/npm registries and release notes
- TradingView Lightweight Charts official documentation and React integration tutorials
- TanStack Query, Zustand, React Router official documentation
- InfluxDB Python client documentation, Flux query patterns
- SEC EDGAR API official documentation (sec.gov)
- Financial Modeling Prep API official documentation and pricing (verified free tier 250 req/day)
- Alpha Vantage API limits (verified 25 req/day across multiple sources)

### Secondary (MEDIUM confidence)
- Llama 3.1 vs Mistral 7B benchmark comparison (MMLU scores, context window) - third-party benchmarking sites
- AlphaSense, Danelfin, SentimenTrader competitive analysis - official product documentation + independent reviews
- Volume Profile trading education - multiple trading education sites (JumpStartTrading, Trusted-Broker-Reviews)
- FastAPI project structure best practices - community GitHub repo (zhanymkanov/fastapi-best-practices)
- LLM hallucination in financial services - academic papers (arXiv) and industry AI governance frameworks (FINOS)
- Financial NLP patterns (FactSet, UC Berkeley studies on earnings call analysis)
- Ollama + FastAPI integration patterns - community Medium tutorials

### Tertiary (LOW confidence)
- Finance-Llama-8B model existence (mentioned in Ollama registry but limited usage data)
- VADER vs TextBlob sentiment accuracy on financial text (single blog post comparison)
- Best local LLMs 2026 rankings (secondary comparison sites)
- AI tools for financial analysis 2026 (industry roundup articles)

---
*Research completed: 2026-02-09*
*Ready for roadmap: yes*
