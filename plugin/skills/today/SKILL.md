---
name: today
description: "Morning brief from calendar, email, tasks and the capture inbox: top 3, schedule with free blocks, threads needing a reply (with drafts), 72h deadlines. Use when the user asks what's on today, for a morning/daily brief, 'what do I have going on', or 'catch me up'. Read-only; drafts, never sends."
argument-hint: "[focus area, e.g. 'job search']"
---

Build my morning brief for today. Work read-only. You may create Gmail **drafts** but never send, archive, label, or delete anything, and never create or edit calendar events.

Gather, using whatever connectors are available (skip any that aren't and say so in one line at the end):

1. **Calendar**: today's events plus anything tomorrow before 10am. Flag conflicts, back-to-backs with no break, and events with no location or link.
2. **Email**: unread or starred threads from the last 24h that are from a real person or need action. Ignore newsletters, promotions and automated notifications unless they carry a deadline.
3. **Tasks**: open items in the capture inbox (run `capture --list` if the `capture` CLI exists, otherwise read `${FLOWKIT_INBOX:-~/.local/share/flowkit/inbox.md}`), plus any Notion task database I use, due today or overdue.
4. **Deadlines**: anything due in the next 72 hours mentioned in email, calendar or tasks.

$ARGUMENTS

Output, in this order and nothing else:

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

Keep the whole thing readable in under two minutes.
