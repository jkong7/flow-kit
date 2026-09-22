---
description: Sunday review of what you shipped, what slipped, where the time went, and the top 3 for next week.
argument-hint: "[week offset, e.g. 'last week']"
---

Run my weekly review for the past 7 days (or $ARGUMENTS).

Gather, read-only:
- **Calendar**: events attended. Group the hours by area (classes, job search, work, meetings, personal).
- **Focus log**: if `flow` exists, run `flow log --days 7` for deep-work time and completion rate.
- **Email**: threads I started or replied to that moved something forward (applications, scheduling, decisions).
- **Tasks**: capture-inbox items checked off vs. still open (`capture --list`), and any Notion tasks completed.
- **Git**: `git log --since="7 days ago" --author="$(git config user.email)" --oneline` in each repo under the current directory (depth 2) that I committed to.

Write the review:

## Wins
3–6 bullets, concrete.

## Slipped
What I meant to do and didn't, with a one-line honest reason for each.

## Time
A table: area · hours · % of the week. One sentence on whether that matches what I said matters.

## Open loops
Anything waiting on me or on someone else. Mention `/followups` if there are several of the latter.

## Next week's top 3
Specific outcomes, not activities.

## One change
A single experiment for next week (a habit, a block, a rule).

Ask whether to save it before writing anywhere. Suggest a Notion page titled `Weekly review · <Mon date>`.
