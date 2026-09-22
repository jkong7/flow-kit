---
name: followups
description: "Find sent emails that never got a reply and draft polite in-thread follow-ups, ranked interviews > recruiters > professors. Use when the user asks who hasn't replied, what they're waiting on, to chase or nudge people, or about recruiter follow-ups. Drafts only, never sends."
argument-hint: "[days, default 5] [filter, e.g. 'recruiters']"
---

Find conversations where I'm waiting on someone, and draft nudges.

Arguments: $ARGUMENTS. The first number is the minimum days of silence (default **5**). Any remaining words narrow the search (e.g. "recruiters", "professors", a company name).

1. Search my Gmail **sent** mail from the last 30 days for threads where the **last message is mine**, it was sent at least N days ago, and it was addressed to a real person (skip no-reply addresses, mailing lists, and threads I closed out with "thanks!"-type messages).
2. For each thread, work out what I was asking for: an application status, a meeting time, a document, an answer.
3. Rank by importance: interviews and offers first, then recruiters and hiring managers, then professors and advisors, then everything else.
4. Draft a follow-up **in the same thread** for each of the top 10:
   - 2–4 sentences, warm, not apologetic, and no "just bumping this".
   - Restate the ask in one line and make it easy to answer (offer two times, or a yes/no).
   - The second nudge on a thread should be shorter than the first. If I've already nudged twice, don't draft; flag it as "consider closing the loop".
5. Never send. Create drafts only.

Output a table: who · subject · days waiting · ask · status (`draft ready` / `flagged`). Then give one line on anything that looks like it slipped through the cracks.
