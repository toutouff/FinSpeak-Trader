# Requirements: FinSpeak Trader

**Defined:** 2026-02-09
**Core Value:** Build a multi-signal financial analysis engine that combines technical analysis convergence with NLP sentiment scoring into a dynamic, confidence-weighted risk index (RQI) and actionable entry recommendations.

## v1 Requirements

Requirements for hackathon MVP (1 week). Each maps to roadmap phases.

### Data Pipeline

- [ ] **DATA-01**: Backend serves cached OHLCV market data from InfluxDB via REST API endpoint
- [ ] **DATA-02**: Backend fetches corporate earnings/news from free API (Financial Modeling Prep or SEC EDGAR)
- [ ] **DATA-03**: Corporate data includes source-type metadata (earnings call, press release, news article)

### Sentiment Analysis

- [ ] **SENT-01**: Ollama local LLM analyzes corporate text and produces sentiment score (bullish/neutral/bearish with numeric value)
- [ ] **SENT-02**: Sentiment confidence varies by source quality (earnings calls > press releases > news articles)
- [ ] **SENT-03**: Analysis narrative generated — 2-3 paragraph synthesis tying sentiment findings to trading context

### Technical Analysis

- [ ] **TECH-01**: Volume Profile calculation (VPOC, Value Area High, Value Area Low) from daily OHLCV data
- [ ] **TECH-02**: Support/Resistance level identification from historical price action
- [ ] **TECH-03**: RSI (Relative Strength Index) calculation with overbought/oversold signals
- [ ] **TECH-04**: MACD (Moving Average Convergence Divergence) with signal line crossovers
- [ ] **TECH-05**: Bollinger Bands calculation (upper, middle, lower bands + squeeze detection)
- [ ] **TECH-06**: Ichimoku Cloud computation (Tenkan-sen, Kijun-sen, Senkou Span A/B, Chikou Span)
- [ ] **TECH-07**: Convergence-based confidence scoring — multiple independent methods pointing to same level = higher confidence

### Position Building

- [ ] **POS-01**: Multi-tier Dollar-Cost Average entry plan across identified price levels
- [ ] **POS-02**: Each entry tier includes recommended allocation percentage and price level

### Risk Scoring (RQI)

- [ ] **RQI-01**: Risk Quantification Index computes composite score (0-100) combining technical + sentiment
- [ ] **RQI-02**: Dynamic weighting — confidence of each analysis source determines its weight in RQI
- [ ] **RQI-03**: Explainable scoring breakdown showing which indicators contributed and their weights
- [ ] **RQI-04**: Score maps to human-readable categories (High Risk / Moderate / Low Risk)

### Frontend / UX

- [ ] **UI-01**: Modern clean fintech UI (Robinhood/Revolut style) built with React + Vite + Tailwind
- [ ] **UI-02**: Loading states with progress indicators during LLM inference (5-30 seconds)
- [ ] **UI-03**: Ticker selector UI affordance (AAPL for demo, extensible)
- [ ] **UI-04**: Data freshness timestamps on all displayed data
- [ ] **UI-05**: Dashboard displaying all analysis results (sentiment, TA signals, RQI, entry plan)

### Integration

- [ ] **INT-01**: End-to-end analysis flow for single ticker (AAPL) — all signals computed and displayed
- [ ] **INT-02**: FastAPI orchestration endpoint combining market data + sentiment + all TA methods + RQI

## v1.5 Requirements

Minor update — UI enhancements, no structural changes.

- **PET-01**: Plain English Translator — corporate jargon decoded into clear language via Ollama
- **PET-02**: Side-by-side display of original corporate text and plain English translation
- **PET-03**: Jargon-to-meaning inline annotations (tooltips on specific phrases)
- **CHART-01**: Interactive candlestick price chart via Lightweight Charts (TradingView)
- **CHART-02**: Volume Profile overlay on chart (VPOC, VAH, VAL lines)
- **CHART-03**: Technical indicator overlays (Bollinger Bands, Ichimoku Cloud, S/R levels)
- **UI-06**: Responsive mobile-friendly layout

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Pattern Recognition

- **PATN-01**: Fibonacci retracement level identification
- **PATN-02**: Candlestick pattern recognition (engulfing, doji, hammer, etc.)
- **PATN-03**: Chart pattern detection (head & shoulders, double top/bottom, etc.)

### Scale

- **SCALE-01**: Multi-ticker analysis support
- **SCALE-02**: Historical sentiment tracking across quarters
- **SCALE-03**: Backtesting framework for RQI validation

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Real-time streaming data | Alpha Vantage free tier can't support it, analysis is daily-timeframe |
| User authentication | Zero demo value, adds complexity without hackathon benefit |
| Trade execution | Brokerage APIs add regulatory complexity |
| Mobile app | Web-first, responsive deferred to v1.5 |
| Social/community features | Different product category entirely |
| CI/CD pipeline | Not needed for hackathon |
| Production deployment | Local demo only |
| Portfolio-level insights | Requires multi-ticker (v2) |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | — | Pending |
| DATA-02 | — | Pending |
| DATA-03 | — | Pending |
| SENT-01 | — | Pending |
| SENT-02 | — | Pending |
| SENT-03 | — | Pending |
| TECH-01 | — | Pending |
| TECH-02 | — | Pending |
| TECH-03 | — | Pending |
| TECH-04 | — | Pending |
| TECH-05 | — | Pending |
| TECH-06 | — | Pending |
| TECH-07 | — | Pending |
| POS-01 | — | Pending |
| POS-02 | — | Pending |
| RQI-01 | — | Pending |
| RQI-02 | — | Pending |
| RQI-03 | — | Pending |
| RQI-04 | — | Pending |
| UI-01 | — | Pending |
| UI-02 | — | Pending |
| UI-03 | — | Pending |
| UI-04 | — | Pending |
| UI-05 | — | Pending |
| INT-01 | — | Pending |
| INT-02 | — | Pending |

**Coverage:**
- v1 requirements: 26 total
- Mapped to phases: 0
- Unmapped: 26

---
*Requirements defined: 2026-02-09*
*Last updated: 2026-02-09 after initial definition*
