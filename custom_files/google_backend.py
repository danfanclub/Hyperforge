"""
Google Custom Search backend for gpt-oss browser tool.
Uses Google Custom Search API instead of You.com or Exa.
"""

import os
import chz
from aiohttp import ClientSession
from typing import Optional

from .backend import Backend, BackendError
from .page_contents import PageContents, process_html


@chz.chz(typecheck=True)
class GoogleBackend(Backend):
    """Backend that uses Google Custom Search API."""

    source: str = chz.field(doc="Description of the backend source")

    def _get_api_key(self) -> str:
        key = os.environ.get("GOOGLE_KEY")
        if not key:
            raise BackendError("Google API key not provided")
        return key

    def _get_cx(self) -> str:
        cx = os.environ.get("GOOGLE_CX")
        if not cx:
            raise BackendError("Google Custom Search Engine ID not provided")
        return cx

    async def search(
        self, query: str, topn: int, session: ClientSession
    ) -> PageContents:
        """Perform a Google Custom Search."""
        api_key = self._get_api_key()
        cx = self._get_cx()

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cx,
            "q": query,
            "num": min(topn, 10),  # Google allows max 10 results per query
        }

        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise BackendError(
                    f"GoogleBackend error {resp.status}: {error_text}"
                )
            data = await resp.json()

        # Process results into HTML format
        titles_and_urls = []
        if "items" in data:
            for item in data["items"]:
                title = item.get("title", "")
                link = item.get("link", "")
                snippet = item.get("snippet", "")
                titles_and_urls.append((title, link, snippet))

        html_page = f"""
<html><body>
<h1>Search Results for: {query}</h1>
<ul>
{"".join([f"<li><a href='{url}'>{title}</a><br>{summary}</li>" for title, url, summary in titles_and_urls])}
</ul>
</body></html>
"""

        return process_html(
            html=html_page,
            url="",
            title=query,
            display_urls=True,
            session=session,
        )

    async def fetch(self, url: str, session: ClientSession) -> PageContents:
        """
        Fetch a URL's content.
        For now, use simple HTTP GET. Could be enhanced with Selenium later.
        """
        async with session.get(url, timeout=10) as resp:
            if resp.status != 200:
                raise BackendError(f"Failed to fetch {url}: HTTP {resp.status}")

            html = await resp.text()
            return process_html(
                html=html,
                url=url,
                title="",
                display_urls=True,
                session=session,
            )
