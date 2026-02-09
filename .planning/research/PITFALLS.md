# Pitfalls Research

**Domain:** Financial analysis platform with NLP corporate text translation + technical trading indicators
**Researched:** 2026-02-09
**Confidence:** MEDIUM-HIGH (domain-specific pitfalls well-documented; Ollama/financial-LLM intersection is newer territory)

## Critical Pitfalls

### Pitfall 1: LLM Hallucination of Financial Numbers and Sentiment

**What goes wrong:**
Ollama local models generate plausible-sounding financial figures, percentages, or sentiment conclusions that have no grounding in the actual corporate filing. A model might state "revenue grew 12.3%" when the actual figure is 8.7%, or flip the sentiment of a hedged statement entirely. Because LLM-generated numbers *look* authoritative, users (and downstream calculations like RQI) treat fabricated data as fact.

**Why it happens:**
General-purpose LLMs lack specialized financial knowledge. Smaller models available for local Ollama deployment (7B-13B parameter range) hallucinate more frequently than frontier models, especially on domain-specific numerical extraction. Financial language is deliberately ambiguous -- corporate hedging phrases like "substantially all" or "materially impacted" are designed to be vague, and models frequently resolve ambiguity confidently rather than flagging uncertainty.

**How to avoid:**
- Never use the LLM to extract numerical values. Parse numbers programmatically from structured XBRL/JSON data, then pass them to the LLM only for contextual interpretation.
- Constrain LLM output with structured response formats (JSON schema) that force categorical answers (bullish/neutral/bearish) rather than freeform financial claims.
- Include explicit system prompt instructions: "Do not generate specific financial figures. Reference only the numbers provided in the input context."
- Add a confidence field to every LLM response and treat low-confidence outputs as "unable to determine" rather than guessing.

**Warning signs:**
- LLM output contains specific numbers not present in the input text.
- Sentiment scores are consistently extreme (always very bullish or very bearish) rather than nuanced.
- Comparing LLM output against the same prompt run twice produces different numerical claims.

**Phase to address:**
Phase 1 (LLM integration). This must be validated before any downstream calculation (RQI, DCA tiers) can be trusted. Build a test harness with 5-10 known earnings excerpts and expected outputs before connecting to the pipeline.

---

### Pitfall 2: Volume Profile from Daily OHLCV Data Produces Misleading Support/Resistance Levels

**What goes wrong:**
Volume Profile is designed to distribute volume across price levels within a trading session. With daily OHLCV data, you only have one bar per day with a single open/high/low/close range. The entire day's volume gets allocated across that range using some approximation (uniform distribution, or concentrated at close), rather than reflecting where trading actually occurred. This produces volume nodes that don't correspond to real institutional support/resistance, which makes the resulting entry points unreliable.

**Why it happens:**
Proper Volume Profile requires intraday tick or minute-level data to know how much volume traded at each price level. Daily data forces you to estimate -- typically by uniformly distributing volume across the high-low range or weighting it toward close. During high-volatility days (earnings, gaps), this estimation becomes grossly inaccurate. Even 1-minute data can produce large errors during panic-selling sessions; daily data is orders of magnitude worse.

**How to avoid:**
- Acknowledge this limitation explicitly in the UI and documentation: "Volume Profile approximated from daily data -- not equivalent to intraday VP."
- Use a triangular distribution (peak at VWAP or typical price = (H+L+C)/3) rather than uniform distribution across the daily range, which is slightly more realistic.
- Supplement VP with conventional support/resistance (prior highs/lows, moving averages) to cross-validate zones. Do not use VP as the sole entry signal.
- For the demo (AAPL), consider pre-loading a small intraday dataset (even 1 week of 5-minute bars from a free source) to demonstrate what real VP looks like, alongside the daily approximation.
- Label VP-derived levels as "estimated value areas" rather than "confirmed support/resistance."

