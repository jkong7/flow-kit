#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Capture Browser Tab
# @raycast.mode silent
# @raycast.packageName flow-kit
# @raycast.icon 🔖
# @raycast.argument1 { "type": "text", "placeholder": "Note (optional)", "optional": true }

KIT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
"$KIT/bin/capture" --tab "$1" >/dev/null && echo "Tab captured"
