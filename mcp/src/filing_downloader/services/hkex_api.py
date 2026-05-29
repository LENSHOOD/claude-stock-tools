"""HKEXnews filing search and download client.

Uses the undocumented titleSearchServlet.do JSON API.
The API requires a JSF session initialization (GET page → extract ViewState → POST form)
before the JSON search endpoint works.

Reference: https://github.com/simonplmak-cloud/hkex-filing-scraper
"""

import json
import re
from datetime import datetime, timedelta
from calendar import monthrange
from dataclasses import dataclass

import httpx

SEARCH_PAGE = "https://www1.hkexnews.hk/search/titlesearch.xhtml"
API_ENDPOINT = "https://www1.hkexnews.hk/search/titleSearchServlet.do"
BASE_URL = "https://www1.hkexnews.hk"

CATEGORY_CODES = {
    "annual": {"t1code": "40000", "t2code": "40100"},
    "interim": {"t1code": "40000", "t2code": "40200"},
    "all": {"t1code": "-2", "t2code": "-2"},
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8",
}


@dataclass
class Filing:
    title: str
    stock_code: str
    stock_name: str
    date: str
    file_link: str
    file_type: str
    file_size: str
    category: str
    news_id: str

    def full_url(self) -> str:
        if self.file_link.startswith("http"):
            return self.file_link
        return f"{BASE_URL}{self.file_link}"


def _parse_record(record: dict) -> Filing:
    raw_code = record.get("STOCK_CODE", "").split("<br/>")[0].strip()
    raw_name = record.get("STOCK_NAME", "").split("<br/>")[0].strip()
    title = record.get("TITLE", "").replace("&#x3b;", ";").replace("&amp;", "&")
    file_link = record.get("FILE_LINK", "")

    date_time = record.get("DATE_TIME", "")
    date_part = date_time.split(" ")[0] if date_time else ""

    return Filing(
        title=title.strip(),
        stock_code=raw_code,
        stock_name=raw_name.strip(),
        date=date_part,
        file_link=file_link,
        file_type=record.get("FILE_TYPE", ""),
        file_size=record.get("FILE_INFO", ""),
        category=record.get("LONG_TEXT", ""),
        news_id=record.get("NEWS_ID", ""),
    )


def _monthly_chunks(from_date: datetime, to_date: datetime) -> list[tuple[datetime, datetime]]:
    chunks = []
    cursor = datetime(to_date.year, to_date.month, 1)
    while cursor >= datetime(from_date.year, from_date.month, 1):
        chunk_start = max(cursor, from_date)
        _, last_day = monthrange(cursor.year, cursor.month)
        chunk_end = min(datetime(cursor.year, cursor.month, last_day), to_date)
        chunks.append((chunk_start, chunk_end))
        if cursor.month == 1:
            cursor = datetime(cursor.year - 1, 12, 1)
        else:
            cursor = datetime(cursor.year, cursor.month - 1, 1)
    return chunks


class HKEXClient:
    def __init__(self):
        self._client = httpx.AsyncClient(
            headers=HEADERS,
            timeout=30.0,
            follow_redirects=True,
        )
        self._session_ready = False

    async def _init_session(self):
        """Initialize JSF session: GET page, extract ViewState, POST form."""
        if self._session_ready:
            return

        # Step 1: GET the search page to get ViewState
        resp = await self._client.get(
            SEARCH_PAGE,
            params={
                "sortDir": "0",
                "sortByRecordDate": "on",
                "searchType": "0",
                "category": "0",
                "t1code": "-2",
                "t2Gcode": "-2",
                "t2code": "-2",
                "documentType": "-1",
                "rowRange": "0",
                "lang": "EN",
            },
        )
        resp.raise_for_status()

        # Extract ViewState and form action
        vs_match = re.search(r'javax\.faces\.ViewState.*?value="([^"]+)"', resp.text)
        view_state = vs_match.group(1) if vs_match else ""
        fa_match = re.search(r'<form[^>]*action="([^"]+)"', resp.text)
        form_action = fa_match.group(1) if fa_match else ""

        submit_url = (
            f"{BASE_URL}{form_action}" if form_action.startswith("/") else form_action
        )

        # Step 2: POST the form to set date range on server session
        await self._client.post(
            submit_url,
            data={
                "j_idt10": "j_idt10",
                "j_idt10:loadMoreRange": "100",
                "javax.faces.ViewState": view_state,
                "from": "20260101",
                "to": "20260530",
            },
        )

        self._session_ready = True

    async def _fetch_chunk(
        self,
        from_yyyymmdd: str,
        to_yyyymmdd: str,
        t1code: str = "-2",
        t2code: str = "-2",
        lang: str = "E",
        max_records: int = 2000,
    ) -> list[dict]:
        """Fetch records for a date range via the JSON API."""
        resp = await self._client.get(
            API_ENDPOINT,
            params={
                "sortDir": "0",
                "sortByOptions": "DateTime",
                "category": "0",
                "market": "SEHK",
                "stockId": "-1",
                "documentType": "-1",
                "fromDate": from_yyyymmdd,
                "toDate": to_yyyymmdd,
                "title": "",
                "searchType": "0",
                "t1code": t1code,
                "t2Gcode": "-2",
                "t2code": t2code,
                "rowRange": str(max_records),
                "lang": lang,
            },
            headers={
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Referer": SEARCH_PAGE,
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        raw = data.get("result", "[]")
        return json.loads(raw) if isinstance(raw, str) else raw

    async def search(
        self,
        stock_code: str,
        category: str = "all",
        from_date: str | None = None,
        to_date: str | None = None,
        title_keyword: str = "",
        lang: str = "zh",
    ) -> list[Filing]:
        await self._init_session()

        cat = CATEGORY_CODES.get(category, CATEGORY_CODES["all"])

        if not from_date:
            dt_from = datetime.now() - timedelta(days=365)
        else:
            dt_from = datetime.strptime(from_date.replace("-", ""), "%Y%m%d")

        if not to_date:
            dt_to = datetime.now()
        else:
            dt_to = datetime.strptime(to_date.replace("-", ""), "%Y%m%d")

        # API lang: "zh" → "C", "en" → "E"
        api_lang = "C" if lang == "zh" else "E"

        # The API always searches all stocks with stockId=-1.
        # We search with monthly chunks and filter by stock code locally.
        chunks = _monthly_chunks(dt_from, dt_to)
        padded_code = stock_code.zfill(5)

        all_filings: list[Filing] = []
        for chunk_from, chunk_to in chunks:
            records = await self._fetch_chunk(
                from_yyyymmdd=chunk_from.strftime("%Y%m%d"),
                to_yyyymmdd=chunk_to.strftime("%Y%m%d"),
                t1code=cat["t1code"],
                t2code=cat["t2code"],
                lang=api_lang,
            )

            for r in records:
                f = _parse_record(r)
                if f.stock_code != padded_code:
                    continue
                if title_keyword and title_keyword.lower() not in f.title.lower():
                    continue
                all_filings.append(f)

        return all_filings

    async def download_pdf(self, file_link: str) -> bytes:
        if not file_link.startswith("http"):
            file_link = f"{BASE_URL}{file_link}"

        resp = await self._client.get(file_link)
        resp.raise_for_status()
        return resp.content

    async def close(self):
        await self._client.aclose()
