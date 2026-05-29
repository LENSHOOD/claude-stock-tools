# claude-stock-tools

Claude Code tools for stock investment analysis. Combines a **skill** (analysis framework) and an **MCP server** (filing downloader) in one repo.

## What's Included

### stock-analysis skill
Generates comprehensive investment analysis reports using four frameworks:
- **Graham** — Asset protection, margin of safety
- **Schloss** — Low P/B, asset value investing
- **Buffett & Munger** — Moat analysis, DCF valuation
- **Lynch** — PEG ratio, growth at reasonable price

Supports Hong Kong stocks and A-shares. Outputs self-contained HTML reports in Chinese.

### filing-downloader MCP server
Direct access to stock exchange filings:
- **HKEX** (Hong Kong Stock Exchange) — annual/interim reports
- **CNINFO** (巨潮资讯网) — A-share annual/quarterly reports

## Prerequisites

- Python >= 3.13 (`brew install python@3.13`)
- Claude Code CLI

## Quick Start

```bash
git clone <repo-url> claude-stock-tools
cd claude-stock-tools
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Create a Python venv and install MCP dependencies
2. Symlink the skill to `~/.claude/skills/stock-analysis`
3. Register the MCP server with Claude Code (user scope)

Then restart Claude Code.

## Manual Installation

If you prefer not to use the setup script:

### 1. Install MCP server

```bash
cd mcp
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Register MCP with Claude Code

```bash
claude mcp add --scope user filing-downloader -- \
  $(pwd)/.venv/bin/python -m filing_downloader.server
```

### 3. Install skill

```bash
ln -s $(pwd)/skill ~/.claude/skills/stock-analysis
```

## Usage

```
分析一下02313
0700的投资价值
600519估值
```

Reports are saved to `~/Documents/doc/investment_analysis/{stock_name}_{stock_code}/`.

## Structure

```
claude-stock-tools/
├── README.md
├── setup.sh                        # One-click install
├── .gitignore
├── skill/                          # Claude Code skill
│   ├── SKILL.md                    # Skill definition & workflow
│   ├── reference/
│   │   └── methodology.md          # Analysis methodology
│   ├── templates/
│   │   └── report_template.html    # HTML styling
│   └── scripts/
│       └── generate_html.py        # Report generator
└── mcp/                            # MCP server (Python)
    ├── pyproject.toml
    ├── .mcp.json.example
    └── src/filing_downloader/
        ├── server.py               # FastMCP entry, 4 tools
        ├── services/
        │   ├── hkex_api.py         # HKEX API client
        │   └── cninfo_api.py       # CNINFO API client
        └── utils/
            └── pdf.py              # PDF download & extraction
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `hkex_search_filings` | Search HKEX filings by stock code, category, date |
| `hkex_download_filing` | Download a HKEX filing PDF |
| `cninfo_search_filings` | Search CNINFO filings for A-shares |
| `cninfo_download_filing` | Download a CNINFO filing PDF |

## How It Works

1. You ask Claude to analyze a stock
2. The skill uses MCP tools to download annual reports from HKEX/CNINFO
3. It extracts financial data from the PDFs
4. It fetches current price/metrics from TradingView/Google Finance
5. It runs four valuation frameworks
6. It generates a self-contained HTML report

The MCP server starts automatically when a tool is called — no manual startup needed.
