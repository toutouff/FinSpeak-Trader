# Feature Research

**Domain:** Financial analysis platform combining NLP-powered corporate communication analysis with technical trading intelligence
**Researched:** 2026-02-09
**Confidence:** MEDIUM (based on competitive landscape analysis, multiple sources, and domain-specific research)

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Interactive price chart** | Every financial platform shows a price chart. Without one, there is nothing to anchor the analysis to. Users expect candlestick/OHLC display with zoom, pan, and time range selection. | MEDIUM | TradingView Lightweight Charts is the right tool (45KB, Apache 2.0, canvas-based). Already a project decision. Must support at minimum: candlestick series, time range selector, responsive layout. |
| **Ticker search/selection** | Users need to specify what they are analyzing. Even with single-ticker demo, the UI pattern must exist. | LOW | For hackathon MVP: dropdown or search box pre-populated with AAPL. Hardcoded is fine for demo but the UI affordance must exist. |
| **Corporate text display** | If the product claims to translate corporate communications, the original text must be visible alongside the translation. Users need to see what was decoded. | LOW | Side-by-side or toggle view. Source text + translated text. Must show which document type (earnings call, press release, news). |
| **Plain English translation output** | The core promise. Users expect clear, jargon-free summaries of corporate communications. Without this, the product has no identity. | HIGH | Requires: Ollama LLM integration, prompt engineering for financial jargon decoding, structured output format. This is the hardest table-stakes feature because LLM quality directly determines perceived product quality. |
| **Sentiment indicator** | Users expect to know "is this bullish or bearish?" at a glance. Every competitor (AlphaSense, SentimenTrader, Danelfin) provides this. A color-coded positive/negative/neutral signal is minimum. | MEDIUM | Can be derived from LLM analysis output. Color coding (green/yellow/red) is expected. Must include sentiment score, not just label. AlphaSense uses color-coded text highlighting; Danelfin uses 1-10 scores. |
| **Loading/processing states** | LLM analysis takes time. Users must see progress indicators, not frozen screens. Financial users are especially impatient. | LOW | Skeleton loaders, progress bars, or step indicators ("Fetching earnings call... Analyzing sentiment... Calculating entry points..."). |
| **Data freshness indicator** | Users need to know when data was last updated. Stale financial data is dangerous. Shows "Last updated: [timestamp]" and data source. | LOW | Display fetch timestamp for market data and corporate data. Critical for trust. |
| **Mobile-responsive layout** | Judges and demo viewers may use phones/tablets. Robinhood/Revolut style implies mobile-first thinking. | MEDIUM | Not a native app, but responsive CSS. Chart must resize. Key metrics must be visible on mobile without horizontal scroll. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Risk Quantification Index (RQI)** | No competitor combines technical analysis confidence + sentiment analysis confidence into a single dynamic-weighted score. Danelfin scores 1-10 but uses fixed weighting. RQI dynamically weights based on confidence of each input -- if technical signals are strong but sentiment data is sparse, technical gets more weight. This is novel. | HIGH | Core differentiator. Requires: (1) technical confidence calculation from convergence of multiple indicators, (2) sentiment confidence calculation weighted by source quality (earnings calls > press releases > news), (3) dynamic weighting algorithm, (4) clear visual presentation (gauge, score card, or similar). Dependencies: Volume Profile Analysis + Sentiment Analysis must both work first. |
| **Source-quality-weighted sentiment** | Most competitors treat all text sources equally. FinSpeak explicitly weights by reliability: earnings call transcripts (management speaking directly, legally accountable) > press releases (company-controlled narrative) > financial news (third-party interpretation). This mirrors how professional analysts think. | MEDIUM | Requires: classifying input source type, assigning quality multiplier, displaying the weighting rationale to users. This is defensible because it encodes domain expertise that generic NLP tools miss. Research confirms FinBERT analysis shows earnings call soft information is as informative as earnings surprises (UC Berkeley, FactSet studies). |
| **Volume Profile entry zones with convergence-based confidence** | Goes beyond "here is a support level." Multiple technical methods (VWAP, VPOC, Value Area High/Low, key moving averages) are computed independently, and where they converge = higher confidence entry zone. Most retail platforms show one indicator at a time. Convergence visualization is rare outside institutional tools. | HIGH | Requires: (1) VPOC calculation, (2) Value Area (VAH/VAL) calculation, (3) VWAP, (4) key MAs (50/200), (5) convergence detection algorithm, (6) confidence scoring based on number of methods agreeing within a price band. TradingView Lightweight Charts supports custom plugins for overlay rendering. |
| **Multi-tier DCA position plan** | Instead of "buy here," the system says "build a position across these 3-5 levels with these allocation percentages." This is how professional traders actually operate but retail tools rarely suggest it. Translates complex position management into a simple visual plan. | MEDIUM | Depends on Volume Profile entry zones. Algorithm: distribute allocation across identified levels inversely weighted by distance from current price and directly weighted by confidence score. Output: table showing price level, allocation %, confidence, and rationale. |
| **Jargon-to-meaning annotation** | Beyond full translation: highlight specific corporate phrases and show what they actually mean inline. "We are exploring strategic alternatives" -> "We might sell the company." This micro-level decoding is what corporate jargon decoders do, but none connect it to financial analysis. | MEDIUM | LLM prompt engineering to identify and annotate specific phrases. Display as tooltips or inline annotations on the source text. Competitors like PlainSpeak and Corporate Speak Translator do this generically but never in a financial analysis context connected to trading decisions. |
| **Analysis narrative** | Instead of just showing numbers/charts, generate a 2-3 paragraph human-readable analysis tying the sentiment, technical levels, and RQI together. "Apple's latest earnings call was cautiously optimistic (sentiment: 0.72). Management's language around iPhone sales was notably hedged compared to last quarter. Meanwhile, the volume profile shows strong support at $182 with 3 technical indicators converging. The RQI of 7.2 suggests moderate confidence in an entry at current levels." | MEDIUM | Uses LLM to synthesize all analysis outputs into coherent narrative. High demo impact. Depends on all other analysis features completing first. This is what differentiates from a dashboard of disconnected widgets. |
| **Explainable scoring (show your work)** | Danelfin uses "Explainable AI" as a selling point. Users can see which factors drive the score. FinSpeak should show: which technical indicators agreed, which sentiment sources contributed, how the weights were assigned. Transparency builds trust, especially for non-traders who do not understand the underlying methods. | LOW | UI component showing breakdown: "RQI 7.2 = Technical (8.1, weight 60%) + Sentiment (5.8, weight 40%). Technical confidence high because VPOC, 200MA, and VAL converge within $2. Sentiment confidence moderate: 1 earnings call analyzed, 2 press releases, 0 news articles." |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Real-time streaming data** | "Financial platforms need live data." | Alpha Vantage free tier: 5 calls/min. Real-time requires WebSocket infrastructure, streaming state management, and constant API usage. Massive complexity for hackathon. Stale-by-seconds data provides zero additional value for the daily-timeframe analysis FinSpeak performs. | Use daily OHLCV data already in InfluxDB. Show "as of market close [date]" timestamp. The analysis is about corporate communications + volume profiles, not tick-by-tick trading. |
| **Trade execution / brokerage integration** | "Let users act on recommendations directly." | Brokerage API integration (Alpaca, Interactive Brokers) requires: OAuth flows, order management, error handling for partial fills, regulatory compliance. 1-week hackathon killer. Also shifts liability -- recommending entries is different from executing trades. | Show entry plan as exportable information. "Here is where and how much to buy" without a buy button. Future consideration post-hackathon. |
| **Multi-ticker comparison** | "Compare AAPL vs MSFT sentiment side by side." | Multiplies every computation by N. LLM analysis is slow (local Ollama). Volume profile calculation is per-ticker. UI complexity doubles. Already explicitly out of scope in PROJECT.md. | Perfect single-ticker experience first. The demo flow for one ticker is the hackathon deliverable. Multi-ticker is v2. |
| **Historical pattern tracking** | "Show how sentiment changed over last 4 quarters." | Requires: historical earnings transcripts (API availability uncertain), temporal sentiment storage, trend visualization, and significantly more LLM processing time. Scope explosion. | Show current analysis only. One earnings call, current price data. Flag as future roadmap item. |
| **User accounts and saved analyses** | "Let users save their analyses and come back later." | Auth system (even basic) adds: user model, session management, database schema, login UI, password handling. Zero value for hackathon demo. Already out of scope in PROJECT.md. | Stateless demo. Each visit runs fresh analysis. No persistence needed. |
| **Backtesting** | "Prove the RQI score predicts outcomes." | Requires historical RQI calculations, outcome tracking, statistical validation framework. SentimenTrader charges hundreds/month for this. Enormous scope. | Show the methodology is sound through transparency (explainable scoring). Backtesting is a v2+ feature that requires months of historical data collection first. |
| **Social/community features** | "Let users share analyses or discuss." | Chat, comments, user profiles, moderation -- entirely different product category. Distracts from core analytical value. | Not even on the roadmap. The product is an analysis tool, not a social platform. |
| **Push notifications / alerts** | "Notify me when RQI changes or new earnings drop." | Requires: background processing, notification infrastructure (email/push), user preferences, alert configuration UI. | Out of scope. The demo is a pull model: user opens app, sees analysis. |

