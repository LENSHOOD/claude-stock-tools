# Stock Analysis Methodology

## Data Collection Strategy

### Source Priority (in order)

**Tier 1 — Primary sources (always start here for annual/quarterly financials):**
1. **Company Investor Relations website** — Official annual reports, interim reports, results announcements (most accurate, audited data)
2. **Stock Exchange filings** — HKEXnews (港股), CNINFO (A股) — official regulatory filings with complete financial statements

**Tier 2 — Financial data aggregators (for real-time price, derived metrics, supplementary data):**
3. **TradingView** — Good for HK stocks: price, market cap, P/E, P/B, dividend yield, EBITDA
4. **Google Finance** — Good for A-shares: price, P/E, P/B, balance sheet
5. **ETNet / AAStocks** — HK-specific: EPS, NBV, dividend history

**Tier 3 — Supplementary research:**
6. **Web search** — Earnings call summaries, management commentary, operating metrics, qualitative analysis
7. **Financial news sites** — Industry context, peer comparison data

**Tier 4 — Fallback:**
8. **User-provided data** — When automated sources fail, ask user to paste from broker terminal

**Key principle**: For audited annual/quarterly financials (revenue, net profit, EPS, balance sheet), ALWAYS prioritize primary sources (Tier 1). Financial aggregators may have rounding errors, currency mismatches, or delayed updates.

### Currency Handling

- HK stocks: Financials usually in RMB, stock price in HKD
- A-shares: Financials and price both in RMB
- Conversion rate: Use ~1.10 HKD/RMB (update if significantly different)
- Always state the currency used in calculations

### Fiscal Year Alignment

- Most Chinese/HK companies: FY ends December 31
- Quarterly reports: Q1 (Mar 31), Q2 interim (Jun 30), Q3 (Sep 30), Q4 (Dec 31)
- Q1 results typically released in May
- Annual results typically released in March-April
- **Always check if the latest annual report is available**

---

## Earnings Report Qualitative Analysis

Since financial reports are already fetched for quantitative analysis, extract qualitative insights from the same sources.

### Data Sources
- Latest annual report highlights / management discussion
- Earnings call transcripts or summaries
- Company press releases for the reporting period

### Key Areas to Extract

**1. Strategic Direction & Expansion Plans**
- Is the company investing heavily in expansion (stores, capacity, R&D)?
- Capital expenditure trends and future plans
- New market/product initiatives

**2. Management Commentary**
- Forward guidance and outlook
- Key priorities for the coming year
- Tone: confident, cautious, or uncertain?

**3. Abnormal Signals in Context**
- Low profitability but high capex → expansion mode (may be undervalued)
- Revenue stagnation but margin improvement → efficiency gains
- High R&D spending → future growth investment
- One-time charges masking underlying growth

**4. Risk Factors**
- New risks disclosed in the report
- Regulatory changes
- Competitive threats
- Supply chain or operational risks

### Output
A narrative section explaining what the numbers alone don't tell. This provides crucial context for interpreting the quantitative analysis in the framework sections.

---

## Valuation Frameworks

### Framework 1: Benjamin Graham — "The Intelligent Investor"

**Philosophy**: Buy stocks trading below their intrinsic value with a sufficient margin of safety. Focus on asset protection and low valuations.

**Graham Number**:
```
Graham Number = sqrt(22.5 * EPS * BVPS)
```

This represents the maximum price a defensive investor should pay. The formula assumes:
- Maximum P/E of 15
- Maximum P/B of 1.5
- Combined: P/E * P/B <= 22.5

**Seven Standards** (all must pass for Graham to buy):
1. Adequate size (large company)
2. Strong financial condition (current ratio > 2)
3. Earnings stability (profitable for 10+ consecutive years)
4. Dividend record (20+ years of uninterrupted dividends)
5. Earnings growth (33%+ growth over 10 years)
6. Moderate P/E (< 15x)
7. Moderate P/B (< 1.5x) AND P/E*P/B < 22.5

**Limitations for Chinese stocks**:
- Few Chinese companies have 20-year dividend histories
- Asset-light businesses (tech, services) will always fail P/B test
- Best applied to: banks, utilities, industrials, consumer staples

### Framework 2: Walter Schloss — "The Superinvestor of Graham-and-Doddsville"

**Philosophy**: Buy stocks below their tangible book value. Diversify widely. Hold for the long term. Let mean reversion work.

