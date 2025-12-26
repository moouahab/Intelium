"""
Headless HTML fetcher extensible.
Stratégie par défaut : Playwright (si disponible). Retourne None sinon.
"""
from __future__ import annotations

from typing import Optional, Protocol

try:
    from playwright.sync_api import sync_playwright  # type: ignore

    HAS_PLAYWRIGHT = True
except Exception:  # pragma: no cover - absence de Playwright
    HAS_PLAYWRIGHT = False

try:
    from selenium import webdriver  # type: ignore
    from selenium.webdriver.chrome.options import Options as ChromeOptions  # type: ignore

    HAS_SELENIUM = True
except Exception:  # pragma: no cover - absence de Selenium
    HAS_SELENIUM = False


class HeadlessStrategy(Protocol):
    def fetch(self, url: str, timeout: int = 10, user_agent: Optional[str] = None, proxy: Optional[str] = None) -> Optional[str]:
        ...


class PlaywrightStrategy:
    def fetch(self, url: str, timeout: int = 10, user_agent: Optional[str] = None, proxy: Optional[str] = None) -> Optional[str]:
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


class SeleniumStrategy:
    def fetch(self, url: str, timeout: int = 10, user_agent: Optional[str] = None, proxy: Optional[str] = None) -> Optional[str]:
        if not HAS_SELENIUM:
            return None
        try:
            opts = ChromeOptions()
            opts.add_argument("--headless=new")
            opts.add_argument(f"--timeout={timeout}")
            if user_agent:
                opts.add_argument(f"user-agent={user_agent}")
            if proxy:
                opts.add_argument(f"--proxy-server={proxy}")
            driver = webdriver.Chrome(options=opts)  # pragma: no cover - dépend de l'env runtime
            driver.set_page_load_timeout(timeout)
            driver.get(url)
            content = driver.page_source
            driver.quit()
            return content
        except Exception:
            return None


def get_default_headless_strategy() -> Optional[HeadlessStrategy]:
    if HAS_PLAYWRIGHT:
        return PlaywrightStrategy()
    if HAS_SELENIUM:
        return SeleniumStrategy()
    return None


def fetch_headless(url: str, timeout: int = 10, user_agent: Optional[str] = None, proxy: Optional[str] = None) -> Optional[str]:
    """
    Compat : utilise la stratégie par défaut (Playwright si dispo).
    """
    strategy = get_default_headless_strategy()
    if not strategy:
        return None
    return strategy.fetch(url, timeout=timeout, user_agent=user_agent, proxy=proxy)
