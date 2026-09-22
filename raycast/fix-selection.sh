#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Fix Selection
# @raycast.mode silent
# @raycast.packageName flow-kit
# @raycast.icon ✍️

KIT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
"$KIT/bin/ask" fix --selection --paste --no-copy >/dev/null && echo "Fixed"