## Feature Dependencies

```
[Market Data Pipeline (existing)]
    |
    +---> [Interactive Price Chart]
    |         |
    |         +---> [Volume Profile Entry Zones]
    |                    |
    |                    +---> [Multi-Tier DCA Position Plan]
    |                    |
    |                    +---> [Technical Confidence Score] ---+
    |                                                          |
[Corporate Data Pipeline (new)]                                |
    |                                                          |
    +---> [Corporate Text Display]                             |
    |         |                                                |
    |         +---> [Plain English Translation] (LLM)          |
    |                    |                                     |
    |                    +---> [Jargon-to-Meaning Annotations]  |
    |                    |                                     |
    |                    +---> [Sentiment Analysis]             |
    |                              |                           |
    |                              +---> [Source-Quality       |
    |                                     Weighted Sentiment] --+
    |                                                          |
    |                                          +---------------+
    |                                          |
    |                                          v
    |                                   [RQI Score]
    |                                          |
    |                                          +---> [Explainable Scoring]
    |                                          |
    |                                          +---> [Analysis Narrative]
    |
    +---> [Data Freshness Indicator]

[Ticker Search/Selection] ---> (gates all above features for chosen ticker)
[Loading States] ---> (required by all async features)
[Mobile-Responsive Layout] ---> (required by all UI features)
```

