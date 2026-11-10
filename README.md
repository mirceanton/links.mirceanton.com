# links.mirceanton.com

A minimalist "link in bio" style landing page that aggregates all my social media profiles and important links in one place.

## Latest video and post

The two cards at the top are filled in at build time by `scripts/update-latest.py`, from the YouTube channel feed and `https://mirceanton.com/feed.xml`. The GitHub Pages workflow runs it on every push and every 8 hours; the Docker workflow runs it on each image build. If a feed can't be read, the values committed in `site/index.html` ship instead.

To refresh the committed fallback locally:

```bash
python3 scripts/update-latest.py && mise exec -- prettier --write site/index.html
```
