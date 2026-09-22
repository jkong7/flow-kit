#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Draft Reply
# @raycast.mode fullOutput
# @raycast.packageName flow-kit
# @raycast.icon ↩️
# @raycast.argument1 { "type": "text", "placeholder": "What to say (optional)", "optional": true }

KIT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
FLOWKIT_IGNORE_STDIN=1 "$KIT/bin/ask" reply ${1:+"$1"} < /dev/null
