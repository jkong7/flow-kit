---
name: weekly-review
description: "Weekly review: wins, what slipped, planned vs actual, goals check, open loops, next week's top 3, one experiment, plus the dream pass that verifies and cleans Claude's memory and the vault. Use when the user asks for a weekly review, 'how did my week go', a retro, Sunday planning, or 'dream'."
argument-hint: "[week offset, e.g. 'last week']"
---

Run my weekly review for the past 7 days (or $ARGUMENTS). The vault is `${FLOWKIT_BRAIN:-~/brain}`. Never send, share or delete outside the vault and memory, and show me every memory change before writing it.

## Part 1: Review

Gather, read-only:
- **Todoist**: tasks completed this week (`find-activity`, completed, my user id) by project; tasks with the `rolled-over` label; overdue count.
- **Calendar**: events attended and time blocks planned. Group hours by area (classes, job search, projects, meetings, personal).
- **Handoffs**: this week's `daily/*.md` files ("Tomorrow first" vs what actually got done).
- **Git**: `git log --since="7 days ago" --author="$(git config user.name)" --oneline` in every repo under `~/dev` with commits.
- **Email**: threads I started or replied to that moved something forward.
- **Goals**: `me/goals.md`. **Decisions**: this week's lines in `decisions/log.md`.
- **Agent actions**: `~/.local/state/flowkit/actions.jsonl` for the week (what Claude changed on my behalf).

Write:

### Wins
3 to 6 concrete bullets.

### Slipped
What I meant to do and didn't, each with a one-line honest reason. Name tasks that rolled over 3+ times and recommend do, shrink, or drop for each.

### Planned vs actual
A table: area · planned hours (calendar blocks, Todoist durations) · actual (calendar, commits, completed tasks) · %. One sentence on whether that matches `me/goals.md`.

### Goals check
For each goal: on track, behind, or untouched this week, with the evidence. Flag any goal with no activity for two weeks and ask whether it is still a goal.

### Open loops
Waiting on me or on someone else. Suggest `followups` if several are on others.

### Next week's top 3
Specific outcomes, not activities. Offer to add them to Todoist as p1 tasks.

### One change
A single experiment for next week.

## Part 2: Dream (memory and vault upkeep)

1. **Verify Claude's memory.** For each file in the auto-memory directory (the one holding `MEMORY.md`), check its claims against sources: git state of repos it names, Todoist, the ledger, calendar, recent email, the vault. Classify each memory as **confirmed**, **stale** (true once, now outdated), **wrong**, or **status-not-rule** (project status that belongs in `projects/<repo>.md`, not memory).
2. **Propose changes as a diff**, then wait for my yes:
   - wrong: delete the wrong claim outright (never just mark it stale);
   - stale: rewrite with the current fact and an absolute date;
   - status-not-rule: move the status into the vault project page and leave only rules and durable facts in memory;
   - duplicates: merge.
   Every surviving fact gets an absolute date and a source.
3. **Wiki lint** (Karpathy LLM-wiki pattern; start from `index.md` and this week's `log.md` lines):
   - orphans: notes nothing links to and that link to nothing;
   - contradictions: two notes stating different facts (dates, statuses, people's roles), with the newer sourced fact winning;
   - superseded claims: facts a newer note or log line replaced;
   - unsourced AI claims: synthesis lines with no link, URL or ledger/email id;
   - `## Suggested links` sections: confirm or drop each suggestion.
   Propose fixes in the same diff as the memory changes. After applying, append one `log.md` line per change and rerun `python3 .tools/build_index.py`.
4. **Vault hygiene.** Projects with no commits in 14 days: ask keep active or park. People with open loops older than 14 days: list them. Ideas added this week: suggest links to related notes, projects or classes.
5. **Me.** If this week's decisions or behavior show a new preference, goal or change in direction, propose an edit to `me/preferences.md` or `me/goals.md`.
6. After my approval, apply the changes, then commit the vault: `git -C ${FLOWKIT_BRAIN:-~/brain} add -A && git -C ${FLOWKIT_BRAIN:-~/brain} commit -qm "Weekly review YYYY-MM-DD"`.

Save the review itself to `daily/YYYY-MM-DD-weekly.md` and complete the recurring "Weekly review" Todoist task.