**Key Metrics**:
- Price relative to tangible book value (P/B < 1.0 preferred)
- Debt-to-equity ratio (lower is better)
- Insider ownership and buyback activity
- Earnings trend (stable or improving)
- Price relative to historical range

**Schloss's Edge**: He would also consider "special situations" — stocks with P/B > 1 but with hidden assets, strong earnings growth, or catalysts for re-rating.

**Limitations for growth stocks**:
- Schloss never bought high-P/B stocks
- Not suitable for asset-light, high-ROE businesses
- Best applied to: asset-heavy industries, holding companies, cyclical businesses

### Framework 3: Warren Buffett & Charlie Munger — "Buy Wonderful Companies at Fair Prices"

**Philosophy**: Buy companies with durable competitive advantages (moats), excellent management, and reasonable valuations. Hold for the very long term.

**Moat Assessment** (rate each 1-5):
1. **Brand**: Does the brand command premium pricing or customer loyalty?
2. **Scale Economies**: Does larger scale create cost advantages?
3. **Switching Costs**: Is it costly/difficult for customers to switch?
4. **Network Effects**: Does the product become more valuable with more users?
5. **Other**: Regulatory barriers, patents, unique resources

**Moat Rating**:
- 20-25 points: Wide moat
- 12-19 points: Narrow moat
- < 12 points: No moat

**Management Evaluation**:
- Capital allocation: buybacks, dividends, M&A track record
- Operational efficiency: margin trends
- Strategic vision: are they building for the long term?
- Shareholder alignment: insider ownership, compensation structure

**DCF Valuation**:
```
Intrinsic Value = Sum of discounted future earnings + Discounted terminal value
```

Always use 3 scenarios:
1. **Optimistic**: 10-12% EPS growth for 10 years, then 3% perpetual
2. **Zero Growth**: Current EPS forever at 3% perpetual (floor value)
3. **Pessimistic**: -3% EPS decline for 10 years, then 3% perpetual (worst case)

