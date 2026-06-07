# Stock Investment Analysis Skill

## Purpose

Generate comprehensive stock investment analysis reports using four investing frameworks (Graham, Schloss, Buffett & Munger, Lynch). Outputs professional HTML reports in Chinese.

## Supported Markets

- **Hong Kong stocks**: e.g., 0700.HK, 06862.HK, 09987.HK
- **A-shares (China)**: e.g., 600519.SH, 000858.SZ, 300750.SZ

## Invocation

Trigger when:
- User asks to analyze a stock: "分析一下XXX"
- User asks for investment value assessment: "XXX的投资价值"
- User provides a stock code and asks for valuation: "0700估值"
- User asks to compare stocks: "对比XXX和YYY"

Arguments: `<stock_code>` (required), optional flags for comparison mode.

## Workflow

### Phase 0: Load Historical Data

**Before fetching any new data, check for existing financial data in the stock directory.**

1. **Check if stock directory exists**: `~/Documents/doc/investment_analysis/{stock_name}_{stock_code}/`
   - `{stock_name}` = company name in Chinese (e.g., `腾讯控股`)
   - `{stock_code}` = stock code with suffix (e.g., `00700.HK`, `600519.SH`)

2. **If `financials.json` exists**, read it and extract:
   - Which annual periods (FY20XX) are already stored (need 3 most recent)
   - Which quarterly periods (Q1-Q4_XXXX) are already stored
   - List of previously detected data revisions
   - Count of PDF reports already downloaded

