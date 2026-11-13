#!/usr/bin/env python3
"""Write the latest YouTube video and blog post into site/index.html.

Rewrites the HTML between the <!-- latest:video:start/end --> and
<!-- latest:post:start/end --> markers. Run every 8 hours by
.github/workflows/update-latest.yaml, which formats the file with prettier and
commits it when it changed; that push triggers the Pages and Docker builds.

Stdlib only. A feed that can't be read leaves its card as committed; exits non-zero
only if neither feed could be read.
"""

from __future__ import annotations

import html
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

YOUTUBE_CHANNEL_ID = "UChoN8zyrrkFGiHdd9iiqLZQ"
# The channel feed 404s for some callers (GitHub runners included), so fall back to the
# channel's "uploads, no Shorts" playlist (UULF + the channel ID without its "UC" prefix).
YOUTUBE_FEEDS = [
    f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}",
    f"https://www.youtube.com/feeds/videos.xml?playlist_id=UULF{YOUTUBE_CHANNEL_ID[2:]}",
]
BLOG_FEED = "https://mirceanton.com/feed.xml"

INDEX = Path(__file__).resolve().parent.parent / "site" / "index.html"
ATOM = {"a": "http://www.w3.org/2005/Atom"}


def fetch(url: str, attempts: int = 5) -> ET.Element:
    """GET and parse a feed, retrying: YouTube's feed endpoint returns sporadic 404s/5xx."""
    req = urllib.request.Request(url, headers={"User-Agent": "links-latest-updater"})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return ET.fromstring(resp.read())
        except (urllib.error.URLError, TimeoutError, ET.ParseError) as exc:
            if attempt == attempts:
                raise RuntimeError(f"{url}: {exc}") from exc
            delay = 5 * 2 ** (attempt - 1)
            print(f"warn: {url}: {exc}; retry {attempt}/{attempts - 1} in {delay}s", file=sys.stderr)
            time.sleep(delay)
    raise AssertionError("unreachable")


def latest_video() -> tuple[str, str]:
    """Newest entry in the channel's Atom feed, skipping Shorts."""
    errors = []
    for url in YOUTUBE_FEEDS:
        try:
            root = fetch(url, attempts=2)
        except RuntimeError as exc:
            errors.append(str(exc))
            continue
        for entry in root.iterfind("a:entry", ATOM):
            link = entry.find("a:link", ATOM).get("href", "")
            if "/shorts/" in link:
                continue
            return entry.findtext("a:title", "", ATOM).strip(), link
        errors.append(f"{url}: no non-Short videos")
    raise RuntimeError("; ".join(errors))


def latest_post() -> tuple[str, str]:
    """First item in the blog's RSS feed (Hugo lists newest first)."""
    item = fetch(BLOG_FEED).find("channel/item")
    if item is None:
        raise RuntimeError("no items in the blog feed")
    return item.findtext("title", "").strip(), item.findtext("link", "").strip()


CARD = """\
        <a
          class="card card--{kind}"
          href="{href}"
          target="_blank"
          rel="noopener"
          data-umami-event="link-click"
          data-umami-event-link="latest-{kind}"
        >
          {icon}
          <span class="card__label">
            <span class="kicker">latest {kind}</span>
            {title}
          </span>
        </a>"""

ICONS = {
    "video": '<span class="play" aria-hidden="true"></span>',
    "post": '<span class="prompt" aria-hidden="true">&gt;_</span>',
}


def card(kind: str, title: str, href: str) -> str:
    """Formatted like prettier's output, so a local run followed by prettier keeps lint green."""
    return CARD.format(
        kind=kind, icon=ICONS[kind], href=html.escape(href), title=html.escape(title)
    )


def replace_block(page: str, kind: str, content: str) -> str:
    pattern = re.compile(
        rf"(<!-- latest:{kind}:start -->).*?(\n[ \t]*<!-- latest:{kind}:end -->)",
        re.DOTALL,
    )
    if not pattern.search(page):
        raise RuntimeError(f"latest:{kind} markers not found in {INDEX}")
    return pattern.sub(lambda m: f"{m.group(1)}\n{content}{m.group(2)}", page, count=1)


def main() -> int:
    """Update each card independently; a source that fails keeps its committed card."""
    page = INDEX.read_text(encoding="utf-8")
    failed = 0
    for kind, getter in (("video", latest_video), ("post", latest_post)):
        try:
            title, href = getter()
            if not (title and href):
                raise RuntimeError(f"empty title or link: {title!r} {href!r}")
        except Exception as exc:  # network, parse or empty feed
            print(f"warn: latest {kind} not updated: {exc}", file=sys.stderr)
            failed += 1
            continue
        page = replace_block(page, kind, card(kind, title, href))
        print(f"{kind}: {title} <{href}>")
    INDEX.write_text(page, encoding="utf-8")
    # Only fail when nothing could be fetched; one flaky feed shouldn't turn CI red.
    return 1 if failed == 2 else 0


if __name__ == "__main__":
    sys.exit(main())
