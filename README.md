# links.mirceanton.com

A minimalist "link in bio" style landing page that aggregates all my social media profiles and important links in one place.

## Latest video and post

The two cards at the top are written into `site/index.html` by `scripts/update-latest.py`, from the YouTube channel feed and `https://mirceanton.com/feed.xml`. The `Update latest video and post` workflow runs it every 8 hours (or on demand) and commits the file as the bot when something changed. That push triggers the Pages and Docker builds, which only run on push. If a feed can't be read, the run fails and nothing is committed.

To refresh them locally:

```bash
python3 scripts/update-latest.py && mise exec -- prettier --write site/index.html
```
