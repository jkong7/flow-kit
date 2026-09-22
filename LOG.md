# Log

## 2026-09-21

**State**
- Researched popular automations across four areas: Claude Code, Raycast, macOS keyboard tools, and personal AI automations.
- Built and tested everything in this repo: 67 tests, CI green on macOS and Ubuntu.
- Plugin `flow-kit@flow-kit` v0.2.0 is installed at user scope: hooks, 6 skills and `/push`. Verified in a fresh session.
- v0.2.0 turned `today`, `plan-day`, `followups`, `prep`, `weekly-review` and `triage-inbox` from commands into skills. `/push` stays a command on purpose.
- Nothing else is wired into the machine yet.

**Next**
- [ ] Raycast → Settings → Keyboard → Hyper Key = Caps Lock (manual; Raycast has no config file for it)
- [ ] Add the `skhd/skhdrc.example` bindings to `~/.config/skhd/skhdrc`, then `skhd --restart-service`. Keep the existing ⌘1/⌘2/⌘3 launchers.
- [ ] Add the statusline to `~/.claude/settings.json`
- [ ] Set `"attribution": {"commit": "", "pr": ""}` in `~/.claude/settings.json`
- [ ] Add `raycast/` as a Raycast Script Commands directory (manual)
- [ ] Create `~/.config/flowkit/flow.json` (Spotify focus playlist, apps to open)
- [ ] Two Apple Shortcuts that turn a Work Focus on and off, named in `flow.json`
- [ ] Schedule the `today` skill for weekday mornings
- [ ] Later: voice dictation, Canvas deadline sync, parallel worktree sessions

**Resume**
- Update the plugin after pushing: `claude plugin marketplace update flow-kit && claude plugin update flow-kit@flow-kit`
- Checks: `make check`
- House rules: no code comments, one commit per component, no co-author trailers.
