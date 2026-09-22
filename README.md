# flow-kit

Small, sharp tools that cut the friction between having a thought and acting on it. It's built around Claude Code, Raycast and a hyper key on macOS.

Each piece is based on an automation that power users keep recommending: the done chime, the dangerous-command guard, pipe-selection-to-Claude, quick capture, one-key focus sessions, a morning brief. Each one is rebuilt here to be dependency-free, testable, and easy to read.

```
hyper+F   fix the selected text in place          hyper+C   capture a thought to your inbox
hyper+R   rewrite selection (pro/casual/shorter)  hyper+B   capture the current browser tab
hyper+E   explain the selection                   hyper+S   start a focus session
hyper+A   ask Claude anything                     hyper+X   stop it
```

| Piece | What it is | Where |
| --- | --- | --- |
| **Claude Code plugin** | Hooks: done/permission chimes, a Bash guard, auto-format. Also 6 skills, a `/push` command, and a statusline. | [`plugin/`](plugin) |
| **`ask`** | Pipe any text through Claude with a preset. Can replace the selection in place. | [`bin/ask`](bin/ask) |
| **`capture`** | One-keystroke inbox (a markdown checklist) for thoughts, links and tabs | [`bin/capture`](bin/capture) |
| **`flow`** | One command to start a focus session: Raycast Focus, DND, Spotify, apps, timer, time log | [`bin/flow`](bin/flow) |
| **Raycast scripts** | 12 script commands wrapping the tools above | [`raycast/`](raycast) |
| **skhd bindings** | Hyper-key map that fires everything without touching Raycast's hotkey UI | [`skhd/skhdrc.example`](skhd/skhdrc.example) |