### Dependency Notes

- **Volume Profile Entry Zones requires Market Data Pipeline:** OHLCV data must be queryable from InfluxDB before any technical analysis can run. This dependency is already satisfied for AAPL.
- **Plain English Translation requires Corporate Data Pipeline:** Cannot translate text that has not been fetched. The corporate data pipeline (earnings transcripts, press releases) is the biggest new infrastructure piece.
- **RQI requires both Technical Confidence + Sentiment Confidence:** The dynamic weighting algorithm needs both inputs. If either pipeline fails, RQI degrades to single-signal mode (still functional, but less differentiated).
- **Analysis Narrative requires all analysis outputs:** This is the final synthesis step. It depends on sentiment, technical analysis, and RQI all being computed. Build last.
- **Multi-Tier DCA Position Plan requires Volume Profile Entry Zones:** Cannot distribute position allocation without identified price levels.
- **Jargon-to-Meaning Annotations enhance Plain English Translation:** Not a hard dependency but meaningless without the translation existing.

## MVP Definition

### Launch With (v1 -- Hackathon Demo)

Minimum viable product -- what's needed for a compelling 1-ticker demo.

- [ ] **Interactive price chart (AAPL)** -- visual anchor for the entire demo, first thing judges see
- [ ] **Corporate data pipeline** -- fetch at least 1 earnings call transcript for AAPL via free API (Financial Modeling Prep or SEC EDGAR)
- [ ] **Plain English translation** -- the core promise; Ollama + engineered prompt translating corporate jargon
- [ ] **Sentiment indicator** -- bullish/bearish/neutral with score, derived from LLM output
- [ ] **Volume Profile entry zones** -- at minimum VPOC + Value Area overlay on chart
- [ ] **RQI score** -- combined technical + sentiment confidence with visual display
- [ ] **Loading states** -- essential UX for LLM processing time (5-30 seconds per analysis)
- [ ] **Ticker selector (AAPL pre-selected)** -- UI affordance even if only one ticker works

