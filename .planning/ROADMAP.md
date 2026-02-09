# Roadmap: FinSpeak Trader

## Overview

FinSpeak Trader delivers a multi-signal financial analysis engine that combines NLP sentiment scoring with technical analysis convergence into a dynamic Risk Quantification Index (RQI) with actionable entry recommendations. The roadmap builds the analytical engine first (data pipelines, LLM sentiment, and technical analysis in parallel), then unifies them through RQI scoring and position strategy, and finally surfaces everything through a React dashboard for end-to-end demo on AAPL. Four phases, with Phases 1 and 2 executing in parallel to maximize the 1-week hackathon timeline.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation & Data Pipeline** - FastAPI skeleton, market data API, corporate data fetcher, Ollama LLM sentiment engine
- [ ] **Phase 2: Technical Analysis Engine** - Six TA methods with convergence-based confidence scoring [PARALLEL with Phase 1]
- [ ] **Phase 3: RQI Scoring & Position Strategy** - Dynamic-weighted composite score, multi-tier entry plan, analysis narrative
- [ ] **Phase 4: Dashboard & End-to-End Demo** - React frontend, all UI panels, orchestration endpoint, full AAPL demo flow

## Phase Details

### Phase 1: Foundation & Data Pipeline
**Goal**: A running FastAPI backend that serves cached market data, fetches corporate communications, and produces LLM-powered sentiment scores from earnings transcripts
**Depends on**: Nothing (first phase)
**Parallel**: Phase 2 can start once project skeleton and data service layer are committed
**Requirements**: DATA-01, DATA-02, DATA-03, SENT-01, SENT-02
**Success Criteria** (what must be TRUE):
  1. Hitting GET /api/market-data/AAPL returns cached OHLCV JSON from InfluxDB without calling Alpha Vantage
  2. Hitting GET /api/corporate-data/AAPL returns at least one earnings transcript with source-type metadata (earnings call, press release, or news article)
  3. Hitting POST /api/sentiment/analyze with corporate text returns a sentiment object containing direction (bullish/neutral/bearish), numeric score, and confidence value -- with zero fabricated financial numbers in the output
  4. Sentiment confidence is observably higher for earnings call text than for news article text when tested with equivalent content
**Plans**: TBD (1-3 plans)

Plans:
- [ ] 01-01: TBD
- [ ] 01-02: TBD
- [ ] 01-03: TBD

### Phase 2: Technical Analysis Engine
**Goal**: A computational engine that calculates six independent technical analysis signals from OHLCV data and scores their convergence into a unified technical confidence metric
**Depends on**: Phase 1 (project skeleton and data service layer only -- can start in parallel once skeleton exists)
**Parallel**: Runs alongside Phase 1 after project structure is established
**Requirements**: TECH-01, TECH-02, TECH-03, TECH-04, TECH-05, TECH-06, TECH-07
**Success Criteria** (what must be TRUE):
  1. Calling the Volume Profile service with AAPL data returns VPOC, Value Area High, and Value Area Low price levels that fall within the recent trading range
  2. Calling the technical analysis suite for AAPL returns signals from all six methods: Volume Profile, Support/Resistance, RSI, MACD, Bollinger Bands, and Ichimoku Cloud
  3. Each method returns its own signal (bullish/neutral/bearish) with a numeric confidence value
  4. The convergence scorer produces a higher confidence when 4+ methods agree on direction than when only 1-2 agree
  5. Hitting GET /api/technical/AAPL returns the complete technical analysis bundle as JSON
**Plans**: TBD (1-3 plans)

Plans:
- [ ] 02-01: TBD
- [ ] 02-02: TBD
- [ ] 02-03: TBD

### Phase 3: RQI Scoring & Position Strategy
**Goal**: A unified scoring system that dynamically weighs technical and sentiment signals into an explainable Risk Quantification Index, paired with a multi-tier entry plan at identified price levels
**Depends on**: Phase 1 and Phase 2 (requires both sentiment and technical outputs)
**Requirements**: RQI-01, RQI-02, RQI-03, RQI-04, POS-01, POS-02, SENT-03
**Success Criteria** (what must be TRUE):
  1. Calling the RQI service with AAPL's technical and sentiment outputs returns a composite score between 0-100 that maps to a human-readable category (High Risk / Moderate / Low Risk)
  2. The RQI score visibly shifts when sentiment confidence is artificially set to low (technical gets more weight) vs high (sentiment gets more weight) -- demonstrating dynamic weighting
  3. The scoring breakdown shows which indicators contributed and their individual weights, so a user can understand why the score is what it is
  4. The entry builder returns a multi-tier DCA plan with 3-5 price levels, each with a recommended allocation percentage that sums to 100%
  5. An analysis narrative of 2-3 paragraphs ties together sentiment findings, technical signals, and the RQI score into a coherent trading context summary
**Plans**: TBD (1-3 plans)

Plans:
- [ ] 03-01: TBD
- [ ] 03-02: TBD

### Phase 4: Dashboard & End-to-End Demo
**Goal**: A React frontend that displays all analysis results in a modern fintech UI, backed by a single orchestration endpoint that computes everything for AAPL end-to-end
**Depends on**: Phase 3 (all backend analysis must be complete)
**Requirements**: UI-01, UI-02, UI-03, UI-04, UI-05, INT-01, INT-02
**Success Criteria** (what must be TRUE):
  1. Opening the app in a browser shows a clean fintech-style dashboard with a ticker selector defaulting to AAPL
  2. Clicking "Analyze" triggers the orchestration endpoint and displays a loading state with progress indicator while LLM inference runs (5-30 seconds)
  3. After loading completes, the dashboard displays all five panels: sentiment results, technical analysis signals, RQI score with breakdown, multi-tier entry plan, and analysis narrative
  4. Every displayed data element shows a freshness timestamp indicating when it was computed
  5. The full end-to-end flow works reliably for AAPL: from button click to complete analysis display with no manual intervention
**Plans**: TBD (1-3 plans)

Plans:
- [ ] 04-01: TBD
- [ ] 04-02: TBD
- [ ] 04-03: TBD

## Progress

**Execution Order:**
Phases 1 and 2 execute in parallel. Phase 3 starts after both complete. Phase 4 follows Phase 3.

```
Phase 1 ──────┐
               ├──→ Phase 3 ──→ Phase 4
Phase 2 ──────┘
```

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Data Pipeline | 0/TBD | Not started | - |
| 2. Technical Analysis Engine | 0/TBD | Not started | - |
| 3. RQI Scoring & Position Strategy | 0/TBD | Not started | - |
| 4. Dashboard & End-to-End Demo | 0/TBD | Not started | - |
