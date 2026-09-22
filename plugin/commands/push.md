---
description: Stage, write a good commit message, push, and open a PR (or update the existing one) in one step.
argument-hint: "[extra context for the commit message]"
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(git branch:*), Bash(git rev-parse:*), Bash(gh pr view:*), Bash(gh pr create:*), Bash(gh repo view:*)
---

Ship the current work.

1. Run `git status` and `git diff` (staged and unstaged). If there's nothing to commit and nothing unpushed, say so and stop.
2. Stage the relevant changes. **Don't stage** secrets (`.env*`, keys, credentials), build output, or large binaries. If any of those are modified, list them and leave them unstaged.
3. Write the commit message:
   - Subject: imperative, under 72 characters, matching the style of `git log --oneline -10`.
   - Body: *why*, not what, only if the change isn't obvious.
   - Extra context from me: $ARGUMENTS
4. If I'm on the default branch (`gh repo view --json defaultBranchRef`), **stop and ask** whether to create a branch first. Suggest a name.
5. Commit, then `git push -u origin HEAD`.
6. If `gh pr view` finds no PR for this branch, and the branch isn't the default, create one with `gh pr create`: a short title and a body with **Summary** (bullets) and **Testing** (what was run). If a PR already exists, print its URL.
7. End with one line: branch → PR URL (or commit SHA if there's no PR).

Never force-push, and never skip hooks.
