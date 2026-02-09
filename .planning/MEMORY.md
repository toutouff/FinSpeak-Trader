# FinSpeak Trader - Claude Session Memory

> **Purpose**: This file preserves critical learnings and decisions across machines/sessions.
> When starting a new Claude Code session on another machine, reference this file to restore context.
> Copy this to your local Claude memory: `~/.claude/projects/<project-key>/memory/MEMORY.md`

## Project Identity
- **Type**: Hackathon MVP, 1-week timeline
- **Core**: Multi-signal financial analysis engine (NOT a translation tool)
- **User**: Not a trader - relies on system intelligence for analysis

## Key Decisions
- **Backend**: FastAPI (Python) - reuses existing data pipeline
- **Frontend**: React + Vite + Tailwind CSS 4 + Lightweight Charts
- **LLM**: Ollama local (Llama 3.1 8B Instruct recommended) - zero API cost
- **DB**: InfluxDB (existing, OHLCV data for AAPL/MSFT/GOOGL/NVDA)
- **Corporate data**: Financial Modeling Prep free tier (250 req/day)
- **State mgmt**: Zustand + TanStack Query (not Redux)
- **NO**: LangChain, Axios, MUI, pandas-ta (removed from GitHub)

## Architecture Priority
1. Analytical engine FIRST (phases 1-3), UI LAST (phase 4)
2. Plain English Translation = v1.5 (not v1!) - user considers it polish
3. Candlestick chart = v1.5 - user wants analysis data, not chart overlays
4. 5 TA methods in v1: Volume Profile, S/R, RSI+MACD, Bollinger, Ichimoku
5. RQI = dynamic weighting based on confidence of each signal source

## Critical Pitfalls (from research)
- LLM hallucination: never let LLM extract numbers, use structured data
- VP from daily data: label as "estimated", supplement with conventional S/R
- Alpha Vantage: 25 req/day free tier - cache EVERYTHING
- Ollama: use httpx async (not requests), pre-warm model, streaming responses
- Scope creep: daily checkpoints, timebox features to 1 day

## Roadmap (4 phases)
```
Phase 1 (Foundation + Data Pipeline) ──────┐
                                            ├──→ Phase 3 (RQI + Position) ──→ Phase 4 (Dashboard + E2E)
Phase 2 (Technical Analysis Engine) ───────┘
```

- Phase 1: FastAPI + market data API + corporate data fetch + LLM sentiment (5 reqs)
- Phase 2: 6 TA methods + convergence scoring (7 reqs) — PARALLEL with Phase 1
- Phase 3: RQI dynamic scoring + DCA entries + narrative (7 reqs) — after 1+2
- Phase 4: React dashboard + orchestration + full AAPL demo (7 reqs) — last

## Files Structure
- `.planning/PROJECT.md` - project context & core value
- `.planning/REQUIREMENTS.md` - 26 v1 requirements with REQ-IDs
- `.planning/ROADMAP.md` - 4 phases (1+2 parallel → 3 → 4)
- `.planning/STATE.md` - current progress tracker
- `.planning/research/` - STACK, FEATURES, ARCHITECTURE, PITFALLS, SUMMARY
- `.planning/config.json` - YOLO mode, quick depth, parallel, quality models

## GSD Workflow Config
- Mode: YOLO (auto-approve)
- Depth: Quick (3-5 phases)
- Parallel: Yes
- Research + Plan Check + Verifier: All enabled
- Models: Opus for research/planning, Sonnet for coding, Haiku for simple tasks

## How to Resume on Another Machine
1. `git pull` to get latest
2. Copy `.planning/MEMORY.md` content to `~/.claude/projects/<project-key>/memory/MEMORY.md`
3. Run `/gsd:progress` to see current state
4. Run `/gsd:plan-phase N` for the next unplanned phase
