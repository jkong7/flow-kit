---
name: today
description: "Daily brief from calendar, email, Todoist, yesterday's handoff and the capture inbox: one thing to start with, top 3, schedule with free blocks, threads needing a reply (with drafts), 72h deadlines. Use when the user asks what's on today, for a morning/daily brief, 'what do I have going on', or 'catch me up'. Read-only; drafts, never sends."
argument-hint: "[focus area, e.g. 'job search']"
---

Build my brief for today. Work read-only except for two things: you may create Gmail **drafts**, and you may add Todoist tasks for deadlines found in email. Never send, archive, label, or delete anything, and never create or edit calendar events.

Gather, using whatever connectors are available (skip any that aren't and say so in one line at the end):

1. **Calendar**: today's events plus anything tomorrow before 10am. Flag conflicts, back-to-backs with no break, and events with no location or link.
2. **Email**: unread or starred threads from the last 24h that are from a real person or need action. Ignore newsletters, promotions and automated notifications unless they carry a deadline.
3. **Handoff**: the most recent `${FLOWKIT_BRAIN:-~/brain}/daily/YYYY-MM-DD.md` before today. Start from its "Tomorrow first" and "Open loops", and never raise anything under "Don't bring up again".
4. **Tasks**: Todoist tasks due today or overdue (`find-tasks-by-date`), plus `p1` tasks due in the next 3 days. Also open items in the capture inbox (`capture --list` if the CLI exists, otherwise `${FLOWKIT_INBOX:-~/.local/share/flowkit/inbox.md}` and `${FLOWKIT_BRAIN:-~/brain}/inbox/`).
5. **Deadlines**: anything due in the next 72 hours mentioned in email, calendar or tasks. If an email carries a deadline or a clear to-do that isn't in Todoist yet, add it to the right Todoist project with the `from-email` label (afternoon due time, never mornings) and mark it `(added)` in the brief.

$ARGUMENTS

Output, in this order and nothing else:

## Start with
One thing, one line, and why it beats everything else. Not a menu.

## Top 3
The three things that most deserve my attention today, one line each, each with *why today*.

## Schedule
A compact timeline (`9:30–10:20  Operating Systems (Tech L361)`). Mark free blocks of 45 min or more as `▢ free`; these are where deep work goes.

## Needs a reply
One line per thread: who, what they need, and how urgent. If a reply is simple, draft it in Gmail and mark the line `(draft ready)`.

## Coming up
Deadlines in the next 72h.

## Inbox
Count of open capture items, and the 3 oldest.

## Overdue
Count of overdue Todoist tasks and the oldest three. Don't reschedule them here; that's `shutdown`'s job.

Keep the whole thing readable in under two minutes.
