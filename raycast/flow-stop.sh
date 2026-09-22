#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Stop Flow
# @raycast.mode silent
# @raycast.packageName flow-kit
# @raycast.icon ⏹️

KIT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
"$KIT/bin/flow" stop | sed 's/^flow: //' | tail -1
