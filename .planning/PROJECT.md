# FinSpeak Trader

## What This Is

FinSpeak Trader is a financial analysis platform that decodes corporate communications (earnings calls, press releases, financial news) into plain English and connects those insights to actionable technical trading strategies. It empowers non-trader investors to make informed decisions by combining NLP-powered communication analysis with technical indicators, volume profiling, and a dynamic risk scoring system. Built for a hackathon demo with a 1-week timeline.

## Core Value

**Build a multi-signal financial analysis engine that combines technical analysis convergence with NLP sentiment scoring into a dynamic, confidence-weighted Risk Quantification Index (RQI) and actionable entry recommendations** — the analytical engine is the product, the UI is the display layer.

## Requirements

### Validated

- ✓ Market data ingestion from Alpha Vantage API (OHLCV daily) — existing
- ✓ InfluxDB time-series storage with batch writes and retry logic — existing
- ✓ Data integrity verification for stored market data — existing
- ✓ ESLint + Prettier code quality tooling configured — existing

### Active

- [ ] Plain English Translator: analyze corporate text via local LLM and produce clear translation
- [ ] Volume Profile Analysis: identify key price levels using multiple technical methods
- [ ] Multi-Tier Position Building: Dollar-Cost Average entry points across identified levels
- [ ] Risk Quantification Index (RQI): dynamic-weighted score combining technical + sentiment confidence
- [ ] Corporate data pipeline: fetch earnings/news via free API
- [ ] FastAPI backend serving all analysis endpoints
- [ ] React frontend with modern clean fintech UI (Robinhood/Revolut style)
- [ ] Lightweight Charts (TradingView) price visualization with volume profile overlay
- [ ] End-to-end demo flow for single ticker (AAPL)

### Out of Scope

- Multi-company comparison — post-hackathon feature
- Historical pattern recognition across communications — too complex for 1-week MVP
- Real-time updates and alerts — requires infrastructure beyond hackathon scope
- Mobile app — web-first, responsive sufficient
- Portfolio-level insights — requires multi-ticker analysis
- User authentication — unnecessary for hackathon demo
- CI/CD pipeline — not needed for hackathon
- Production deployment — local demo only

## Context

**Hackathon context**: 1-week timeline. Demo-ready is the priority. The app needs to work end-to-end on one ticker (AAPL) with a compelling visual flow.

**Existing code**: A Python script (`backend/influx-populate-script.py`) already handles fetching OHLCV data from Alpha Vantage and storing it in InfluxDB. This is the only functional code — frontend and backend API are empty.

**User profile**: The builder is not a trader. The system needs to be intelligent about analysis methods — research and implement proven technical analysis approaches rather than relying on domain expertise.

**LLM setup**: Ollama is installed locally but not fully configured. A model needs to be selected (likely Llama 3 or Mistral 7B) for corporate text analysis.

**Corporate data gap**: No pipeline exists for corporate communications. Need a free API (Financial Modeling Prep, SEC Edgar, or similar) for earnings transcripts and financial news.

**Existing data**: InfluxDB contains OHLCV daily data for AAPL, MSFT, GOOGL, NVDA via Alpha Vantage.

**Known issues**:
- API key may be exposed in git history (commit b5d5b78)
- No `requirements.txt` for Python dependencies
- `.gitignore` only covers `/node_modules`
- No `tsconfig.json` despite TypeScript ESLint config

## Constraints

- **Timeline**: 1 week (hackathon) — speed over perfection
- **LLM**: Ollama local only — no paid API keys for LLM
- **Market data API**: Alpha Vantage free tier — 5 calls/min, 500/day
- **Budget**: Zero cost — free APIs and local tools only
- **Demo scope**: Single ticker (AAPL) end-to-end flow

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FastAPI over Express | Python backend reuses existing code, natural for numerical computations (numpy/pandas), single runtime | — Pending |
| Ollama local LLM | Zero API cost, hackathon-friendly, no external dependency | — Pending |
| Lightweight Charts (TradingView) | Professional finance rendering, open-source, perfect for hackathon demo | — Pending |
| React + Vite frontend | Fast DX, modern tooling, good ecosystem | — Pending |
| Dollar-Cost Average for Multi-Tier | Simple, intuitive, easy to visualize for demo | — Pending |
| Dynamic RQI weighting | Weight technique vs sentiment based on confidence of each analysis rather than fixed ratio | — Pending |
| Convergence-based technical confidence | Multiple indicators pointing to same level = higher confidence | — Pending |
| Source-quality sentiment confidence | Earnings calls > press releases > news articles, weighted by quantity and reliability | — Pending |
| Modern clean UI (Robinhood/Revolut style) | Accessible, non-intimidating, good for hackathon judges | — Pending |
| Free API for corporate data | Financial Modeling Prep or SEC Edgar — zero cost, hackathon constraint | — Pending |

---
*Last updated: 2026-02-09 after initialization*
