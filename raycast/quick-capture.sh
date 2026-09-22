#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Quick Capture
# @raycast.mode silent
# @raycast.packageName flow-kit
# @raycast.icon 📥
# @raycast.argument1 { "type": "text", "placeholder": "Thought" }

KIT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
"$KIT/bin/capture" "$1" >/dev/null && echo "Captured ($("$KIT/bin/capture" --count) open)"