**Warning signs:**
- VP nodes land at prices where daily candle bodies don't cluster (the approximation is creating phantom levels).
- High-volume VP nodes consistently appear at round numbers or candle midpoints rather than at meaningful price action.
- Backtesting entries from VP levels shows no better performance than random entry.

**Phase to address:**
Phase 2 (Technical Analysis Engine). This must be resolved in the VP calculation module before the DCA entry tiers consume VP output. Building DCA tiers on unreliable VP levels compounds the error.

---

### Pitfall 3: Alpha Vantage Free Tier Bottleneck Stalls Development and Demo

**What goes wrong:**
Alpha Vantage's free tier allows only 25 API requests per day and 5 per minute. During active development -- iterating on data ingestion, testing different endpoints, debugging response formats -- you burn through 25 requests in minutes. On demo day, a single full data refresh for one ticker could consume multiple requests (daily prices, fundamental data, earnings). If the API quota is exhausted mid-demo, the application fails live.

**Why it happens:**
The free tier used to be 500/day, then 100/day, now 25/day. Developers often start building assuming they can iterate freely, then discover mid-development that they're locked out until the next day. The existing populate script fetches 4 tickers with full history -- that's 4 requests just for price data, plus waits of 15 seconds between calls.

**How to avoid:**
- Cache aggressively from day 1. Store all API responses locally (JSON files or directly to InfluxDB) on first fetch. Never re-fetch data you already have.
- Build a data access layer that checks local cache before making any API call. Use file-based caching during development, InfluxDB for the running app.
- Pre-populate all demo data on day 1-2 of the hackathon. For AAPL demo, fetch once and commit the raw data to the repo as a fixture.
- Use SEC EDGAR (free, no API key needed, no daily limit) for corporate filings/earnings data instead of Alpha Vantage fundamental endpoints.
- Consider Finnhub as a supplementary source (60 requests/minute free tier) for real-time quotes if Alpha Vantage is exhausted.

**Warning signs:**
- Getting `"Note": "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day"` in API responses.
- Development velocity drops because you're waiting until tomorrow for more API calls.
- Populate script takes 60+ seconds due to mandatory delays between requests.

**Phase to address:**
Phase 0 (Infrastructure / Data Pipeline). Solve the data sourcing strategy before writing any analysis logic. The existing `influx-populate-script.py` should be the first thing hardened with caching.

---

### Pitfall 4: Ollama Model Response Time Blocks FastAPI and Destroys UX

**What goes wrong:**
Local LLM inference on consumer hardware takes 5-60+ seconds depending on model size and prompt length. If the FastAPI endpoint calls Ollama synchronously, the entire server blocks during inference -- no other requests are served. The React frontend shows a spinner for 30 seconds, the user assumes the app is broken, and on demo day this looks like a failure. Worse, if multiple requests queue up (page load triggers multiple analyses), the server becomes completely unresponsive.

**Why it happens:**
Default Ollama integration tutorials use synchronous HTTP calls. FastAPI is async-capable, but beginners often use the synchronous `requests` library which blocks the event loop. Additionally, Ollama unloads models after 5 minutes of inactivity, so the first request after idle time incurs a cold-start penalty (model loading into VRAM) that can add 10-30 seconds. With 7B models on 8GB VRAM, expect 10-20 seconds per response; 13B+ models are slower.

**How to avoid:**
- Use `httpx` with async/await (not `requests`) for all Ollama API calls in FastAPI.
- Implement streaming responses: Ollama supports token streaming. Stream partial results to the frontend so users see text appearing within 1-2 seconds, even if the full response takes 15 seconds.
- Set `keepalive: -1` (or a long duration) to prevent model unloading between requests.
- Pre-warm the model on server startup with a dummy prompt so the first real request doesn't incur cold-start.
- Add a loading state in the React frontend with progress indication ("Analyzing corporate filing...") rather than a generic spinner.
- For the demo, pre-compute LLM results for AAPL and serve cached results, with live inference available as a fallback.

