---
description: Process the capture inbox by turning each quick note into a calendar event, task, reply, note, or delete. Proposes first.
---

Triage my capture inbox.

1. Load open items with `capture --list` (or read `${FLOWKIT_INBOX:-~/.local/share/flowkit/inbox.md}`).
2. Classify each one:
   - **event**: has a time or date, or should be scheduled → propose a calendar event (title, time, duration).
   - **task**: a concrete next action → rewrite it as a verb-first task with a due date if one is implied.
   - **reply**: "email/text X about Y" → find the thread and propose a draft.
   - **read**: a link to read later → one-line summary of what's behind it, fetched from the web.
   - **note**: an idea or reference to keep → where it should live.
   - **drop**: stale, done, or no longer relevant.
3. Show a numbered table: item · type · proposed action. Ask me to approve all, or to edit by number ("3 → drop, 5 tomorrow 2pm").
4. After approval, carry out each action with the available connectors (drafts only for email, never send), then check each processed item off with `capture --done N`. Work from the highest number down so the numbering stays stable.
5. Finish with the count processed and anything that's left.
