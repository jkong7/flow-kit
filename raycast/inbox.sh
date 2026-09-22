#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Inbox
# @raycast.mode inline
# @raycast.refreshTime 5m
# @raycast.packageName flow-kit
# @raycast.icon 📥

KIT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
n="$("$KIT/bin/capture" --count)"
if [ "$n" = "0" ]; then echo "Inbox zero"; else echo "$n open · oldest: $("$KIT/bin/capture" --list | head -1 | cut -c5-)"; fi