Requirements: macOS, Python 3.9+ (the system `python3` is fine), and the [Claude Code](https://code.claude.com) CLI for anything AI. No pip installs.

---

## Claude Code plugin

### Hooks

**`notify.py`** runs on `Stop` and `Notification`. You can walk away and come back when it's your turn.
- Each event has its own sound:
  - *Glass*: done
  - *Ping*: needs permission
  - *Tink*: idle
  - *Purr*: has a question
- The banner title is the project folder, so you know which of your sessions is calling. The body is the first line of Claude's last message.
- Quotes and special characters are passed to AppleScript as `argv`, so nothing Claude writes can break the script or inject into it.

| Env | Effect |
| --- | --- |
| `FLOWKIT_NTFY_TOPIC=my-secret-topic` | Also push to [ntfy.sh](https://ntfy.sh), so you get phone notifications with no account |
| `FLOWKIT_NTFY_URL` | Self-hosted ntfy server |
| `FLOWKIT_QUIET_APPS=Terminal,Ghostty` | Skip the banner when you're already looking at the terminal. The sound still plays. |
| `FLOWKIT_MUTE=1` | Banner only |

**`guard_bash.py`** runs on `PreToolUse` for Bash. It lets you allow-list Bash broadly without worrying.
- **Blocked outright:**
  - `rm -rf` on `/`, `~`, `$HOME`, `..` or system dirs
  - force-push to `main`/`master`/`prod`
  - `mkfs`, `dd of=/dev/disk*`, `diskutil erase*`
  - fork bombs
  - `gh repo delete`
- **Forced back to a permission prompt:**
  - `git reset --hard`, `git clean -f`, `git checkout -- .`, `branch -D`, `stash drop`
  - `--no-verify`
  - `curl … | sh`
  - `sudo`
  - `DROP TABLE`
  - `npm publish`
  - `rm -rf .` or `*`
  - force-push to other branches
  - overwriting a shell rc
- The checks parse the shell command, so `echo 'rm -rf /'` and `grep -r sudo .` pass.
- Add your own rules with `FLOWKIT_GUARD_RULES=~/rules.json`:

```json
[{ "pattern": "\\bkubectl\\s+delete\\b", "action": "deny", "reason": "prod cluster" }]
```

**`autoformat.py`** runs on `PostToolUse` for Edit, Write and MultiEdit. It formats the file Claude just touched with a formatter you already have, preferring project-local binaries (`node_modules/.bin`, `.venv/bin`):

| Language | Formatter |
| --- | --- |
| Python | ruff, then black |
| JS/TS/JSON/CSS/HTML/YAML | biome, then prettier |
| Go | gofmt |
| Rust | rustfmt |
| Shell | shfmt |
| Swift | swift-format |
| Lua | stylua |
| Terraform | `terraform fmt` |

It runs silently, costs no tokens, and never blocks. Turn it off with `FLOWKIT_FORMAT_OFF=1`.

### Skills

These run when you ask in plain words ("what's on today?", "who hasn't replied to me?", "prep me for my 3pm") or when you type the slash name. They use whatever connectors you have (Gmail, Google Calendar, Notion, web). They're **draft-only**: they propose, you approve, and they never send.

| Skill | Does |
| --- | --- |
| `/today [focus]` | Morning brief: top 3, today's schedule with free blocks, threads that need a reply (with drafts), 72-hour deadlines, inbox count |
| `/plan-day [must-dos]` | Time-boxes the rest of today around your meetings. Asks for approval, then writes `▢ task` blocks to your calendar and offers to start `flow`. |
| `/followups [days] [filter]` | Finds sent mail with no reply after N days (default 5), ranks it (interviews, then recruiters, then professors), and drafts nudges in-thread |
| `/prep [meeting]` | One-page brief: who they are, your email history, talking points, sharp questions, watch-outs |
| `/weekly-review` | Wins, what slipped, hours by area, open loops, next week's top 3, one experiment. Pulls from calendar, `flow log`, mail, the inbox and git. |
| `/triage-inbox` | Turns each `capture` item into an event, task, reply, read, note or drop. You approve, it carries them out, then checks them off. |

`/push` stays a slash command so that committing and pushing only happens when you ask for it:

| Command | Does |
| --- | --- |
| `/push [context]` | Stage, write the commit message, push, and open or update a PR. Won't commit secrets. Asks before committing to the default branch. |

### Statusline

```
Opus · my-app ⎇ main*↑1 · ctx ▰▰▰▱▱▱▱▱ 38% · 5h 81% · $0.42 · 12m · ⏱ 31m left
```

- The context bar turns yellow at 60% and red at 80%, which is your cue to `/compact` or hand off.
- The 5-hour rate limit appears once it passes 50%.
- A running `flow` session shows its countdown.

Plugins can't set a statusline, so wire it in your settings:

```json
{ "statusLine": { "type": "command", "command": "python3 ~/dev/flow-kit/plugin/statusline/statusline.py" } }
```

### Install

```sh
claude plugin marketplace add jkong7/flow-kit
claude plugin install flow-kit@flow-kit
```

Or try it for one session without installing: `claude --plugin-dir ./plugin`.

---

## `ask`

```sh
ask fix "teh quick brwon fox"            # → The quick brown fox
pbpaste | ask tldr
ask explain                              # no input → uses the clipboard
ask fix --selection --paste              # copy selection, fix, paste back over it
ask reply "yes, but 2pm"                 # clipboard = the email; arg = what you want to say
git add -p && ask commit                 # message for the staged diff
ask what is a monad                      # unknown preset → just a question
ask --list
```

Presets: `fix`, `rewrite`, `pro`, `casual`, `shorter`, `tldr`, `bullets`, `explain`, `eli5`, `reply`, `commit`, `translate`, `todo`. To add your own or override one, drop `~/.config/flowkit/prompts/<name>.md` (the file body becomes the system prompt).

- It runs `claude -p` on your existing Claude Code login.
- **No tools and no settings are loaded**, so it's fast and can't touch your files.
- The default model is `haiku`. Use `-m sonnet` or `FLOWKIT_ASK_MODEL` to change it.
- Output goes to stdout and the clipboard. `--no-copy` skips the clipboard.
- `--selection` and `--paste` send ⌘C/⌘V through System Events, so whatever launches it needs Accessibility permission.
- It strips `CLAUDECODE`/`CLAUDE_CODE_*` from the environment. Without that, `ask` would exit instantly when launched from a terminal that a Claude session spawned.

## `capture`

```sh
capture "email prof about extension"
capture --tab "read before interview"    # front Chrome / Arc / Safari tab as a markdown link
capture --clip
capture --list        # numbered open items
capture --done 3
capture --count       # for status bars
```

The inbox is a plain checklist at `~/.local/share/flowkit/inbox.md` (set `FLOWKIT_INBOX` to put it in Obsidian, iCloud and so on):

```markdown
- [ ] 2026-09-21 14:03 email prof about extension
- [ ] 2026-09-21 14:05 [Some article](https://…) read before interview
```

Capture is instant, and processing happens later with `/triage-inbox`.

## `flow`

```sh
flow start 50 "finish OS problem set"
flow start "write essay"          # default minutes
flow status                       # ⏱ 31m left · finish OS problem set
flow extend 10
flow stop                         # early: logged as partial
flow log --days 7                 # time audit
```

`start` does whatever you enable in `~/.config/flowkit/flow.json` (`flow config` prints the defaults):

```json
{
  "default_minutes": 50,
  "raycast_focus": true,
  "raycast_categories": ["social", "news"],
  "focus_on_shortcut": "Work Focus On",
  "focus_off_shortcut": "Work Focus Off",
  "spotify_playlist": "spotify:playlist:37i9dQZF1DWZeKCadgRdKQ",
  "open_apps": ["Cursor"],
  "open_urls": []
}
```

- **Raycast Focus** blocks distracting apps and sites via `raycast://focus/start`.
- **macOS Focus/DND** has no CLI, so make two one-step Apple Shortcuts ("Set Focus → Work → On/Off") and put their names here.
- A detached timer chimes, notifies, and tears everything down when time's up. Every session goes to `~/.local/state/flowkit/flow-log.jsonl`:

```
Mon Sep 21   3h10m  ●●◐●
top goals:
   1h40m  OS problem set
```

## Raycast

Add `raycast/` as a Script Commands directory (Raycast → Settings → Extensions → Script Commands → Add Directory). You get:

| Command | Mode |
| --- | --- |
| Fix Selection | silent: replaces in place |
| Rewrite Selection (Professional / Casual / Shorter / Clearer) | silent |
| Explain Selection | full output |
| Ask Claude (+ clipboard context) | full output, Sonnet |
| Summarize Clipboard | full output |
| Draft Reply | full output |
| Quick Capture | silent: shows "Captured (3 open)" |
| Capture Browser Tab | silent |
| Inbox | inline: shows the open count in root search |
| Start Flow / Stop Flow | silent |
| Flow Status | inline: live countdown |

## skhd

Raycast hotkeys can only be assigned in its UI. With [skhd](https://github.com/koekeishiya/skhd), the whole key map lives in a file. [`skhd/skhdrc.example`](skhd/skhdrc.example) binds `hyper` (⌃⌥⇧⌘; turn it on in Raycast → Settings → Keyboard → Hyper Key, mapped to Caps Lock) to:
- the tools directly, for instant actions (`hyper+F`, `B`, `I`, `X`)
- Raycast script commands through `raycast://script-commands/<name>` deeplinks, for anything that needs an input field (`hyper+R`, `E`, `A`, `V`, `D`, `C`, `S`)

`hyper+space` opens Raycast AI Chat. The first time a deeplink runs, Raycast asks for confirmation; choose "Always". Paths assume the repo lives at `~/dev/flow-kit`.

---

## Development

```sh
make check      # lint + 67 tests, no network, no side effects
```

- Every side effect (`osascript`, `afplay`, `open`, `shortcuts`, Spotify, ntfy) goes through a `FLOWKIT_DRY_RUN=1` path.
- The tests mock `claude`, `pbcopy` and `pbpaste` on `PATH` and point all state at temp dirs.
- CI runs on macOS and Ubuntu with Python 3.9 and 3.13.

## Credits

Ideas drawn from:
- [claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery)
- [ccstatusline](https://github.com/sirmalloc/ccstatusline)
- [claude-remote-approver](https://github.com/yuuichieguchi/claude-remote-approver) and ntfy
- Teresa Torres' `/today` workflow
- [Boris Cherny's Claude Code tips](https://x.com/bcherny/status/2017742743125299476)
- Raycast's [script-commands](https://github.com/raycast/script-commands)
- the hyper-key setups in [jasonrudolph/keyboard](https://github.com/jasonrudolph/keyboard)

MIT licensed.