**Warning signs:**
- FastAPI health check endpoint stops responding during LLM inference.
- Frontend requests time out with 504 Gateway Timeout.
- Model load messages appear in Ollama logs on every request (model is being unloaded/reloaded).

**Phase to address:**
Phase 1 (Backend API + LLM Integration). The async architecture must be correct from the first endpoint. Retrofitting sync-to-async is painful.

---

### Pitfall 5: Scope Creep Kills the 1-Week Hackathon

**What goes wrong:**
The feature list (Plain English Translator + Volume Profile + RQI Scoring + DCA Multi-Tier + React Charts + Free API Integration) is ambitious for a 1-week hackathon. Each feature has hidden complexity: VP needs calculation logic, RQI needs weighting calibration, DCA needs tier computation, the LLM needs prompt engineering, the frontend needs chart integration. Attempting to build all features to completion results in nothing being demo-ready -- half-finished features everywhere.

**Why it happens:**
Financial analysis projects are seductive because each feature sounds simple in concept ("just calculate a weighted score") but has deep domain complexity. The RQI alone requires defining what inputs feed it, how to weight them, how confidence affects weighting, and how to normalize across different data scales. A non-trader building this must research each concept before implementing it, doubling the time estimate.

**How to avoid:**
- Define a ruthless MVP: one ticker (AAPL), one earnings release, one complete flow from corporate text input to chart with entry recommendations. If this works end-to-end on day 5, add polish. If not, cut features.
- Implement features in vertical slices (full stack for one feature) rather than horizontal layers (all backend, then all frontend). A working demo of one feature beats a broken demo of five.
- Timebox each feature to 1 day. If VP calculation isn't working after 1 day, simplify to conventional support/resistance and move on.
- Hard-code what you can for the demo. If RQI weighting calibration takes too long, use fixed weights and document them as "v1 defaults."
- The LLM integration is the differentiator -- protect time for it. VP and DCA are technical implementations that can be simplified; the "plain English translator" is the unique value.

**Warning signs:**
- Day 3 and no endpoint returns real data to the frontend yet.
- Spending hours researching financial formulas instead of writing code.
- Multiple partially-started features with none producing visible output.
- The temptation to add "just one more indicator" or "multi-ticker support."

**Phase to address:**
Every phase. Build the project plan with explicit cut lines: "If behind schedule at checkpoint X, drop feature Y." The roadmap must include daily milestones with go/no-go criteria.

---

### Pitfall 6: RQI Score Without Calibration Is Meaningless

**What goes wrong:**
The Risk Quantification Index combines technical indicators with NLP sentiment into a single score. Without calibration against known outcomes, the score is an arbitrary number. A score of 72 means nothing if you haven't validated that scores above 70 historically correlate with favorable outcomes. Users (and demo judges) will immediately ask "what does this score mean?" and "how accurate is it?" -- if the answer is "we made up the formula," credibility collapses.

**Why it happens:**
Composite scoring systems require backtesting or at minimum expert calibration. The weighting between technical and sentiment components is subjective. Dynamic confidence-based weighting adds another layer of complexity -- how much should low LLM confidence reduce the sentiment weight? These are research questions, not engineering questions, and they eat time.

**How to avoid:**
- Start with a simple, transparent formula: `RQI = 0.5 * technical_score + 0.5 * sentiment_score` with both components normalized to 0-100. Document the formula visibly in the UI.
- Map RQI ranges to human-readable categories: 0-30 = High Risk, 31-60 = Moderate, 61-100 = Low Risk. Users understand categories better than raw numbers.
- Use confidence as a display modifier, not a weighting modifier for v1. Show "RQI: 65 (Moderate Risk) -- Confidence: Medium" rather than trying to dynamically adjust the score.
- For the demo, pre-validate the formula against 3-5 historical AAPL earnings events. Show the judges: "Here's what our RQI said before the last 3 earnings, and here's what actually happened."
- Explicitly disclaim: "RQI is a demonstration metric, not financial advice."

