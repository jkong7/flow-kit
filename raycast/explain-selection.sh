#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Explain Selection
# @raycast.mode fullOutput
# @raycast.packageName flow-kit
# @raycast.icon 💡

KIT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
"$KIT/bin/ask" explain --selection --no-copy
