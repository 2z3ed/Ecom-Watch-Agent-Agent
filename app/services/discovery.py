from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from app.core.config import settings


@dataclass
class DiscoveryResult:
    title: str
    url: str
    domain: str
    snippet: str
    rank: int


class DiscoveryService:
    def __init__(self) -> None:
        self.base_url = settings.searxng_base_url.rstrip("/")
        self.timeout = settings.searxng_timeout
        self.default_limit = settings.searxng_default_limit

    def _normalize_domain(self, url: str) -> str:
        return urlparse(url).netloc.lower()

    def _domain_match(self, domain: str, allowed_domains: list[str]) -> bool:
        if not allowed_domains:
            return True
        for allowed in allowed_domains:
            allowed = allowed.lower()
            if domain == allowed or domain.endswith(f".{allowed}"):
                return True
        return False

    def _dedupe_and_filter(self, rows: list[dict], allowed_domains: list[str]) -> list[DiscoveryResult]:
        seen: set[str] = set()
        output: list[DiscoveryResult] = []
        for row in rows:
            url = str(row.get("url", "")).strip()
            if not url or url in seen:
                continue
            domain = self._normalize_domain(url)
            if not self._domain_match(domain, allowed_domains):
                continue
            seen.add(url)
            output.append(
                DiscoveryResult(
                    title=str(row.get("title", "")).strip(),
                    url=url,
                    domain=domain,
                    snippet=str(row.get("content", "")).strip(),
                    rank=len(output) + 1,
                )
            )
        return output

    def _fallback_results(self, query: str, limit: int, allowed_domains: list[str]) -> list[DiscoveryResult]:
        fallback_pool = [
            {"title": f"{query} - example candidate", "url": "https://example.com/products/demo-1", "content": "fallback"},
            {"title": f"{query} - demo candidate", "url": "https://demo.com/items/demo-2", "content": "fallback"},
            {"title": f"{query} - mock candidate", "url": "https://shop.example.org/p/demo-3", "content": "fallback"},
        ]
        data = self._dedupe_and_filter(fallback_pool, allowed_domains)
        return data[:limit]

    def search(self, query: str, limit: int | None = None, allowed_domains: list[str] | None = None) -> dict:
        if not settings.enable_discovery:
            return {
                "ok": False,
                "error": "Discovery is disabled. Set ENABLE_DISCOVERY=true.",
                "results": [],
                "is_fallback": False,
            }

        if not query.strip():
            return {"ok": False, "error": "Query is empty.", "results": [], "is_fallback": False}

        request_limit = limit or self.default_limit
        allowed = allowed_domains if allowed_domains is not None else settings.searxng_allowed_domains_list

        if not self.base_url:
            fallback = self._fallback_results(query, request_limit, allowed)
            return {
                "ok": True,
                "error": "SEARXNG_BASE_URL is not configured. Returned fallback results.",
                "results": [item.__dict__ for item in fallback],
                "is_fallback": True,
            }

        try:
            with httpx.Client(timeout=float(self.timeout)) as client:
                resp = client.get(
                    f"{self.base_url}/search",
                    params={"q": query, "format": "json"},
                )
                resp.raise_for_status()
                payload = resp.json()
                if not isinstance(payload, dict) or "results" not in payload:
                    return {
                        "ok": False,
                        "error": "Unexpected SearXNG response format.",
                        "results": [],
                        "is_fallback": False,
                    }
                rows = payload.get("results", [])
                if not isinstance(rows, list):
                    return {
                        "ok": False,
                        "error": "Unexpected SearXNG results type.",
                        "results": [],
                        "is_fallback": False,
                    }
                data = self._dedupe_and_filter(rows, allowed)[:request_limit]
                return {"ok": True, "error": None, "results": [item.__dict__ for item in data], "is_fallback": False}
        except httpx.TimeoutException:
            fallback = self._fallback_results(query, request_limit, allowed)
            return {
                "ok": True,
                "error": "SearXNG request timeout. Returned fallback results.",
                "results": [item.__dict__ for item in fallback],
                "is_fallback": True,
            }
        except Exception as exc:  # noqa: BLE001
            fallback = self._fallback_results(query, request_limit, allowed)
            return {
                "ok": True,
                "error": f"SearXNG request failed: {exc}. Returned fallback results.",
                "results": [item.__dict__ for item in fallback],
                "is_fallback": True,
            }
