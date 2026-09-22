#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Ask Claude
# @raycast.mode fullOutput
# @raycast.packageName flow-kit
# @raycast.icon 🤖
# @raycast.argument1 { "type": "text", "placeholder": "Question" }
# @raycast.argument2 { "type": "dropdown", "placeholder": "Context", "optional": true, "data": [{"title": "No context", "value": "none"}, {"title": "With clipboard", "value": "clip"}] }

KIT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
if [ "$2" = "clip" ]; then
  pbpaste | "$KIT/bin/ask" "$1" -m sonnet
else
  FLOWKIT_IGNORE_STDIN=1 "$KIT/bin/ask" "$1" -m sonnet < /dev/null
fi
