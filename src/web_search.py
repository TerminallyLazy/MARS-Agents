import asyncio
import os
import re
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import quote_plus, urljoin, urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter


@dataclass
class SearchResult:
    url: str
    title: str
    content: str
    snippet: str
    score: float = 0.0
    source: str = "web"


@dataclass
class WebSearchResponse:
    query: str
    results: list[SearchResult] = field(default_factory=list)
    total_tokens: int = 0
    sources_crawled: int = 0
    error: Optional[str] = None


class WebSearchAgent:
    def __init__(
        self,
        max_results: int = 5,
        content_threshold: float = 0.5,
        timeout: int = 30000,
    ):
        self.max_results = max_results
        self.content_threshold = content_threshold
        self.timeout = timeout

        self.browser_config = BrowserConfig(
            headless=True,
            text_mode=True,
            verbose=False,
        )

        self.crawl_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=50,
            excluded_tags=["nav", "footer", "header", "script", "style", "aside"],
            exclude_external_links=False,
            remove_overlay_elements=True,
            page_timeout=timeout,
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(threshold=content_threshold),
                options={"ignore_links": False},
            ),
        )

    async def search(self, query: str, search_engine: str = "duckduckgo") -> WebSearchResponse:
        search_url = self._build_search_url(query, search_engine)

        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                result = await crawler.arun(url=search_url, config=self.crawl_config)

                if not result.success:
                    return WebSearchResponse(
                        query=query, error=f"Search failed: {result.error_message}"
                    )

                urls = self._extract_search_urls(result, search_engine)

                if not urls:
                    return WebSearchResponse(
                        query=query,
                        results=[
                            SearchResult(
                                url=search_url,
                                title="Search Results",
                                content=result.markdown.raw_markdown[:2000]
                                if result.markdown
                                else "",
                                snippet=result.markdown.raw_markdown[:500]
                                if result.markdown
                                else "",
                                source=search_engine,
                            )
                        ],
                        sources_crawled=1,
                    )

                search_results = await self._crawl_urls(crawler, urls[: self.max_results])

                return WebSearchResponse(
                    query=query,
                    results=search_results,
                    sources_crawled=len(search_results),
                    total_tokens=sum(len(r.content.split()) for r in search_results),
                )

        except Exception as e:
            return WebSearchResponse(query=query, error=str(e))

    async def crawl_url(self, url: str) -> SearchResult:
        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                result = await crawler.arun(url=url, config=self.crawl_config)

                if not result.success:
                    return SearchResult(
                        url=url,
                        title="Error",
                        content=f"Failed to crawl: {result.error_message}",
                        snippet="",
                        score=0.0,
                    )

                title = (
                    result.metadata.get("title", urlparse(url).netloc)
                    if result.metadata
                    else urlparse(url).netloc
                )
                content = (
                    result.markdown.fit_markdown or result.markdown.raw_markdown
                    if result.markdown
                    else ""
                )

                return SearchResult(
                    url=url,
                    title=title,
                    content=content[:10000],
                    snippet=content[:500],
                    score=1.0,
                    source="direct",
                )
        except Exception as e:
            return SearchResult(url=url, title="Error", content=str(e), snippet="", score=0.0)

    async def research_topic(
        self, topic: str, depth: int = 2, max_pages: int = 10
    ) -> WebSearchResponse:
        all_results: list[SearchResult] = []
        crawled_urls: set[str] = set()

        initial_response = await self.search(topic)
        if initial_response.error:
            return initial_response

        all_results.extend(initial_response.results)
        crawled_urls.update(r.url for r in initial_response.results)

        if depth > 1 and len(all_results) < max_pages:
            follow_urls = []
            for result in initial_response.results[:3]:
                links = self._extract_links_from_content(result.content)
                for link in links[:2]:
                    if link not in crawled_urls and len(follow_urls) < max_pages - len(all_results):
                        follow_urls.append(link)

            if follow_urls:
                async with AsyncWebCrawler(config=self.browser_config) as crawler:
                    follow_results = await self._crawl_urls(crawler, follow_urls)
                    all_results.extend(follow_results)
                    crawled_urls.update(r.url for r in follow_results)

        return WebSearchResponse(
            query=topic,
            results=all_results,
            sources_crawled=len(crawled_urls),
            total_tokens=sum(len(r.content.split()) for r in all_results),
        )

    def _build_search_url(self, query: str, engine: str) -> str:
        encoded_query = quote_plus(query)

        engines = {
            "duckduckgo": f"https://html.duckduckgo.com/html/?q={encoded_query}",
            "google": f"https://www.google.com/search?q={encoded_query}",
            "bing": f"https://www.bing.com/search?q={encoded_query}",
        }

        return engines.get(engine, engines["duckduckgo"])

    def _extract_search_urls(self, result, engine: str) -> list[str]:
        urls = []

        if result.links:
            external_links = result.links.get("external", [])
            for link in external_links:
                href = link.get("href", "")
                if href and self._is_valid_result_url(href, engine):
                    urls.append(href)

        if result.markdown and result.markdown.raw_markdown:
            url_pattern = r'https?://[^\s<>"\')\]]+'
            found_urls = re.findall(url_pattern, result.markdown.raw_markdown)
            for url in found_urls:
                url = url.rstrip(".,;:")
                if url not in urls and self._is_valid_result_url(url, engine):
                    urls.append(url)

        return urls[: self.max_results * 2]

    def _is_valid_result_url(self, url: str, engine: str) -> bool:
        excluded_domains = [
            "google.com",
            "bing.com",
            "duckduckgo.com",
            "facebook.com",
            "twitter.com",
            "instagram.com",
            "youtube.com",
            "linkedin.com",
            "pinterest.com",
            "reddit.com/user/",
            "t.co",
            "bit.ly",
        ]

        for domain in excluded_domains:
            if domain in url:
                return False

        return url.startswith("http") and len(url) > 20

    async def _crawl_urls(self, crawler, urls: list[str]) -> list[SearchResult]:
        results = []

        tasks = [self._crawl_single(crawler, url) for url in urls]
        crawl_results = await asyncio.gather(*tasks, return_exceptions=True)

        for url, crawl_result in zip(urls, crawl_results):
            if isinstance(crawl_result, Exception):
                continue
            if crawl_result and crawl_result.score > 0:
                results.append(crawl_result)

        return results

    async def _crawl_single(self, crawler, url: str) -> Optional[SearchResult]:
        try:
            config = self.crawl_config.clone(page_timeout=15000)
            result = await crawler.arun(url=url, config=config)

            if not result.success:
                return None

            title = result.metadata.get("title", "") if result.metadata else ""
            if not title:
                title = urlparse(url).netloc

            content = ""
            if result.markdown:
                content = result.markdown.fit_markdown or result.markdown.raw_markdown or ""

            if len(content) < 100:
                return None

            return SearchResult(
                url=url,
                title=title,
                content=content[:8000],
                snippet=content[:400],
                score=min(len(content) / 1000, 1.0),
                source="crawl",
            )
        except Exception:
            return None

    def _extract_links_from_content(self, content: str) -> list[str]:
        url_pattern = r'https?://[^\s<>"\')\]]+'
        urls = re.findall(url_pattern, content)
        return [url.rstrip(".,;:") for url in urls if self._is_valid_result_url(url, "")]


async def web_search(query: str, max_results: int = 5) -> WebSearchResponse:
    agent = WebSearchAgent(max_results=max_results)
    return await agent.search(query)


async def crawl_page(url: str) -> SearchResult:
    agent = WebSearchAgent()
    return await agent.crawl_url(url)


async def research(topic: str, depth: int = 2, max_pages: int = 10) -> WebSearchResponse:
    agent = WebSearchAgent()
    return await agent.research_topic(topic, depth=depth, max_pages=max_pages)
