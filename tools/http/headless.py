"""
Headless HTML fetcher (best-effort). Utilise Playwright si disponible, sinon retourne None.
"""
from __future__ import annotations

from typing import Optional

try:
    from playwright.sync_api import sync_playwright  # type: ignore

    HAS_PLAYWRIGHT = True
except Exception:  # pragma: no cover - absence de Playwright
    HAS_PLAYWRIGHT = False


def fetch_headless(url: str, timeout: int = 10, user_agent: Optional[str] = None, proxy: Optional[str] = None) -> Optional[str]:
    if not HAS_PLAYWRIGHT:
        return None
    try:
        with sync_playwright() as p:  # pragma: no cover - dépend de l'env runtime
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=user_agent, proxy={"server": proxy} if proxy else None)
            page = context.new_page()
            page.goto(url, timeout=timeout * 1000)
            content = page.content()
            browser.close()
            return content
    except Exception:
        return None
