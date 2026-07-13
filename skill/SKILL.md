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

**DCF Valuation (6 scenarios — 3 standard + 3 adjusted):**

Using formula: `Intrinsic Value = PV(future earnings) + PV(terminal value)`
- Discount rate: 10%
- Terminal perpetual growth: 3%

**Standard scenarios** (baseline, use as universal reference):

| Scenario | Growth Rate | Period | Intrinsic Value |
|----------|-------------|--------|-----------------|
| Optimistic | 12% | 10 years | |
| Zero Growth | 0% | perpetual | |
| Pessimistic | -3% | 10 years | |

**Adjusted scenarios** (dynamic, based on stock-specific factors):

Adjust growth rates based on the company's Lynch category, industry cycle position, recent earnings trend, and market conditions. Examples:
- Mature industry / slow grower (e.g., cement, utilities): Optimistic +3~5%, Pessimistic -5~8%
- Cyclical near trough: Optimistic +5~8%, Pessimistic -8~15%
- High-growth tech: Optimistic +20~30%, Pessimistic +3~5%

| Scenario | Growth Rate | Period | Rationale |
|----------|-------------|--------|-----------|
| Adjusted Optimistic | *(dynamic)* | 10 years | Based on company-specific growth potential |
| Adjusted Zero | 0% | perpetual | Unchanged |
| Adjusted Pessimistic | *(dynamic)* | 10 years | Based on industry/market downside risk |

In the report output, label the standard scenarios as "标准DCF" and adjusted scenarios as "修正DCF". Include both sets in the DCF table so readers can compare universal baseline with stock-specific estimates.

**Safety Margin** = (Intrinsic Value - Current Price) / Intrinsic Value

**Buffett's PR Ratio (巴菲特市赚率):**

PR measures "how much price you pay for how much earning power." It captures the relationship between valuation (PE) and profitability (ROE).

```
PR = PE / ROE
```

Where ROE is the percentage value (e.g., 30% → use 30, not 0.30).

| PR Range | Interpretation |
|----------|---------------|
| < 0.4 | Deep discount (4折), strong buy |
| 0.4 - 0.5 | Significant discount (4-5折), buy |
| 0.5 - 0.6 | Moderate discount (5-6折), buy |
| 0.6 - 1.0 | Slight discount (6折-平价), hold/accumulate |
| 1.0 - 1.5 | Slightly overvalued, caution |
| > 1.5 | Overvalued, avoid |

**ROE Stability Adjustment:**
- Use multi-year average ROE (3-5 years) if annual ROE is volatile
- If ROE is stable (annual variation < 3pp), use latest year ROE

**Shareholder Return Coefficient (股东回报系数):**
Considering dividends + buybacks, apply a coefficient to adjust PR:

| Dividend + Buyback Payout Ratio | Coefficient | Rationale |
|----------------------------------|-------------|-----------|
| ≥ 50% | 1.0 | Generous returns, no adjustment needed |
| 25% - 50% | 1.25 | Moderate returns, slight penalty |
| ≤ 25% | 2.0 | Low returns, double the PR (less attractive) |

```
Adjusted PR = PR × Coefficient
```

**Buyback Data Collection (mandatory for PR calculation):**

Before computing the payout ratio, you MUST check for buyback activity:

1. **Check annual report** — Search for "股份回购" or "回购股份" section, typically in "重要事项" or "股份变动及股东情况" (usually pages 60-75). Extract:
   - Buyback plan amount and share count
   - Actual buyback shares and amount spent
   - Purpose: 注销 (cancellation) vs 员工持股/股权激励 (employee holding)
   - Cancellation buybacks are more valuable (reduces share count permanently)

2. **Estimate buyback cost** if not explicitly stated:
   - If shares cancelled: cost ≈ buyback shares × average price during buyback period
   - If buyback plan specifies amount range: use midpoint as estimate

3. **Calculate total shareholder return:**
   ```
   Total Return = Dividends + Buyback Cost
   Payout Ratio = Total Return / Net Profit to Parent
   ```