**Warning signs:**
- RQI produces the same score range regardless of input (the formula is insensitive to meaningful differences).
- Negative inputs (bearish sentiment + weak technicals) somehow produce high RQI scores (formula bug).
- Time spent debating weighting schemes exceeds time spent coding.

**Phase to address:**
Phase 3 (Scoring and Integration). Build VP and LLM as separate working modules first. RQI integrates them -- so it must come after both are producing valid output.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hard-coded AAPL ticker throughout codebase | Faster demo development | Every function needs refactoring for multi-ticker | Hackathon MVP only -- parameterize from day 1 if possible |
| Synchronous Ollama calls | Simpler code, fewer imports | Server blocks during inference, unusable with concurrent users | Never -- async is the same effort with httpx |
| Storing LLM prompts as inline strings | Quick iteration | Prompts scattered across codebase, hard to tune | First 2 days only -- extract to prompt templates by day 3 |
| Skipping input validation on financial data | Faster endpoint development | Division by zero on missing volume, NaN propagation through calculations | Hackathon only -- add basic null checks at minimum |
| Using InfluxDB Flux queries with string interpolation | Faster query building | Injection vulnerability, hard to parameterize | Acceptable for local demo, must fix before any deployment |
| Pre-computing all LLM results and serving cached | Demo runs instantly | No live inference capability demonstrated | Acceptable for demo backup, but show live inference as primary path |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Alpha Vantage API | Calling API during every page load / not caching | Fetch once into InfluxDB or local JSON, serve from cache. Treat API as a batch import tool, not a real-time source |
| SEC EDGAR API | Not setting User-Agent header, getting blocked | SEC requires `User-Agent: CompanyName ContactEmail` header. No API key needed, but requests without proper UA get rate-limited or rejected |
| Ollama API | Using `requests.post()` in async FastAPI handler | Use `httpx.AsyncClient` with `await`. Set timeout to 120+ seconds. Enable streaming for UX |
| InfluxDB writes | Writing points one at a time in a loop | Batch writes (already done in existing script -- good). Also: don't use `range(start: 0)` in queries; specify a reasonable time range to avoid scanning entire DB |
| Lightweight Charts + React | Creating chart instance in render cycle, causing duplicate charts | Use `useRef` for chart instance, `useEffect` for creation/cleanup. Chart must be created once and updated, not recreated |
| Lightweight Charts Volume Profile | Expecting built-in VP support | VP is a plugin, not core. Must use the plugin system. The plugin requires price-level data, not just OHLCV -- you need to pre-compute the volume distribution and pass it as plugin data |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Loading full OHLCV history into frontend memory | Page load takes 5+ seconds, browser tab uses 500MB+ RAM | Paginate or window the data server-side. For charts, send only the visible range + buffer. For AAPL with 20+ years daily data (~6000 points), this is manageable, but will break with multiple tickers | > 10 tickers or intraday data |
| Ollama inference per request without caching | Every analysis takes 10-30 seconds, server handles 1 request at a time | Cache LLM results by input hash. Same earnings text = same analysis. Invalidate cache only when input changes | > 2 concurrent users |
| InfluxDB Flux queries without time bounds | Query scans entire bucket history, takes 10+ seconds | Always specify `range(start: -1y)` or narrower. The existing script uses `range(start: 0)` which means "scan everything" | > 50K data points per ticker |
| Re-computing VP/RQI on every frontend render | Calculations run on every React state change | Compute VP/RQI server-side, return as part of API response. Frontend only renders results, never computes financial logic | Any interactive UI |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Exposing Alpha Vantage API key in frontend code or git history | Key theft, quota exhaustion by others | Key stays in backend `.env` only. The existing script uses `dotenv` correctly. Ensure `.env` is in `.gitignore`. Check git history for accidental commits |
| InfluxDB token with full admin access used in application | Compromised app = full DB access, data deletion | Create a read-only token for the FastAPI app. Keep admin token only for the populate script |
| No input sanitization on ticker symbol parameter | Flux injection via crafted ticker string in InfluxDB query | Validate ticker against allowlist (for MVP, literally `["AAPL"]`). Never interpolate user input directly into Flux queries |
| Serving Ollama API directly to frontend | Users can send arbitrary prompts, abuse compute resources | Ollama should only be accessible from FastAPI backend. Do not expose port 11434 to frontend or public network |
| Trusting LLM output for financial display without sanitization | XSS if LLM generates HTML/script in its response | Strip HTML from all LLM output before rendering. Use React's default JSX escaping (don't use `dangerouslySetInnerHTML`) |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Showing raw RQI number without context | Users don't know if 65 is good or bad | Show categorical labels (Low/Medium/High Risk) with color coding. Add a visual gauge or dial |
| LLM analysis loads with no progress feedback | User stares at blank screen for 15-30 seconds, assumes app is broken | Stream LLM tokens to frontend. Show "Analyzing..." with animated indicator. Display partial results as they arrive |
| Volume Profile chart without explanation | Non-traders see horizontal bars and don't understand what they represent | Add inline tooltips: "High volume node = price level where significant trading occurred = likely support/resistance" |
| Displaying financial data without timestamps | User doesn't know if they're looking at current or stale data | Show "Data as of: 2026-02-07" on every data display. Mark stale data (>1 day old) with a warning |
| All analysis on one screen without hierarchy | Information overload, user doesn't know where to start | Structure as a flow: 1) Corporate text translation, 2) Technical analysis, 3) Risk score, 4) Entry recommendations. Guide the user through the story |
| Entry price recommendations without disclaimers | Perceived as financial advice, liability risk for demo | Always display: "For educational/demonstration purposes only. Not financial advice." Make it prominent, not fine print |

