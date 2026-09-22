#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Rewrite Selection
# @raycast.mode silent
# @raycast.packageName flow-kit
# @raycast.icon 🪄
# @raycast.argument1 { "type": "dropdown", "placeholder": "Style", "data": [{"title": "Professional", "value": "pro"}, {"title": "Casual", "value": "casual"}, {"title": "Shorter", "value": "shorter"}, {"title": "Clearer", "value": "rewrite"}] }

KIT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
"$KIT/bin/ask" "${1:-rewrite}" --selection --paste --no-copy >/dev/null && echo "Rewritten"