4. **Apply buyback-adjusted metrics:**
   - Cancellation buyback → recalculate EPS with reduced share count
   - Show both pre-buyback and post-buyback EPS
   - Show PE reduction from buyback

**Calculation steps in the report:**
1. Show current PE and latest ROE → base PR
2. Show 3-5 year average ROE → conservative PR
3. **Collect buyback data from annual report** → estimate buyback cost
4. Show dividend + buyback payout ratio → determine coefficient
5. Show final adjusted PR (both base and conservative)
6. **Show buyback-adjusted EPS and PE** (for cancellation buybacks)
7. Interpret: how much "discount" the current price represents
8. **Show total shareholder return rate** (dividend yield + buyback yield)

**Conclusion**: Strong Recommend / Recommend / Cautious / Not Recommend (integrate with overall Buffett verdict)

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

**CRITICAL: You MUST fetch actual K-line data before making ANY technical analysis claims. Do NOT assume or guess volume trends, moving average positions, or support/resistance levels. Every claim must be backed by real data.**

**Step 1: Fetch K-line data via East Money API (mandatory)**

Use Bash to call the East Money API and get the last 20-60 trading days of daily data:

```bash
# A-shares (secid=1.{code} for SH, secid=0.{code} for SZ)
curl -s "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.600219&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=1&end=20260713&lmt=60"

# HK stocks (secid=116.{code})
curl -s "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=116.00700&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=1&end=20260713&lmt=60"
```

Parse the response: each kline entry is "date,open,close,high,low,volume,turnover" (volume in shares, turnover in CNY).

**Step 2: Calculate indicators from actual data**

Use Python to compute from the fetched data:

```python
# Moving averages (compute from close prices)
MA5 = average of last 5 closes
MA10 = average of last 10 closes
MA20 = average of last 20 closes

# Volume analysis
vol_ma5 = average of last 5 days volume
vol_ma10 = average of last 10 days volume
volume_ratio = vol_ma5 / vol_ma10  # >1 = expanding, <1 = contracting

# Trend determination
if price < MA5 < MA10 < MA20: "空头排列"
elif price > MA5 > MA10 > MA20: "多头排列"
else: "混合排列"
```

**Step 3: Make claims ONLY supported by data**

| What to check | How | What NOT to say without data |
|---------------|-----|------------------------------|
| Volume trend | Compute vol_ma5/vol_ma10 ratio | Don't say "放量" or "缩量" without calculating the ratio |
| MA alignment | Compare MA5, MA10, MA20 values | Don't say "多头排列" or "空头排列" without computing |
| Support/Resistance | Look at recent lows/highs in actual data | Don't invent price levels without checking |
| Price vs MAs | Compute (price - MA)/MA percentage | Don't say "接近支撑" without quantifying |

**Key Areas to Analyze:**

1. **Trend Judgment** (requires actual MA calculation)
   - MA5, MA10, MA20 alignment (bullish/bearish/neutral) — compute from data
   - Current price relative to key moving averages — compute percentage
   - Overall trend: uptrend / downtrend / consolidation — based on MA slopes

2. **Support & Resistance Levels** (requires actual price history)
   - Identify 2-3 key support levels from recent lows in actual data
   - Identify 2-3 key resistance levels from recent highs in actual data
   - Current price position relative to these levels

3. **Volume-Price Relationship** (requires actual volume data)
   - Compute volume ratio (vol_ma5 / vol_ma10) to determine expanding/contracting
   - Identify volume spikes relative to volume MA
   - Check for volume-price divergence

4. **Technical Verdict**
   - If fundamental analysis → BUY: suggest optimal entry zone based on actual support levels
   - If fundamental analysis → SELL: suggest optimal exit zone based on actual resistance levels
   - Short-term momentum assessment based on computed indicators

**Output**: A concise technical overview table with ACTUAL computed values + narrative interpretation. Every claim must reference the data source (e.g., "MA5=4.03, 低于MA5 2.4%").

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