## "Looks Done But Isn't" Checklist

- [ ] **LLM Translation:** Output looks coherent but has not been validated against known-good interpretations -- verify against 5 manually annotated earnings excerpts
- [ ] **Volume Profile:** Chart renders VP bars but the underlying distribution uses uniform allocation across H-L range -- verify by checking if VP output changes meaningfully with different price distributions
- [ ] **RQI Score:** Score displays a number but the formula has not been tested with edge cases -- verify: what happens when sentiment is unavailable? When volume is zero? When all inputs are identical?
- [ ] **DCA Entry Tiers:** Tiers are computed but are not validated against the current price -- verify: are all tiers below current price (for long entry)? Is tier spacing reasonable relative to average daily range?
- [ ] **API Data Freshness:** Data displays correctly but is actually from the initial cache load days ago -- verify: check timestamps on displayed data, confirm refresh mechanism works
- [ ] **Error Handling:** App works with good data but crashes silently on API failures -- verify: disconnect from InfluxDB, kill Ollama, use invalid ticker -- does the app show useful error messages?
- [ ] **Frontend Chart:** Candlestick chart renders but VP plugin overlay is not connected to real VP data -- verify: does the VP overlay update when you change the analysis period?
- [ ] **End-to-End Flow:** Each component works in isolation but the pipeline from "paste earnings text" to "see entry recommendations" has never been run end-to-end -- verify: run the full flow manually on day 4 at latest

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| LLM hallucinating numbers | LOW | Add post-processing validation: regex-extract numbers from LLM output and cross-reference against input. Flag mismatches. Can be added as middleware |
| VP from daily data is misleading | MEDIUM | Simplify to "price level significance" using close-price clustering rather than full VP. Still valuable, less misleading. Rename from "Volume Profile" to "Price Activity Zones" |
| Alpha Vantage quota exhausted | LOW | Switch to cached data immediately. Use SEC EDGAR for fundamental data (no quota). For price data, use Yahoo Finance unofficial API as emergency backup (less reliable, but no quota) |
| FastAPI blocked by sync Ollama calls | MEDIUM | Replace `requests` with `httpx.AsyncClient`. Requires changing every Ollama call site but is mechanical refactoring, not architectural |
| Scope creep -- too many features, nothing works | HIGH | Triage immediately: pick the 1-2 features closest to working, abandon the rest. For demo, hard-code/mock the abandoned features with realistic static data |
| RQI produces meaningless scores | LOW | Switch to categorical output: "Based on [sentiment] and [technical levels], this setup appears [favorable/neutral/unfavorable]." Removes the burden of a calibrated number |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| LLM hallucination of financial data | Phase 1: LLM Integration | Run 5 test prompts against known earnings, compare output to expected interpretations. Zero fabricated numbers in output |
| VP from daily data inaccuracy | Phase 2: Technical Analysis | Compare VP output against manually identified S/R levels for AAPL. VP nodes should cluster near known institutional levels |
| Alpha Vantage rate limit | Phase 0: Infrastructure/Data | Verify all demo data is cached locally. Run demo without internet connection -- it should work |
| Ollama blocking FastAPI | Phase 1: Backend API | Load test: send 3 concurrent requests. All should receive responses (even if queued). Health endpoint responds < 100ms during inference |
| Scope creep | Every phase (daily checkpoints) | Day 3 checkpoint: can you demo one complete flow (text in, recommendations out) for AAPL? If no, cut features immediately |
| RQI without calibration | Phase 3: Integration | Show RQI output for 3 known historical AAPL events. Scores should directionally match actual outcomes (bearish event = higher risk score) |
| SEC EDGAR data parsing | Phase 0-1: Data Pipeline | Successfully parse and display key metrics from one AAPL 10-Q filing. Numbers match what appears on sec.gov |
| Frontend chart rendering | Phase 4: Frontend | Chart loads in < 2 seconds. VP overlay renders. Zoom/pan works. No duplicate chart instances on re-render |
| Stale data display | Phase 4: Frontend | All data displays include timestamps. Data older than 24 hours shows a staleness warning |
| Missing error handling | Phase 3-4: Integration/Frontend | Deliberately break each dependency (kill Ollama, disconnect InfluxDB, exhaust API quota). App shows informative error, does not crash |

