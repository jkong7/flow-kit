#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Flow Status
# @raycast.mode inline
# @raycast.refreshTime 1m
# @raycast.packageName flow-kit
# @raycast.icon ⏱️

KIT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
"$KIT/bin/flow" status -q