3. **Identify data gaps**: Determine which periods need to be fetched vs. already available
   - Need 3 years of detailed financials from separate annual reports
   - Always check the latest annual report (e.g., if 2026, check FY2025)
   - Always check the latest quarterly report (e.g., Q1 2026)
   - If `financials.json` has < 3 years of detailed data, download additional annual reports
   - Only skip fetching for periods already in `financials.json` (but still verify they haven't been revised)

4. **If no `financials.json` exists**, proceed with full data collection (Phase 1)

### Phase 1: Data Collection

**CRITICAL: Always fetch the LATEST available data. If the current year is 2026, FY2025 annual report should be available. If Q1 2026 quarterly report exists, include it.**

**Multi-year reporting**: Download the **latest 3 years** of annual reports for detailed year-over-year comparison. The latest report's 5-year summary covers older periods. This enables:
- Full P&L, balance sheet, cash flow comparison across 3 years
- Trend analysis of margins, turnover, and capital structure
- Detection of data revisions between report versions

**Source priority — ALWAYS start from primary/first-hand sources, then fall back to aggregators:**

#### Tier 1: Primary Sources via MCP (优先从一手信源获取)

**filing-downloader MCP** provides direct access to stock exchange filings. These tools are the PRIMARY data source for annual/interim reports. Claude Code auto-starts the MCP server on first call — no manual startup needed.

**For HK stocks** (e.g., 0700.HK, 02313.HK):
```
Step 1: hkex_search_filings(stock_code="02313", category="annual", lang="zh")
Step 2: From the results, identify the LATEST 3 annual reports by date/title
Step 3: Download each PDF:
        hkex_download_filing(file_link=<latest_report>, output_dir=<stock_dir>, extract_text_flag=True)
        hkex_download_filing(file_link=<2nd_latest>, output_dir=<stock_dir>, extract_text_flag=True)
        hkex_download_filing(file_link=<3rd_latest>, output_dir=<stock_dir>, extract_text_flag=True)
```

**For A-shares** (e.g., 600519.SH, 000858.SZ):
```
Step 1: cninfo_search_filings(stock_code="600519", market="sh", category="annual")
Step 2: From the results, identify the LATEST 3 annual reports
Step 3: Download each PDF:
        cninfo_download_filing(adjunct_url=<latest_report>, output_dir=<stock_dir>, extract_text_flag=True)
        cninfo_download_filing(adjunct_url=<2nd_latest>, output_dir=<stock_dir>, extract_text_flag=True)
        cninfo_download_filing(adjunct_url=<3rd_latest>, output_dir=<stock_dir>, extract_text_flag=True)
```

**What to extract from EACH year's report:**
- Revenue, gross profit, operating profit, net profit
- EPS (basic and diluted), dividends per share
- Total assets, total liabilities, shareholders equity
- Cash and equivalents, total debt
- Operating metrics (segment data, geographic breakdown)
- Management discussion and strategic direction

**Older data (beyond 3 years)**: Use the 5-year financial summary found in the latest annual report (typically near the start, pages 18-22). Do NOT download reports older than 3 years.

**MCP error handling**: If the MCP tool returns an error (server not running, network issue), fall back to Tier 2 sources. Do NOT block the analysis — continue with available data.

#### Tier 1.5: Company IR Website (补充一手信源)

1. **Company Investor Relations website**:
   - Search for "{company_name} investor relations" or "{company_name} 投资者关系"
   - Look for: investor presentations, earnings call transcripts, fact sheets
   - These complement exchange filings with forward-looking commentary

#### Tier 2: Financial Data Aggregators (二手数据源，用于补充实时行情和衍生指标)

3. **TradingView** (good for HK stocks, reliable aggregated data):
   - `https://www.tradingview.com/symbols/HKEX-{code}/` for HK stocks
   - Good for: current price, market cap, P/E, P/B, dividend yield, EBITDA, 52-week range

4. **Google Finance** (for A-shares):
   - `https://www.google.com/finance/quote/{code}:SHA` or `:SHE`
   - Extract: price, market cap, PE, PB, dividend yield, EPS

5. **ETNet / AAStocks** (Hong Kong specific):
   - `https://www.etnet.com.hk/www/eng/stocks/realtime/quote.php?code={code}`
   - Good for: EPS, NBV per share, dividend history

#### Tier 3: Supplementary Research (补充定性分析和行业数据)

6. **WebSearch**:
   - Search for "{company_name} {year} annual results revenue net profit"
   - Search for "{company_name} 财报 营收 净利润"
   - Search for "{company_name} dividend buyback history"
   - Search for "{company_name} operating metrics"
   - Search for earnings call summaries, management commentary

7. **Agent subagent** (deep data collection from multiple sources):
   - Spawn a general-purpose agent to fetch from Tier 1 + Tier 2 sources in parallel
   - Focus on: annual financials (3-4 years), quarterly data, operating metrics, dividend/buyback history

#### Tier 4: Fallback

8. **User-provided data**: If critical data cannot be fetched from any source:
   - Notify user with specific gaps: "无法获取以下数据：XXX，请提供"
   - Ask user to paste data from their broker terminal or financial app
   - Continue analysis with available data + user-provided data

**Data Quality Checklist** (must have before proceeding):
- [ ] Current stock price and market cap
- [ ] P/E, P/B ratios
- [ ] 3 years of detailed financials from separate annual reports (P&L, balance sheet, cash flow)
- [ ] 5-year summary from latest report (for periods beyond the 3 downloaded reports)
- [ ] Total assets, total liabilities, shareholders equity (latest)
- [ ] EPS for all 3 years
- [ ] Shares outstanding

### Phase 1.5: Persist Financial Data

After collecting and validating data, save it to `financials.json` for future reuse:

1. **Load existing `financials.json`** (if it exists from Phase 0)
2. **Merge new data** with existing data:
   - Add new annual/quarterly periods that weren't previously stored
   - For periods that already exist, compare key figures (revenue, net_profit, EPS)
   - If numbers differ, record a revision entry and update with latest values
3. **Save updated `financials.json`** to the stock directory

**Revision detection**: If a previously stored period's revenue or net profit differs from the newly fetched data by more than 1%, log it as a revision:
```json
{ "period": "FY2024", "field": "net_profit", "old_value": 1234, "new_value": 1280, "detected_date": "2026-05-29" }
```

### Phase 2: Data Organization

Organize all collected data into these tables (will be used in the report):

1. **Stock Overview**: price, market cap, PE, PB, dividend yield, 52-week range, shares outstanding
2. **Income Statement**: revenue, gross profit, operating profit, net profit, EPS for 3-4 years
3. **Balance Sheet**: total assets, total liabilities, equity, cash, debt, BVPS
4. **Operating Metrics**: industry-specific KPIs
5. **Shareholder Returns**: dividends, buybacks history
6. **Latest Quarter**: most recent quarterly/interim data with YoY comparison

### Phase 2.5: Earnings Report Qualitative Analysis

Since financial reports are already fetched for quantitative analysis, extract qualitative insights from the same sources:

**Data Sources** (use WebSearch to find):
- Latest annual report highlights / management discussion
- Earnings call transcripts or summaries
- Company press releases for the reporting period

**Key Areas to Extract:**

1. **Strategic Direction & Expansion Plans**
   - Is the company investing heavily in expansion (stores, capacity, R&D)?
   - Capital expenditure trends and future plans
   - New market/product initiatives

2. **Management Commentary**
   - Forward guidance and outlook
   - Key priorities for the coming year
   - Tone: confident, cautious, or uncertain?

3. **Abnormal Signals in Context**
   - Low profitability but high capex → expansion mode (may be undervalued)
   - Revenue stagnation but margin improvement → efficiency gains
   - High R&D spending → future growth investment
   - One-time charges masking underlying growth

4. **Risk Factors**
   - New risks disclosed in the report
   - Regulatory changes
   - Competitive threats
   - Supply chain or operational risks

**Output**: A narrative section explaining what the numbers alone don't tell. This provides crucial context for interpreting the quantitative analysis in Phase 3.

### Phase 3: Four-Framework Analysis

#### 3.1 Graham Framework

**Graham Number:**
```
Graham Number = sqrt(22.5 * EPS * BVPS)
```
- Use Non-IFRS/adjusted EPS if available (better reflects sustainable earnings)
- If financials are in a different currency from the stock price, convert using the current exchange rate (see "Currency Handling" section). Do NOT hardcode rates.

**Seven Standard Tests:**

| # | Standard | Requirement | Check |
|---|----------|-------------|-------|
| 1 | Adequate Size | Large-cap company | Market cap check |
| 2 | Financial Strength | Current ratio > 2, low debt | Balance sheet analysis |
| 3 | Earnings Stability | Profitable every year for 10 years | Check history |
| 4 | Dividend Record | Uninterrupted dividends for 20 years | Check history |
| 5 | Earnings Growth | >33% EPS growth over 10 years | Calculate CAGR |
| 6 | Low P/E | P/E < 15 | Current PE check |
| 7 | Low P/B | P/B < 1.5 AND P/E * P/B < 22.5 | Combined check |

**Safety Margin:**
- Calculate premium/discount vs Graham Number
- Graham requires at least 33% discount (buy below 2/3 of intrinsic value)

**Conclusion**: Recommend / Cautious / Not Recommend

#### 3.2 Schloss Framework

**Selection Criteria:**

| # | Criterion | Requirement | Check |
|---|-----------|-------------|-------|
| 1 | Price vs Tangible Book | P/B < 1.0 preferred | P/B analysis |
| 2 | Debt Level | Low debt preferred | D/E ratio |
| 3 | Management Alignment | Insider ownership or buybacks | Buyback history |
| 4 | Earnings History | Stable or improving | Trend analysis |
| 5 | Price Position | Near historical lows | 52-week range |

**Asset Value Analysis:**
- Calculate tangible book value per share
- If P/B > 1, analyze what justifies the premium (ROE, growth, brand)
- Check if investment portfolio / hidden assets provide additional margin of safety

**Conclusion**: Recommend / Special Situation / Not Recommend

#### 3.3 Buffett & Munger Framework

**Moat Analysis (5 dimensions):**

| Dimension | Rating (1-5) | Evidence |
|-----------|--------------|----------|
| Brand | | |
| Scale Economies | | |
| Switching Costs | | |
| Network Effects | | |
| Regulatory/Other | | |

**Moat Rating**: Wide / Narrow / None

**Management Assessment:**
- Capital allocation track record (buybacks, dividends, M&A)
- Margin trends (operational efficiency)
- Strategic vision and execution
- Alignment with shareholders

**DCF Valuation (3 scenarios):**

Using formula: `Intrinsic Value = PV(future earnings) + PV(terminal value)`
- Discount rate: 10%
- Perpetual growth: 3%

| Scenario | Growth Rate | Period | Intrinsic Value |
|----------|-------------|--------|-----------------|
| Optimistic | 12% | 10 years | |
| Zero Growth | 0% | perpetual | |
| Pessimistic | -3% | 10 years | |

**Safety Margin** = (Intrinsic Value - Current Price) / Intrinsic Value

**Inversion (Munger's "Invert, always invert"):**
- List 3-5 scenarios that would make this a bad investment
- Assess probability and impact of each

**Conclusion**: Strong Recommend / Recommend / Cautious / Not Recommend

#### 3.4 Lynch Framework (Peter Lynch)

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

**For growth stocks (Fast Growers / Stalwarts), focus on:**

**PEG Ratio Analysis:**
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

**Lynch's Key Checks:**

| # | Check | What to Look For |
|---|-------|-----------------|
| 1 | Earnings Growth Consistency | 5+ years of consistent EPS growth, no major misses |
| 2 | Growth Sustainability | Is growth driven by one-time factors or durable advantages? |
| 3 | Debt Level | D/E < 0.5 for fast growers (growth shouldn't rely on debt) |
| 4 | Institutional Ownership | Moderate (20-60%) — too low = overlooked, too high = crowded |
| 5 | Insider Activity | Net buying is a positive signal |
| 6 | PEG vs Peers | Is PEG competitive within the same industry? |
| 7 | "Story" Clarity | Can the investment thesis be explained in 2 minutes? |

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

**Conclusion**: Strong Recommend / Recommend / Cautious / Not Recommend

### Phase 3.5: Technical Analysis

Provide basic technical analysis to help users identify better entry/exit points when fundamental analysis signals buy or sell.

**Data Sources:**
- Google Finance for price history and chart data
- WebSearch for "{stock_code} technical analysis" or "{stock_code} 技术分析"
- Financial sites (TradingView, Investing.com, East Money) for MA and volume data

**Key Areas to Analyze:**

1. **Trend Judgment**
   - MA5, MA20, MA60 alignment (bullish/bearish/neutral)
   - Current price relative to key moving averages
   - Overall trend: uptrend / downtrend / consolidation

2. **Support & Resistance Levels**
   - Identify 2-3 key support levels (recent lows, MA support)
   - Identify 2-3 key resistance levels (recent highs, psychological levels)
   - Current price position relative to these levels

3. **Volume-Price Relationship**
   - Recent volume trend (increasing/decreasing)
   - Volume-price divergence signals
   - Breakout confirmation with volume

4. **Technical Verdict**
   - If fundamental analysis → BUY: suggest optimal entry zone based on support levels
   - If fundamental analysis → SELL: suggest optimal exit zone based on resistance levels
   - Short-term momentum assessment

**Output**: A concise technical overview table + narrative interpretation. This supplements (not replaces) the fundamental buy/sell recommendations.

### Phase 4: Synthesis & Recommendations

**Cross-Framework Comparison Table:**

| Dimension | Graham | Schloss | Buffett & Munger | Lynch |
|-----------|--------|---------|-------------------|-------|
| Core Focus | Asset protection | Low P/B | Moat + Management | Growth at Reasonable Price |
| Verdict | | | | |
| Key Obstacle | | | | |
| Ideal Buy Price | | | | |

**Buy Point Recommendations:**

| Tier | Price Range | Position % | Logic |
|------|-------------|------------|-------|
| Tier 1 | | 15% | |
| Tier 2 | | 25% | |
| Tier 3 | | 30% | |
| Tier 4 | | 30% | |

**Sell Point Recommendations:**

| Tier | Price Range | Sell % | Logic |
|------|-------------|--------|-------|
| Tier 1 | | 20% | |
| Tier 2 | | 25% | |
| Tier 3 | | 30% | |
| Core | Hold | 25% | |

**Mandatory Sell Signals:**
- Yellow warning (reduce 50%): list specific triggers
- Red alert (sell to 10%): list specific triggers

### Phase 5: Peer Comparison

Compare the current stock with 3-5 comparable companies in the same industry. This provides context for evaluating whether the stock is attractive relative to its peers.

**How to identify peers:**
1. Use WebSearch to find "{company_name} competitors" or "{company_name} 同行业竞争对手"
2. Select 3-5 companies in the same industry/sector
3. Prioritize companies of similar size and business model

**Metrics to compare (fundamentals only):**
- P/E ratio
- P/B ratio
- ROE
- Revenue growth rate (latest year)
- Net profit margin
- Dividend yield
- Market cap

**Important:**
- Peer companies do NOT need detailed analysis — only fetch their key metrics
- Use Google Finance or quick WebSearch for peer data
- Highlight where the current stock ranks among peers (best/worst in each metric)

### Phase 6: Generate HTML Report

**Output directory**: `~/Documents/doc/investment_analysis/{stock_name}_{stock_code}/`
- `{stock_name}` = company name in Chinese (e.g., `腾讯控股`)
- `{stock_code}` = stock code with suffix (e.g., `00700.HK`)

**Files to generate:**
1. `{date}.html` — The analysis report named by date (e.g., `2026-05-29.html`)
2. `{date}.json` — Machine-readable report data for this analysis
3. `summary.json` — Latest report summary (overwritten each time)
4. `financials.json` — Persisted financial data (updated in Phase 1.5)
5. Open the HTML file in browser automatically

**Check for prior reports** before generating:
1. List existing `*.html` files in the stock directory
2. If prior reports exist, read the most recent `{date}.json` to get previous verdicts
3. Compare current verdicts (Graham, Schloss, Buffett, Lynch) with prior verdicts
4. If any verdict changed (e.g., Cautious → Recommend), include a "观点变化" section at the top of the report showing:
   - Which framework(s) changed
   - Previous verdict vs. current verdict
   - Brief reason for the change
5. In the report footer, list all prior report dates as links

**HTML Template**: Use `templates/report_template.html` as base

**Report Structure:**
```
0. 观点变化 (Viewpoint Changes) [only if prior reports exist and verdicts changed]
1. 公司概况 (Company Overview)
2. 核心财务数据 (Key Financial Data)
   - 利润表 (Income Statement)
   - 资产负债表 (Balance Sheet)
   - 运营指标 (Operating Metrics)
   - 股东回报 (Shareholder Returns)
3. 财报定性分析 (Earnings Report Insights)
4. 估值指标速览 (Valuation Snapshot)
5. 四大投资框架分析 (Four-Framework Analysis)
   5.1 格雷厄姆框架
   5.2 施洛斯框架
   5.3 巴菲特&芒格框架
   5.4 林奇框架
6. 技术面分析 (Technical Analysis)
7. 综合结论 (Synthesis)
   - 框架对比表
   - 买入/卖出建议
8. 行业对比 (Peer Comparison) [if applicable]
9. 历史报告 (Prior Reports) [list all prior report dates with links, if any]
10. 免责声明
```

## Reference Files

- **Methodology**: [methodology.md](./reference/methodology.md) — Detailed analysis methodology
- **HTML Template**: [report_template.html](./templates/report_template.html) — Report styling
- **HTML Generator**: [generate_html.py](./scripts/generate_html.py) — Python script to generate HTML from data

## Currency Handling (货币换算)

**CRITICAL: When financial report data and stock market data are in different currencies, you MUST look up the correct exchange rate and apply it consistently throughout the report.**

### Step 1: Identify Currencies

Before any analysis, determine:
1. **Financial statement currency** — Check the annual report. HK-listed companies may report in USD, RMB, or HKD. Look for "currency" or "列报货币" in the financial statements header.
2. **Stock price currency** — HK stocks trade in HKD. A-shares trade in RMB.
3. **Are they the same?** If yes, no conversion needed. If no, proceed to Step 2.

**Common scenarios:**
| Stock | Financial Currency | Price Currency | Conversion Needed |
|-------|-------------------|----------------|-------------------|
| 00700.HK (腾讯) | RMB | HKD | Yes (RMB → HKD) |
| 00316.HK (东方海外) | USD | HKD | Yes (USD → HKD) |
| 600519.SH (茅台) | RMB | RMB | No |

### Step 2: Look Up Current Exchange Rate

**Do NOT hardcode or guess exchange rates.** Use WebSearch to find the current rate:
- Search: `"USD to HKD"` or `"RMB to HKD"` or `"USD to RMB"`
- Verify from 2+ sources if possible (Google Finance, XE.com, etc.)
- Record the rate and its source in `financials.json`

### Step 3: Apply Consistently

Once you have the correct rate:
1. **Record it** in `financials.json` as `exchange_rate` with source
2. **Apply uniformly** to ALL conversions — Graham Number, DCF, narrative text, tables
3. **Label every converted figure** with both currencies, e.g., "US$32.03 (HK$249.2)"
4. **Never mix rates** — use the same rate for the entire report

### Step 4: Verify

After generating the report, double-check:
- All HKD values in tables = USD/RMB values × correct rate
- Narrative text mentions of converted values match the tables
- The exchange rate used is documented in the report or `financials.json`

## Quality Standards

- **Annual/quarterly financials must come from primary sources first** (filing-downloader MCP → HKEX/CNINFO filings → company IR website). Only fall back to financial aggregators (TradingView, Google Finance) for real-time price and derived metrics.
- All financial data must cite source with tier level (Tier 1: primary, Tier 2: aggregator, etc.)
- `financials.json` must record the source for each data point so future analyses can verify data quality
- Use Non-IFRS/adjusted earnings for valuation when available (better for Chinese tech companies)
- Always include the latest available quarterly data
- DCF must use 3 scenarios (optimistic, zero-growth, pessimistic)
- **Graham Number must use consistent currency** — look up the current exchange rate if financials and stock price are in different currencies (see "Currency Handling" section above). Never hardcode exchange rates.
- Investment portfolio value should be analyzed separately for companies with significant holdings
- Report must be in Chinese
- HTML must be self-contained (inline CSS, no external dependencies)