## Sources

- [Alpha Vantage API Limits](https://www.macroption.com/alpha-vantage-api-limits/) -- MEDIUM confidence: verified across multiple sources that free tier is 25 requests/day
- [Volume Profile Complete Guide](https://www.jumpstarttrading.com/volume-profile/) -- HIGH confidence: authoritative trading education source on VP data requirements
- [LLM Hallucinations in Financial Services](https://biztechmagazine.com/article/2025/08/llm-hallucinations-what-are-implications-financial-institutions) -- MEDIUM confidence: industry analysis of LLM financial risks
- [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) -- HIGH confidence: official SEC documentation
- [LLM Financial Report Summarization Study](https://arxiv.org/html/2411.06852v1) -- MEDIUM confidence: academic research showing LLM accuracy rates on financial documents
- [Ollama + FastAPI Integration Patterns](https://medium.com/@simeon.emanuilov/ollama-with-fastapi-7f43cf532c43) -- MEDIUM confidence: community best practices for timeout/async handling
- [InfluxDB Schema Design Best Practices](https://docs.influxdata.com/influxdb3/cloud-serverless/write-data/best-practices/schema-design/) -- HIGH confidence: official InfluxData documentation
- [Lightweight Charts Volume Profile Plugin](https://tradingview.github.io/lightweight-charts/plugin-examples/plugins/volume-profile/example/) -- HIGH confidence: official TradingView documentation
- [FINOS AI Governance - Hallucination Risks](https://air-governance-framework.finos.org/risks/ri-4_hallucination-and-inaccurate-outputs.html) -- MEDIUM confidence: financial industry AI governance framework
- [Detecting LLM Hallucinations in Finance](https://www.packtpub.com/en-us/newsletters/how-to-tutorials/detecting-addressing-llm-hallucinations-in-finance) -- MEDIUM confidence: technical tutorial with practical mitigation strategies

---
*Pitfalls research for: FinSpeak Trader -- Financial NLP + Technical Trading Analysis Platform*
*Researched: 2026-02-09*
