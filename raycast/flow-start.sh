#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Start Flow
# @raycast.mode silent
# @raycast.packageName flow-kit
# @raycast.icon 🎧
# @raycast.argument1 { "type": "text", "placeholder": "Minutes", "optional": true }
# @raycast.argument2 { "type": "text", "placeholder": "Goal", "optional": true }

KIT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
"$KIT/bin/flow" start ${1:+"$1"} ${2:+"$2"} | sed 's/^flow: //' | tail -1