### Add After Validation (v1.x -- If Time Remains in Hackathon Week)

Features to add once core is working.

- [ ] **Multi-tier DCA position plan** -- add if Volume Profile and RQI are solid; high demo impact
- [ ] **Jargon-to-meaning annotations** -- add if Plain English Translation quality is good; enhances wow factor
- [ ] **Source-quality weighted sentiment** -- add if multiple source types are available; strengthens RQI narrative
- [ ] **Analysis narrative** -- add as polish layer; ties everything together for the demo pitch
- [ ] **Explainable scoring breakdown** -- add if RQI is implemented; transparency is a strong demo talking point
- [ ] **Data freshness indicator** -- quick win, adds credibility

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Multi-ticker support** -- requires scaling all pipelines; post-hackathon priority #1
- [ ] **Historical sentiment tracking** -- needs quarters of data; post-hackathon
- [ ] **Backtesting framework** -- needs historical RQI data; months of collection first
- [ ] **Trade execution integration** -- brokerage API; regulatory considerations
- [ ] **Portfolio-level insights** -- requires multi-ticker + user accounts
- [ ] **Mobile native app** -- responsive web is sufficient until user base justifies

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Interactive price chart | HIGH | MEDIUM | P1 |
| Corporate data pipeline | HIGH | MEDIUM | P1 |
| Plain English translation (LLM) | HIGH | HIGH | P1 |
| Sentiment indicator | HIGH | MEDIUM | P1 |
| Volume Profile entry zones | HIGH | HIGH | P1 |
| RQI score | HIGH | HIGH | P1 |
| Loading/processing states | MEDIUM | LOW | P1 |
| Ticker selector | MEDIUM | LOW | P1 |
| Multi-tier DCA plan | HIGH | MEDIUM | P2 |
| Jargon annotations | MEDIUM | MEDIUM | P2 |
| Source-quality sentiment weighting | MEDIUM | MEDIUM | P2 |
| Analysis narrative | HIGH | MEDIUM | P2 |
| Explainable scoring | MEDIUM | LOW | P2 |
| Data freshness indicator | LOW | LOW | P2 |
| Mobile-responsive layout | MEDIUM | MEDIUM | P2 |
| Multi-ticker support | HIGH | HIGH | P3 |
| Historical sentiment tracking | MEDIUM | HIGH | P3 |
| Backtesting | MEDIUM | HIGH | P3 |

**Priority key:**
- P1: Must have for hackathon demo launch
- P2: Should have, add if time permits during hackathon week
- P3: Post-hackathon, future consideration

## Competitor Feature Analysis