Discount rate: 10% (Buffett's minimum required return)

**Safety Margin**:
- Buffett typically requires 20-30% discount to intrinsic value
- Wider margin for higher uncertainty

**Inversion (Munger)**:
- Always ask: "What could go wrong?"
- List 3-5 specific risks that would destroy the thesis
- Assess probability and impact

### Framework 4: Peter Lynch — "One Up on Wall Street"

**Philosophy**: Buy what you understand. Use PEG to find growth at a reasonable price. Categorize the company first, then apply the right valuation method.

**Company Classification (Six Categories):**

| Category | Characteristics | Typical Growth Rate | Valuation Approach |
|----------|----------------|--------------------|--------------------|
| Slow Growers | Mature industries, stable dividends | 2-5% | Dividend yield focus |
| Stalwarts | Large, reliable, moderate growth | 8-12% | PE relative to growth |
| Fast Growers | Small/medium, aggressive expansion | 20%+ | PEG ratio, earnings growth sustainability |
| Cyclicals | Revenue tied to economic cycles | Variable | Peak/trough earnings analysis |
| Turnarounds | Distressed but recovering | N/A | Asset value + recovery potential |
| Asset Plays | Hidden/undervalued assets | N/A | Sum-of-parts valuation |

**PEG Ratio Analysis (for growth stocks):**
```
PEG = PE / Annual EPS Growth Rate (%)
```

| PEG Range | Interpretation | Action |
|-----------|---------------|--------|
| < 0.5 | Significantly undervalued | Strong buy signal |
| 0.5 - 1.0 | Undervalued | Buy signal |
| 1.0 - 1.5 | Fairly valued | Hold |
| 1.5 - 2.0 | Expensive | Caution |
| > 2.0 | Overvalued | Avoid |

**Lynch's Seven Key Checks:**

1. **Earnings Growth Consistency**: 5+ years of consistent EPS growth, no major misses
2. **Growth Sustainability**: Is growth driven by one-time factors or durable advantages?
3. **Debt Level**: D/E < 0.5 for fast growers (growth shouldn't rely on debt)
4. **Institutional Ownership**: Moderate (20-60%) — too low = overlooked, too high = crowded
5. **Insider Activity**: Net buying is a positive signal
6. **PEG vs Peers**: Is PEG competitive within the same industry?
7. **"Story" Clarity**: Can the investment thesis be explained in 2 minutes?

**Growth Rate Estimation:**
- Use historical 3-5 year EPS CAGR as base
- Cross-check with analyst consensus if available
- Apply hair-cut: use 80% of consensus for safety
- For very high growth (>30%), apply mean reversion: assume growth will halve within 3-5 years

**DCF with Growth Adjustment:**
- Stage 1: Current growth rate for 3-5 years
- Stage 2: Half growth rate for next 5 years
- Stage 3: 3% perpetual growth
- Discount rate: 10-12% (higher for less proven growth)

**Limitations for value/cyclical stocks:**
- Not suitable for companies with erratic earnings
- PEG meaningless for negative or declining earnings
- Best applied to: technology, consumer, healthcare, and other growth sectors

---

## Technical Analysis

Provide basic technical analysis to help users identify better entry/exit points when fundamental analysis signals buy or sell.

### Data Sources
- Google Finance for price history and chart data
- WebSearch for "{stock_code} technical analysis" or "{stock_code} 技术分析"
- Financial sites (TradingView, Investing.com, East Money) for MA and volume data

### Key Areas

**1. Trend Judgment**
- MA5, MA20, MA60 alignment (bullish/bearish/neutral)
- Current price relative to key moving averages
- Overall trend: uptrend / downtrend / consolidation

**2. Support & Resistance Levels**
- Identify 2-3 key support levels (recent lows, MA support)
- Identify 2-3 key resistance levels (recent highs, psychological levels)
- Current price position relative to these levels

**3. Volume-Price Relationship**
- Recent volume trend (increasing/decreasing)
- Volume-price divergence signals
- Breakout confirmation with volume

**4. Technical Verdict**
- If fundamental analysis → BUY: suggest optimal entry zone based on support levels
- If fundamental analysis → SELL: suggest optimal exit zone based on resistance levels
- Short-term momentum assessment

### Output
A concise technical overview table + narrative interpretation. This supplements (not replaces) the fundamental buy/sell recommendations.

---

## Buy/Sell Point Methodology

### Buy Points — Pyramid Strategy

Buy more as price drops (inverted pyramid of capital):

| Tier | Trigger | Capital % | Rationale |
|------|---------|-----------|-----------|
| 1 | Current price near 52-week low | 15% | Establish position |
| 2 | -5 to -10% from Tier 1 | 25% | Price confirmation |
| 3 | -15 to -20% from Tier 1 | 30% | Deep value zone |
| 4 | Near Graham Number | 30% | Maximum conviction |

### Sell Points — Inverted Pyramid Strategy

Sell more as price rises:

| Tier | Trigger | Sell % | Rationale |
|------|---------|--------|-----------|
| 1 | P/E reaches historical median | 20% | Lock in base profit |
| 2 | Near intrinsic value (DCF) | 25% | Fair value achieved |
| 3 | P/E exceeds historical high | 30% | Overvalued territory |
| 4 | Core position | 25% hold | Long-term compounder |

### Mandatory Sell Signals

**Yellow Warning** (reduce position by 50%):
- Moat deterioration signs
- 3 consecutive quarters of margin decline
- Management misallocation of capital
- Major regulatory changes

**Red Alert** (sell to 10% core):
- Core business fundamentally disrupted
- 2+ years of profit decline
- Management team departure (founder/key executives)
- Balance sheet deterioration

---

## Peer Comparison

Compare the current stock with 3-5 comparable companies in the same industry. This provides context for evaluating whether the stock is attractive relative to its peers.

### How to Identify Peers
1. Use WebSearch to find "{company_name} competitors" or "{company_name} 同行业竞争对手"
2. Select 3-5 companies in the same industry/sector
3. Prioritize companies of similar size and business model

### Metrics to Compare (fundamentals only)
- P/E ratio
- P/B ratio
- ROE
- Revenue growth rate (latest year)
- Net profit margin
- Dividend yield
- Market cap

### Important
- Peer companies do NOT need detailed analysis — only fetch their key metrics
- Use Google Finance or quick WebSearch for peer data
- Highlight where the current stock ranks among peers (best/worst in each metric)

---

## Report Quality Standards

1. **Data Currency**: Always use the latest available data. If FY2025 annual report exists, it MUST be included.
2. **Source Attribution**: Every data point must note its source.
3. **Currency Consistency**: State clearly what currency is used in each calculation.
4. **Three Scenarios**: DCF must always include optimistic, zero-growth, and pessimistic cases.
5. **Actionable Conclusions**: Every framework must end with a clear verdict (buy/cautious/avoid).
6. **Chinese Language**: All output in Chinese.
7. **Comparison Ready**: Generate summary.json for peer comparison feature.
