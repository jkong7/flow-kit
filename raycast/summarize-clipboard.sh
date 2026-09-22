#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Summarize Clipboard
# @raycast.mode fullOutput
# @raycast.packageName flow-kit
# @raycast.icon 📋

KIT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
pbpaste | "$KIT/bin/ask" bullets
