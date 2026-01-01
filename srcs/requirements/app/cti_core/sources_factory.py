from typing import Optional, Set

from cti_core.Source import Source
from tools.parsing.html_links import extract_links
from tools.providers.http.url_utils import normalize_url
from tools.providers.http.url_policy import UrlPolicy
from tools.config.overrides import normalize_overrides


def enqueue_links(current: Source, depth: int, state, max_depth: int, url_policy: UrlPolicy):
    """
    Extrait les liens HTML et les ajoute dans la queue si autorisés.
    """
    if (
        current.status != "downloaded"
        or current.type != "html"
        or depth >= max_depth
        or not isinstance(current.content, str)
    ):
        return
    for link in extract_links(current.content, current.url):
        if not url_policy.can_follow(current.url, link):
            continue
        if state.already_visited(link):
            continue
        normalized = url_policy.normalize(link)
        name = f"{(current.name or 'source')}-d{depth+1}"
        new_source = Source({"url": normalized, "type": "html", "name": name})
        state.add(new_source, depth + 1)
