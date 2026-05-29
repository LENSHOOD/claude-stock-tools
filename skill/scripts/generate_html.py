#!/usr/bin/env python3
"""
Stock Analysis HTML Report Generator

Usage:
    python generate_html.py --data report_data.json --template template.html --output report.html

The script reads a JSON data file and an HTML template, fills in the placeholders,
and generates a complete HTML report.
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime


def make_table(headers, rows, highlight_col=None):
    """Generate HTML table from headers and rows."""
    html = '<table>\n<thead><tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr></thead>\n<tbody>\n'
    for row in rows:
        html += '<tr>'
        for i, cell in enumerate(row):
            cls = ''
            if highlight_col is not None and i == highlight_col:
                cls = ' class="highlight-row"'
            html += f'<td{cls}>{cell}</td>'
        html += '</tr>\n'
    html += '</tbody></table>'
    return html


def make_cards(cards):
    """Generate card grid HTML."""
    html = ''
    for card in cards:
        change_html = ''
        if 'change' in card:
            color = 'var(--success)' if card.get('change_positive', True) else 'var(--danger)'
            change_html = f'<div class="change" style="color:{color}">{card["change"]}</div>'
        html += f'''<div class="card">
  <div class="label">{card["label"]}</div>
  <div class="value">{card["value"]}</div>
  {change_html}
</div>\n'''
    return html


def make_verdict_class(verdict_type):
    """Map verdict type to CSS class."""
    mapping = {
        'buy': 'verdict-buy',
        'recommend': 'verdict-buy',
        'strong_recommend': 'verdict-buy',
        'cautious': 'verdict-cautious',
        'special_situation': 'verdict-cautious',
        'avoid': 'verdict-avoid',
        'not_recommend': 'verdict-avoid',
    }
    return mapping.get(verdict_type, 'verdict-cautious')


def build_prior_report_section(data):
    """Build prior report comparison section if prior report data exists."""
    prior = data.get('prior_report', {})
    if not prior:
        return '', ''

    changes = prior.get('verdict_changes', [])
    prior_reports = prior.get('prior_report_dates', [])

    # Build verdict changes section
    changes_html = ''
    if changes:
        rows = []
        for c in changes:
            old_v = c.get('old_verdict', '')
            new_v = c.get('new_verdict', '')
            reason = c.get('reason', '')
            rows.append([
                c.get('framework', ''),
                f'<span class="verdict-avoid">{old_v}</span>',
                f'<span class="verdict-buy">{new_v}</span>',
                reason,
            ])
        table = make_table(['投资框架', '上次结论', '本次结论', '变化原因'], rows)
        changes_html = f'''
    <div class="section">
      <h2 class="section-title">观点变化</h2>
      <p>与上次分析相比，以下框架的投资结论发生了变化：</p>
      <div class="table-wrapper">
        {table}
      </div>
    </div>'''

    # Build prior reports history section
    history_html = ''
    if prior_reports:
        links = []
        for pr in prior_reports:
            date = pr.get('date', '')
            links.append(f'<a href="{date}.html">{date}</a>')
        history_html = f'''
    <div class="section">
      <h2 class="section-title">历史报告</h2>
      <p>本股票的历史分析报告：</p>
      <ul>
        {''.join(f'<li>{link}</li>' for link in links)}
      </ul>
    </div>'''

    return changes_html, history_html


def build_peer_comparison_section(data):
    """Build peer comparison section if peer data exists."""
    peers = data.get('peer_comparison', [])
    if not peers:
        return ''

    current = data.get('stock_overview', {})
    rows = []
    # Add current stock first with highlight
    rows.append([
        f'<strong>{current.get("name", "")}</strong>',
        str(current.get('pe', '-')),
        str(current.get('pb', '-')),
        str(current.get('roe', '-')),
        str(current.get('revenue_growth', '-')),
        str(current.get('net_margin', '-')),
        str(current.get('dividend_yield', '-')),
        str(current.get('market_cap', '-')),
        '<span class="badge badge-info">当前</span>'
    ])
    for p in peers:
        rows.append([
            p.get('name', ''),
            str(p.get('pe', '-')),
            str(p.get('pb', '-')),
            str(p.get('roe', '-')),
            str(p.get('revenue_growth', '-')),
            str(p.get('net_margin', '-')),
            str(p.get('dividend_yield', '-')),
            str(p.get('market_cap', '-')),
            ''
        ])

    table = make_table(
        ['公司', 'P/E', 'P/B', 'ROE', '营收增速', '净利率', '股息率', '市值', ''],
        rows,
        highlight_col=0
    )

    return f'''
    <div class="section">
      <h2 class="section-title">八、行业对比</h2>
      <p>以下为当前分析股票与同行业可比公司的基本面横向对比：</p>
      <div class="table-wrapper">
        {table}
      </div>
    </div>'''


def generate_report(data, template_path):
    """Generate the full HTML report from data and template."""
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    overview = data.get('stock_overview', {})
    income = data.get('income_statement', {})
    balance = data.get('balance_sheet', {})
    operating = data.get('operating_metrics', {})
    shareholder = data.get('shareholder_returns', {})
    quarterly = data.get('quarterly_data', {})
    valuation = data.get('valuation', {})
    graham = data.get('graham', {})
    schloss = data.get('schloss', {})
    buffett = data.get('buffett', {})
    synthesis = data.get('synthesis', {})

    # Basic info
    replacements = {
        '{{TITLE}}': f'{overview.get("name", "")}（{overview.get("code", "")}）投资价值分析',
        '{{COMPANY_NAME}}': overview.get('name', ''),
        '{{STOCK_CODE}}': overview.get('code', ''),
        '{{DATE}}': data.get('date', datetime.now().strftime('%Y-%m-%d')),
        '{{CURRENT_PRICE}}': overview.get('price', ''),
        '{{MARKET_CAP}}': overview.get('market_cap', ''),
        '{{DATA_SOURCES}}': data.get('data_sources', 'Google Finance, 公司年报'),
    }

    # Section 1: Overview cards
    replacements['{{OVERVIEW_CARDS}}'] = make_cards(data.get('overview_cards', []))

    # Section 2: Financial tables
    if income.get('headers') and income.get('rows'):
        replacements['{{INCOME_TABLE}}'] = make_table(income['headers'], income['rows'])
    else:
        replacements['{{INCOME_TABLE}}'] = '<p>数据待补充</p>'

    if balance.get('headers') and balance.get('rows'):
        replacements['{{BALANCE_TABLE}}'] = make_table(balance['headers'], balance['rows'])
    else:
        replacements['{{BALANCE_TABLE}}'] = '<p>数据待补充</p>'

    if operating.get('headers') and operating.get('rows'):
        replacements['{{OPERATING_TABLE}}'] = make_table(operating['headers'], operating['rows'])
    else:
        replacements['{{OPERATING_TABLE}}'] = '<p>数据待补充</p>'

    if shareholder.get('headers') and shareholder.get('rows'):
        replacements['{{SHAREHOLDER_RETURN_TABLE}}'] = make_table(shareholder['headers'], shareholder['rows'])
    else:
        replacements['{{SHAREHOLDER_RETURN_TABLE}}'] = '<p>数据待补充</p>'

    if quarterly.get('headers') and quarterly.get('rows'):
        replacements['{{QUARTERLY_TABLE}}'] = make_table(quarterly['headers'], quarterly['rows'])
    else:
        replacements['{{QUARTERLY_TABLE}}'] = '<p>暂无最新季度数据</p>'

    # Section 3: Earnings Report Insights
    earnings = data.get('earnings_insights', {})
    replacements['{{MANAGEMENT_OUTLOOK}}'] = earnings.get('management_outlook', '暂无管理层展望数据')
    if earnings.get('insights_table'):
        replacements['{{EARNINGS_INSIGHTS_TABLE}}'] = make_table(
            earnings['insights_table']['headers'],
            earnings['insights_table']['rows']
        )
    else:
        replacements['{{EARNINGS_INSIGHTS_TABLE}}'] = '<p>暂无财报洞见数据</p>'

    abnormal = earnings.get('abnormal_signals', [])
    if abnormal:
        signals_html = '<div class="verdict verdict-cautious"><div class="verdict-title">异常信号解读</div><ul>'
        for signal in abnormal:
            signals_html += f'<li>{signal}</li>'
        signals_html += '</ul></div>'
        replacements['{{ABNORMAL_SIGNALS}}'] = signals_html
    else:
        replacements['{{ABNORMAL_SIGNALS}}'] = ''

    # Section 4: Valuation
    replacements['{{VALUATION_CARDS}}'] = make_cards(data.get('valuation_cards', []))
    if valuation.get('headers') and valuation.get('rows'):
        replacements['{{VALUATION_CONTEXT_TABLE}}'] = make_table(valuation['headers'], valuation['rows'])
    else:
        replacements['{{VALUATION_CONTEXT_TABLE}}'] = ''

    # Section 4.1: Graham
    if graham.get('number_table'):
        replacements['{{GRAHAM_NUMBER_TABLE}}'] = make_table(
            graham['number_table']['headers'],
            graham['number_table']['rows']
        )
    else:
        replacements['{{GRAHAM_NUMBER_TABLE}}'] = '<p>数据待补充</p>'

    if graham.get('standards_table'):
        replacements['{{GRAHAM_STANDARDS_TABLE}}'] = make_table(
            graham['standards_table']['headers'],
            graham['standards_table']['rows']
        )
    else:
        replacements['{{GRAHAM_STANDARDS_TABLE}}'] = '<p>数据待补充</p>'

    replacements['{{GRAHAM_VERDICT_CLASS}}'] = make_verdict_class(graham.get('verdict_type', 'cautious'))
    replacements['{{GRAHAM_VERDICT}}'] = graham.get('verdict', '待分析')
    replacements['{{GRAHAM_VERDICT_DETAIL}}'] = graham.get('verdict_detail', '')

    # Section 4.2: Schloss
    if schloss.get('criteria_table'):
        replacements['{{SCHLOSS_CRITERIA_TABLE}}'] = make_table(
            schloss['criteria_table']['headers'],
            schloss['criteria_table']['rows']
        )
    else:
        replacements['{{SCHLOSS_CRITERIA_TABLE}}'] = '<p>数据待补充</p>'

    replacements['{{SCHLOSS_VERDICT_CLASS}}'] = make_verdict_class(schloss.get('verdict_type', 'cautious'))
    replacements['{{SCHLOSS_VERDICT}}'] = schloss.get('verdict', '待分析')
    replacements['{{SCHLOSS_VERDICT_DETAIL}}'] = schloss.get('verdict_detail', '')

    # Section 4.3: Buffett & Munger
    if buffett.get('moat_table'):
        replacements['{{MOAT_TABLE}}'] = make_table(
            buffett['moat_table']['headers'],
            buffett['moat_table']['rows']
        )
    else:
        replacements['{{MOAT_TABLE}}'] = '<p>数据待补充</p>'

    if buffett.get('dcf_table'):
        replacements['{{DCF_TABLE}}'] = make_table(
            buffett['dcf_table']['headers'],
            buffett['dcf_table']['rows']
        )
    else:
        replacements['{{DCF_TABLE}}'] = '<p>数据待补充</p>'

    replacements['{{INVERSION_ANALYSIS}}'] = buffett.get('inversion', '待分析')
    replacements['{{BUFFETT_VERDICT_CLASS}}'] = make_verdict_class(buffett.get('verdict_type', 'cautious'))
    replacements['{{BUFFETT_VERDICT}}'] = buffett.get('verdict', '待分析')
    replacements['{{BUFFETT_VERDICT_DETAIL}}'] = buffett.get('verdict_detail', '')

    # Section 4.4: Lynch
    lynch = data.get('lynch', {})
    replacements['{{LYNCH_CATEGORY_CARDS}}'] = make_cards(lynch.get('category_cards', []))
    if lynch.get('peg_table'):
        replacements['{{LYNCH_PEG_TABLE}}'] = make_table(
            lynch['peg_table']['headers'],
            lynch['peg_table']['rows']
        )
    else:
        replacements['{{LYNCH_PEG_TABLE}}'] = '<p>数据待补充</p>'

    if lynch.get('checks_table'):
        replacements['{{LYNCH_CHECKS_TABLE}}'] = make_table(
            lynch['checks_table']['headers'],
            lynch['checks_table']['rows']
        )
    else:
        replacements['{{LYNCH_CHECKS_TABLE}}'] = '<p>数据待补充</p>'

    if lynch.get('dcf_table'):
        replacements['{{LYNCH_DCF_TABLE}}'] = make_table(
            lynch['dcf_table']['headers'],
            lynch['dcf_table']['rows']
        )
    else:
        replacements['{{LYNCH_DCF_TABLE}}'] = '<p>数据待补充</p>'

    replacements['{{LYNCH_VERDICT_CLASS}}'] = make_verdict_class(lynch.get('verdict_type', 'cautious'))
    replacements['{{LYNCH_VERDICT}}'] = lynch.get('verdict', '待分析')
    replacements['{{LYNCH_VERDICT_DETAIL}}'] = lynch.get('verdict_detail', '')

    # Section 6: Technical Analysis
    technical = data.get('technical', {})
    if technical.get('trend_table'):
        replacements['{{TECHNICAL_TREND_TABLE}}'] = make_table(
            technical['trend_table']['headers'],
            technical['trend_table']['rows']
        )
    else:
        replacements['{{TECHNICAL_TREND_TABLE}}'] = '<p>暂无趋势数据</p>'

    if technical.get('levels_table'):
        replacements['{{TECHNICAL_LEVELS_TABLE}}'] = make_table(
            technical['levels_table']['headers'],
            technical['levels_table']['rows']
        )
    else:
        replacements['{{TECHNICAL_LEVELS_TABLE}}'] = '<p>暂无支撑阻力位数据</p>'

    if technical.get('volume_table'):
        replacements['{{TECHNICAL_VOLUME_TABLE}}'] = make_table(
            technical['volume_table']['headers'],
            technical['volume_table']['rows']
        )
    else:
        replacements['{{TECHNICAL_VOLUME_TABLE}}'] = '<p>暂无量价数据</p>'

    replacements['{{TECHNICAL_VERDICT_CLASS}}'] = make_verdict_class(technical.get('verdict_type', 'cautious'))
    replacements['{{TECHNICAL_VERDICT}}'] = technical.get('verdict', '待分析')
    replacements['{{TECHNICAL_VERDICT_DETAIL}}'] = technical.get('verdict_detail', '')

    # Section 5: Synthesis
    if synthesis.get('comparison_table'):
        replacements['{{FRAMEWORK_COMPARISON_TABLE}}'] = make_table(
            synthesis['comparison_table']['headers'],
            synthesis['comparison_table']['rows']
        )
    else:
        replacements['{{FRAMEWORK_COMPARISON_TABLE}}'] = ''

    if synthesis.get('buy_tiers'):
        replacements['{{BUY_TIERS_TABLE}}'] = make_table(
            synthesis['buy_tiers']['headers'],
            synthesis['buy_tiers']['rows']
        )
    else:
        replacements['{{BUY_TIERS_TABLE}}'] = ''

    if synthesis.get('sell_tiers'):
        replacements['{{SELL_TIERS_TABLE}}'] = make_table(
            synthesis['sell_tiers']['headers'],
            synthesis['sell_tiers']['rows']
        )
    else:
        replacements['{{SELL_TIERS_TABLE}}'] = ''

    replacements['{{YELLOW_SIGNALS}}'] = synthesis.get('yellow_signals', '待分析')
    replacements['{{RED_SIGNALS}}'] = synthesis.get('red_signals', '待分析')

    # Section 8: Peer comparison
    replacements['{{PEER_COMPARISON_SECTION}}'] = build_peer_comparison_section(data)

    # Section 0: Prior report comparison
    changes_html, history_html = build_prior_report_section(data)
    replacements['{{PRIOR_REPORT_CHANGES}}'] = changes_html
    replacements['{{PRIOR_REPORT_HISTORY}}'] = history_html

    # Apply all replacements
    result = template
    for key, value in replacements.items():
        result = result.replace(key, str(value))

    return result


def main():
    parser = argparse.ArgumentParser(description='Generate stock analysis HTML report')
    parser.add_argument('--data', required=True, help='Path to JSON data file')
    parser.add_argument('--template', required=True, help='Path to HTML template file')
    parser.add_argument('--output', required=True, help='Output HTML file path')
    args = parser.parse_args()

    with open(args.data, 'r', encoding='utf-8') as f:
        data = json.load(f)

    html = generate_report(data, args.template)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'Report generated: {output_path}')


if __name__ == '__main__':
    main()