| Feature | AlphaSense | Danelfin | SentimenTrader | TradingView | FinSpeak (Our Approach) |
|---------|------------|----------|----------------|-------------|-------------------------|
| NLP earnings analysis | Deep search + AI summaries across millions of docs. Enterprise-grade. | Not a focus (uses sentiment indicators, not text analysis) | Not a focus (market-level sentiment, not text-level) | Not available | Local LLM (Ollama) translating individual documents. Simpler but zero-cost and privacy-preserving. |
| Sentiment scoring | Color-coded text highlighting with numerical sentiment change scores | 1-10 AI Score combining 150 sentiment indicators | 2800+ proprietary sentiment indicators | Community-built indicators | Source-quality-weighted sentiment from LLM analysis. Novel weighting approach. |
| Technical analysis | Not a focus (research platform, not trading tool) | 600+ technical indicators, AI-scored | Technical indicators combined with sentiment | Full charting platform with 100+ indicators | Volume Profile focus with convergence-based confidence. Narrow but deep. |
| Combined score | No unified score | AI Score (1-10) with sub-scores for technical, fundamental, sentiment. Fixed weighting. | No unified score | No unified score | RQI with dynamic weighting based on input confidence. Novel approach. |
| Entry recommendations | No | Top stock picks based on AI Score | Market-level timing signals | No (charting only) | Specific price levels with confidence and allocation plan. Actionable. |
| Target user | Professional analysts, institutional investors | Retail and semi-pro investors | Professional traders | All traders | Non-trader investors wanting to understand corporate communications |
| Pricing | Enterprise ($10K+/year) | Free tier + $17-50/month premium | $250+/month | Free tier + $15-60/month | Free (hackathon demo, local LLM) |
| Plain English translation | No (shows raw text with highlights) | No | No | No | **Core differentiator.** No competitor decodes corporate jargon into plain language AND connects it to trading intelligence. |

### Competitive Positioning Summary

FinSpeak occupies a unique niche: none of the major competitors translate corporate communications into plain English AND connect those translations to technical entry recommendations with a unified confidence score. AlphaSense is closest on the NLP side but targets institutional analysts and costs $10K+/year. Danelfin is closest on the scoring side but does not analyze corporate text. The combination is novel, especially at zero cost with local LLM.

## Sources

- [AlphaSense - AI Tools for Earnings Analysis](https://www.alpha-sense.com/resources/product-articles/ai-tools-earnings-analysis/) -- MEDIUM confidence, official product marketing
- [Danelfin - How It Works](https://danelfin.com/how-it-works) -- HIGH confidence, official product documentation
- [SentimenTrader - Indicators & Tools](https://sentimentrader.com/indicators-backtest-tools) -- MEDIUM confidence, official product site
- [TradingView Lightweight Charts](https://tradingview.github.io/lightweight-charts/) -- HIGH confidence, official documentation
- [FactSet - Interpreting Earnings Calls with NLP](https://insight.factset.com/interpreting-earnings-calls-with-natural-language-processing) -- MEDIUM confidence, industry research
- [UC Berkeley - Assessing Predictive Power of Earnings Call Transcripts](https://www.ischool.berkeley.edu/projects/2024/assessing-predictive-power-earnings-call-transcripts-next-day-stock-price-movement) -- MEDIUM confidence, academic research
- [LuxAlgo - NLP in Trading](https://www.luxalgo.com/blog/nlp-in-trading-can-news-and-tweets-predict-prices/) -- MEDIUM confidence, industry blog
- [Volume Profile Trading Guide](https://www.trusted-broker-reviews.com/volume-profile/) -- LOW confidence, educational content
- [Danelfin Review 2026](https://www.wallstreetzen.com/blog/danelfin-review/) -- MEDIUM confidence, independent review
- [AI Tools for Financial Analysis 2026](https://www.analyticsinsight.net/artificial-intelligence/which-ai-tools-are-best-for-financial-analysis-in-2026) -- LOW confidence, industry roundup
- [Hudson Labs - AI Earnings Call Tools](https://www.hudson-labs.com/post/top-6-ai-tools-for-summarizing-earnings-calls) -- MEDIUM confidence, competitor analysis
- [Fintech Trends 2026](https://innowise.com/blog/fintech-trends/) -- LOW confidence, industry trends

---
*Feature research for: Financial analysis platform with NLP-powered corporate communication analysis + technical trading intelligence*
*Researched: 2026-02-09*
