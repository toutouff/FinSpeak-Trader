# FinSpeak Trader - Claude Session Memory

> **Purpose**: This file preserves critical learnings and decisions across machines/sessions.
> On a new machine, `setup.sh` auto-copies this to Claude memory. Or manually:
> `cp .planning/MEMORY.md ~/.claude/projects/<project-key>/memory/MEMORY.md`

## Current Status (2026-02-09)
- **Branch**: `phase1&2` (pushed to GitHub)
- **Progress**: Phases 1 & 2 COMPLETE (50%), Phase 3 next
- **Tests**: 69/69 passing
- **Setup**: `./setup.sh` for fresh Mac dev env

## What's Built
### Phase 1 - Foundation & Data Pipeline (DONE)
- FastAPI app with CORS, lifespan (Ollama pre-warm, InfluxDB health)
- `GET /api/market-data/{ticker}` - InfluxDB cached OHLCV
- `GET /api/corporate-data/{ticker}` - FMP API (earnings, news, press)
- `POST /api/sentiment/analyze` - Ollama LLM with source-quality weighting
- Config via pydantic-settings, all async with httpx

### Phase 2 - Technical Analysis Engine (DONE)
- 6 TA methods in `services/ta/`: VP, S/R, RSI, MACD, Bollinger, Ichimoku
- Convergence scorer (4+ agree = boost, 1-2 agree = penalty)
- `GET /api/technical/{ticker}` - complete TA bundle
- Pure numpy/pandas/scipy (no external TA libs)

## Project Identity
- **Type**: Hackathon MVP, 1-week timeline
- **Core**: Multi-signal financial analysis engine (NOT a translation tool)
- **User**: Not a trader - relies on system intelligence for analysis

## Key Decisions
- **Backend**: FastAPI (Python) - reuses existing data pipeline
- **Frontend**: React + Vite + Tailwind CSS 4 + Lightweight Charts
- **LLM**: Ollama local (Llama 3.1 8B) - zero API cost
- **DB**: InfluxDB (existing, OHLCV for AAPL/MSFT/GOOGL/NVDA)
- **Corporate data**: Financial Modeling Prep free tier (250 req/day)
- **NO**: LangChain, Axios, MUI, pandas-ta

## Architecture
- `backend/app/main.py` → routers → services → models
- TA modules: `services/ta/{vp,sr,rsi,macd,bollinger,ichimoku,convergence}.py`
- Tests: `backend/tests/` (69 tests covering models, services, API, all TA)
- Config: `backend/app/config.py` (all keys optional with defaults)

## Roadmap
```
Phase 1 (DONE) ──────┐
                      ├──→ Phase 3 (RQI + Position) ──→ Phase 4 (Dashboard)
Phase 2 (DONE) ──────┘
```

## Critical Pitfalls
- LLM hallucination: never let LLM extract numbers, use structured data
- VP from daily data: label as "estimated", supplement with conventional S/R
- Ollama: httpx async only, pre-warm model on startup
- Scope creep: timebox features to 1 day

## How to Resume
1. `git clone` + `git checkout phase1&2` + `./setup.sh`
2. Fill `.env` with API keys
3. `claude` then `/gsd:progress` to see state
4. Phase 3 is next: RQI scoring + DCA position strategy
