#!/bin/sh
set -eu

TEMPLATE="/etc/nginx/html-templates/index.html.template"
OUTPUT="/usr/share/nginx/html/index.html"
PLACEHOLDER="<!-- UMAMI_SCRIPT -->"

if [ -n "${UMAMI_WEBSITE_ID:-}" ]; then
  HOST="${UMAMI_HOST_URL:-https://analytics.mirceanton.com}"
  SCRIPT_TAG="<script defer src=\"${HOST}/script.js\" data-website-id=\"${UMAMI_WEBSITE_ID}\"></script>"
else
  SCRIPT_TAG=""
fi

sed "s#${PLACEHOLDER}#${SCRIPT_TAG}#" "$TEMPLATE" > "$OUTPUT"
