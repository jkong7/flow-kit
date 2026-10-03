---
name: shutdown
description: "End-of-day shutdown: check off what got done, roll unfinished Todoist tasks forward, sync project next steps from today's git work, write tomorrow's handoff and log decisions. Use when the user says 'done for today', 'shutdown', 'wrap up', 'end of day', or 'I'm done'. Never sends anything."
argument-hint: "[anything to note, e.g. 'decided to drop sidebet']"
---

Run my end-of-day shutdown. The vault is `${FLOWKIT_BRAIN:-~/brain}`; today's date is the local date. Never send, share or delete anything. Todoist changes are limited to completing, rescheduling, labeling and adding tasks; never delete a task.

Note from me: $ARGUMENTS

1. **What got done today.** Gather it from:
   - Todoist: tasks completed today (`find-completed-tasks` for today).
   - Git: `git log --since=midnight --author="$(git config user.name)" --oneline` in every repo under `~/dev` that has commits today.
   - This conversation and any other Claude Code sessions today, if visible.
   - `~/.local/state/flowkit/actions.jsonl` entries from today (drafts made, tasks added).
   If something was clearly finished but its Todoist task is still open, list it and ask before completing it.

2. **Roll forward.** For every open Todoist task that was due today or earlier:
   - Move it with `reschedule-tasks` (never `update-tasks`, which breaks recurrence) to tomorrow at a sensible afternoon time (12pm or later, never mornings).
   - Add the `rolled-over` label.
   - If a task has rolled over 3 or more days in a row (check its labels and the last handoffs), don't move it silently. Put it under **Stuck** in the summary with three options: do it tomorrow first, break it into a smaller first step, or drop it.
   Skip recurring habit tasks that simply recur.

3. **Projects.** For each repo with commits today, update `projects/<repo>.md` in the vault: one dated line under History, and refresh Next steps. Add any new concrete next step to the Todoist Projects section for that repo, and complete tasks the commits clearly finished (ask first if unsure).

4. **Decisions.** Read my note above and today's conversation for decisions (what I chose and why). Append each to `decisions/log.md` as `- YYYY-MM-DD: <decision>. Why: <reason>. Source: <where>.` If I gave none, ask me for one or two lines ("anything you decided or learned today?") and log what I say; if I skip, log nothing.

5. **People.** If today involved a person (email drafted, call, interview, coffee chat), append a dated line to their `people/<name>.md` History and update `last_contact`. Create the page only if they're someone I'm actively dealing with.

6. **Handoff.** Write `daily/YYYY-MM-DD.md` (today's date), overwriting if it exists:
   ```
   # YYYY-MM-DD
   ## Done
   - ...
   ## Tomorrow first
   - <the one thing to start with, and why>
   ## Open loops
   - <waiting on people, half-finished work, with where it lives>
   ## Don't bring up again
   - <things resolved or dropped today>
   ```
   Keep it under 20 lines. `today` reads this tomorrow.

7. **Commit the vault**: `git -C ${FLOWKIT_BRAIN:-~/brain} add -A && git -C ${FLOWKIT_BRAIN:-~/brain} commit -qm "Shutdown YYYY-MM-DD"`.

8. Complete the recurring "Done for today" Todoist task if it's due.

Reply with at most 10 lines: done count, what rolled (and anything Stuck), tomorrow's first thing, and anything you need me to confirm. Don't rewrite Claude's memory files here; that happens in the weekly review.
