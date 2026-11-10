#!/usr/bin/env python3
"""Write the latest YouTube video and blog post into site/index.html.

Rewrites the HTML between the <!-- latest:video:start/end --> and
<!-- latest:post:start/end --> markers. Run every 8 hours by
.github/workflows/update-latest.yaml, which formats the file with prettier and
commits it when it changed; that push triggers the Pages and Docker builds.

Stdlib only. Exits non-zero, leaving the file untouched, if a feed can't be read.
"""

from __future__ import annotations

import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

YOUTUBE_CHANNEL_ID = "UChoN8zyrrkFGiHdd9iiqLZQ"
YOUTUBE_FEED = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"
BLOG_FEED = "https://mirceanton.com/feed.xml"

INDEX = Path(__file__).resolve().parent.parent / "site" / "index.html"
ATOM = {"a": "http://www.w3.org/2005/Atom"}


def fetch(url: str) -> ET.Element:
    req = urllib.request.Request(url, headers={"User-Agent": "links-latest-updater"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return ET.fromstring(resp.read())


def latest_video() -> tuple[str, str]:
    """Newest entry in the channel's Atom feed, skipping Shorts."""
    for entry in fetch(YOUTUBE_FEED).iterfind("a:entry", ATOM):
        link = entry.find("a:link", ATOM).get("href", "")
        if "/shorts/" in link:
            continue
        return entry.findtext("a:title", "", ATOM).strip(), link
    raise RuntimeError("no non-Short videos in the YouTube feed")


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
    try:
        video = latest_video()
        post = latest_post()
    except Exception as exc:  # network, parse or empty feed
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not all(video) or not all(post):
        print(f"error: empty title or link: {video!r} {post!r}", file=sys.stderr)
        return 1

    page = INDEX.read_text(encoding="utf-8")
    page = replace_block(page, "video", card("video", *video))
    page = replace_block(page, "post", card("post", *post))
    INDEX.write_text(page, encoding="utf-8")
    print(f"video: {video[0]} <{video[1]}>")
    print(f"post:  {post[0]} <{post[1]}>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
