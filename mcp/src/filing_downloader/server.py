"""Filing Downloader MCP Server.

Exposes tools for searching and downloading financial filings from
HKEX (Hong Kong Stock Exchange) and CNINFO (巨潮资讯网).
"""

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .services.hkex_api import HKEXClient
from .services.cninfo_api import CNINFOClient
from .utils.pdf import save_pdf, extract_text

mcp = FastMCP("filing-downloader")

hkex = HKEXClient()
cninfo = CNINFOClient()


@mcp.tool()
async def hkex_search_filings(
    stock_code: str,
    category: str = "all",
    from_date: str = "",
    to_date: str = "",
    title_keyword: str = "",
    lang: str = "zh",
) -> str:
    """Search HKEX (Hong Kong Stock Exchange) filings for a stock.

    Args:
        stock_code: Stock code, e.g. "02313", "00700"
        category: "annual" (年报), "interim" (中报), or "all" (全部)
        from_date: Start date YYYY-MM-DD (default: 1 year ago)
        to_date: End date YYYY-MM-DD (default: today)
        title_keyword: Filter by title keyword
        lang: "zh" or "en"
    """
    filings = await hkex.search(
        stock_code=stock_code,
        category=category,
        from_date=from_date or None,
        to_date=to_date or None,
        title_keyword=title_keyword,
        lang=lang,
    )

    results = []
    for f in filings:
        results.append({
            "title": f.title,
            "stock_code": f.stock_code,
            "stock_name": f.stock_name,
            "date": f.date,
            "file_link": f.file_link,
            "file_type": f.file_type,
            "file_size": f.file_size,
            "category": f.category,
            "full_url": f.full_url(),
        })

    return json.dumps(results, ensure_ascii=False, indent=2)


@mcp.tool()
async def hkex_download_filing(
    file_link: str,
    output_dir: str = ".",
    extract_text_flag: bool = False,
) -> str:
    """Download a filing PDF from HKEX.

    Args:
        file_link: The file_link from hkex_search_filings result
        output_dir: Directory to save the PDF
        extract_text_flag: If True, also extract text from the PDF
    """
    content = await hkex.download_pdf(file_link)

    filename = file_link.split("/")[-1]
    if not filename.endswith(".pdf"):
        filename += ".pdf"

    filepath = save_pdf(content, output_dir, filename)

    result = {"file_path": str(filepath), "size_bytes": len(content)}

    if extract_text_flag:
        text = extract_text(filepath)
        result["text_preview"] = text[:5000]
        result["text_length"] = len(text)

    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def cninfo_search_filings(
    stock_code: str,
    market: str,
    category: str = "all",
    from_date: str = "",
    to_date: str = "",
) -> str:
    """Search CNINFO (巨潮资讯网) filings for an A-share stock.

    Args:
        stock_code: Stock code, e.g. "600519", "000858"
        market: "sh" (Shanghai) or "sz" (Shenzhen)
        category: "annual" (年报), "semi_annual" (中报), "q1" (一季报), "q3" (三季报), or "all"
        from_date: Start date YYYY-MM-DD
        to_date: End date YYYY-MM-DD
    """
    filings = await cninfo.search(
        stock_code=stock_code,
        market=market,
        category=category,
        from_date=from_date or None,
        to_date=to_date or None,
    )

    results = []
    for f in filings:
        results.append({
            "title": f.title,
            "stock_code": f.stock_code,
            "stock_name": f.stock_name,
            "date": f.date,
            "adjunct_url": f.adjunct_url,
            "file_type": f.file_type,
            "full_url": f.full_url(),
            "announcement_id": f.announcement_id,
        })

    return json.dumps(results, ensure_ascii=False, indent=2)


@mcp.tool()
async def cninfo_download_filing(
    adjunct_url: str,
    output_dir: str = ".",
    extract_text_flag: bool = False,
) -> str:
    """Download a filing PDF from CNINFO (巨潮资讯网).

    Args:
        adjunct_url: The adjunct_url from cninfo_search_filings result
        output_dir: Directory to save the PDF
        extract_text_flag: If True, also extract text from the PDF
    """
    content = await cninfo.download_pdf(adjunct_url)

    filename = adjunct_url.split("/")[-1]
    if not filename.endswith(".pdf"):
        filename += ".pdf"

    filepath = save_pdf(content, output_dir, filename)

    result = {"file_path": str(filepath), "size_bytes": len(content)}

    if extract_text_flag:
        text = extract_text(filepath)
        result["text_preview"] = text[:5000]
        result["text_length"] = len(text)

    return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
