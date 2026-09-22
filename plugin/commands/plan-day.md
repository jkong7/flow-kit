---
description: Time-box the rest of today into calendar blocks around your meetings. Proposes first; writes only after you approve.
argument-hint: "[what must get done today]"
---

Plan the rest of my day as time blocks.

1. Read today's calendar from now until end of day (default 6pm unless the calendar shows later commitments).
2. Collect candidate work: $ARGUMENTS, open items from the capture inbox (`capture --list`), and anything due in the next 48h from email, calendar or Notion.
3. Propose a schedule:
   - Deep work in blocks of 50–90 minutes, placed in the largest free gaps, hardest task first.
   - Batch small tasks (email, forms, quick replies) into one 30-minute "admin" block.
   - Leave a 10-minute buffer after meetings and a real lunch if none is scheduled.
   - Never move or overlap an existing event.
   - Show it as a table: time, block, what exactly I'll do, and the *done-when* criterion.
4. **Stop and ask for approval.** Accept edits in plain language ("swap the first two", "no admin block").
5. After I approve, create the blocks on my primary calendar titled `▢ <task>`, with the done-when criterion in the description and no attendees. Then list what you created.

If a block starts within 5 minutes and the `flow` CLI exists, offer to run `flow start <minutes> "<task>"`.
