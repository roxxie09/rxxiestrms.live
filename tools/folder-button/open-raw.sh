#!/bin/bash
# Shows a /raw page selected in Finder or your file manager. Started by the folder buttons in the EPG logo dashboard.
# The links look like  roxie-raw:raw/tsn5.html  - only a plain page name is accepted, nothing else is opened.
HERE="$(cd "$(dirname "$0")" && pwd)"
RAW="$(cd "$HERE/../.." && pwd)/raw"
name="$(printf '%s' "${1:-}" | sed -n -E 's#^[Rr][Oo][Xx][Ii][Ee]-[Rr][Aa][Ww]:(//)?/?raw/([A-Za-z0-9-][A-Za-z0-9_-]*\.html)/?$#\2#p')"
file="$RAW/$name"
if [ "$(uname)" = Darwin ]; then
  if [ -n "$name" ] && [ -f "$file" ]; then open -R "$file"; else open "$RAW"; fi
  exit 0
fi
if [ -n "$name" ] && [ -f "$file" ] && command -v dbus-send >/dev/null 2>&1; then
  uri="file://$(printf '%s' "$file" | sed 's/%/%25/g; s/ /%20/g')"
  dbus-send --session --print-reply --dest=org.freedesktop.FileManager1 --type=method_call \
    /org/freedesktop/FileManager1 org.freedesktop.FileManager1.ShowItems array:string:"$uri" string:"" >/dev/null 2>&1 && exit 0
fi
xdg-open "$RAW" >/dev/null 2>&1 &
