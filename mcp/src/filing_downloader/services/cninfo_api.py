"""CNINFO (巨潮资讯网) filing search and download client.

Uses the undocumented hisAnnouncement/query API.
Stock list from: http://www.cninfo.com.cn/new/data/szse_stock.json
(covers both Shanghai and Shenzhen A-shares)

Reference: https://github.com/tr1s7an/CnInfoReports
"""

import asyncio
from dataclasses import dataclass

import httpx

SEARCH_URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
STOCK_LIST_URL = "http://www.cninfo.com.cn/new/data/szse_stock.json"
PDF_BASE = "http://static.cninfo.com.cn/"

CATEGORY_MAP = {
    "annual": "category_ndbg_szsh",
    "semi_annual": "category_bndbg_szsh",
    "q1": "category_yjdbg_szsh",
    "q3": "category_sjdbg_szsh",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": "http://www.cninfo.com.cn",
    "Referer": "http://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
}


@dataclass
class Filing:
    title: str
    stock_code: str
    stock_name: str
    date: str
    adjunct_url: str
    file_type: str
    announcement_id: str

    def full_url(self) -> str:
        return f"{PDF_BASE}{self.adjunct_url}"


class CNINFOClient:
    def __init__(self):
        self._client = httpx.AsyncClient(
            headers=HEADERS,
            timeout=30.0,
            follow_redirects=True,
        )
        self._stock_cache: dict[str, dict] = {}
        self._cache_loaded = False

    async def _load_stock_list(self):
        if self._cache_loaded:
            return
        resp = await self._client.get(STOCK_LIST_URL)
        resp.raise_for_status()
        data = resp.json()
        stocks = data.get("stockList", [])
        for s in stocks:
            self._stock_cache[s["code"]] = s
        self._cache_loaded = True

    def _detect_market(self, org_id: str) -> str:
        if org_id.startswith("gssh"):
            return "sse"
        return "szse"

    async def search(
        self,
        stock_code: str,
        market: str = "",
        category: str = "all",
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[Filing]:
        await self._load_stock_list()

        stock_info = self._stock_cache.get(stock_code)
        if not stock_info:
            raise ValueError(f"Stock code {stock_code} not found in A-share market")

        org_id = stock_info["orgId"]
        column = self._detect_market(org_id)
        stock_param = f"{stock_code},{org_id}"

        if category == "all":
            cat_value = ""
        else:
            cat_value = CATEGORY_MAP.get(category, "")

        se_date = ""
        if from_date and to_date:
            se_date = f"{from_date}~{to_date}"
        elif from_date:
            se_date = f"{from_date}~"
        elif to_date:
            se_date = f"~{to_date}"

        data = {
            "column": column,
            "stock": stock_param,
            "tabName": "fulltext",
            "pageNum": "1",
            "pageSize": "50",
            "category": cat_value,
            "seDate": se_date,
        }

        resp = await self._client.post(SEARCH_URL, data=data)
        resp.raise_for_status()

        result = resp.json()
        announcements = result.get("announcements", []) or []

        filings = []
        for a in announcements:
            adj_url = a.get("adjunctUrl", "")
            title = a.get("announcementTitle", "")
            file_type = "PDF" if adj_url.lower().endswith(".pdf") else "OTHER"

            timestamp = a.get("announcementTime", 0)
            if timestamp:
                from datetime import datetime
                date_str = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")
            else:
                date_str = ""

            f = Filing(
                title=title,
                stock_code=a.get("secCode", stock_code),
                stock_name=a.get("secName", ""),
                date=date_str,
                adjunct_url=adj_url,
                file_type=file_type,
                announcement_id=a.get("announcementId", ""),
            )
            filings.append(f)

        return filings

    async def download_pdf(self, adjunct_url: str) -> bytes:
        url = f"{PDF_BASE}{adjunct_url}"
        resp = await self._client.get(url)
        resp.raise_for_status()
        return resp.content

    async def close(self):
        await self._client.aclose()
