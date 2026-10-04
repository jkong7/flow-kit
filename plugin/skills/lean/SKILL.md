---
name: lean
description: "Audit this Mac for bloat and reclaim RAM and disk: background services, stray dev servers, caches, merged git worktrees, idle node_modules, local models, big project folders. Lists everything with sizes and recommendations, asks what to remove, and acts only on what I pick. Use when the user says lean, clean up, free up space or RAM, what's running, what's bloating my machine, or reclaim storage."
argument-hint: "[focus: ram | disk | <path>]"
---

Keep my machine lean: everything installed or running should be there because I need it right now. Anything else gets removed and comes back on demand.

1. **Scan.** Run `lean --json` (it is in flow-kit's `bin/`; if it is not on PATH, use `~/dev/flow-kit/bin/lean`). It is read-only. If $ARGUMENTS names a focus, weight the presentation toward it (`ram` → services and servers; `disk` → the rest; a path → findings under it).

2. **Sanity check what the scanner can't know**, only for review items that are big or permanent:
   - A big project folder that is not a git repo: list its top-level contents and sizes so I can see what's in it.
   - A worktree with unmerged commits: show `git log --oneline <base>..<branch>` and whether the branch exists on origin.
   - A brew service: grep `~/dev` and `~/.local/bin` for anything that uses it, so I know what would break.
   - Ollama or Hugging Face models: grep `~/dev`, `~/brain` and `~/.local/bin` for the model name.

3. **Present** one compact table per category: item, size or RAM, risk (`safe` = regenerates, nothing lost; `review` = my call), and a one-line recommendation. Lead with the total that the recommended set frees. Mark anything that would lose work (unpushed commits, uncommitted changes, non-git folders) in plain words.

4. **Ask** with AskUserQuestion, multiSelect, one question per group (max 4 options each; bundle by category when there are more):
   - "Recommended (safe)": everything with `recommend: true`, as one option or a few bundles.
   - Review items, biggest first.
   - Always include an option to mark items "keep, stop suggesting".
   Never pre-select or assume a yes.

5. **Act on exactly what I picked**, using each finding's `action`. Run them one category at a time so permission prompts stay readable. Never act on an unpicked item, and never widen a command (no `rm -rf` on a parent folder, no `--force` that the finding didn't include). For `downloads:old` the action only lists files; show them and ask again before deleting anything.

6. **Remember** "keep" answers with `lean --keep <id> ...` so they never come up again.

7. **Report**: what was removed, what each freed, the new free disk (`df -h /System/Volumes/Data`) and memory pressure (`memory_pressure | tail -1`), and the one-line command to bring each removed thing back (for example `brew services start redis`, `pnpm install`, `ollama pull qwen3:8b`).

Rules: nothing is deleted without my explicit pick in this run. If a permission prompt or guard blocks an action, stop and tell me; don't route around it.
