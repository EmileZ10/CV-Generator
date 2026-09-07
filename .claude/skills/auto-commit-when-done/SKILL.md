---
name: auto-commit-when-done
description: Use this immediately after any code change to this repository is complete and its tests pass — do not wait to be asked, and do not treat this as optional. Covers a ticket, a bug fix, a feature, or an edit as small as a one-line tweak. Skip only if the user asked to review first, called the task experimental, or a test is still failing.
---

# Auto-commit when a task is done

## What to do, in order
1. Confirm the full test suite passes (run it if it hasn't been run this session).
2. Confirm any code-review pass has no unresolved findings, or that remaining findings were deliberately left in scope (matches the ticket).
3. Check whether the user asked to review the diff first, or called the task experimental. If so, stop — present the diff instead of committing, and say why.
4. Otherwise, commit to the current branch with a message in this exact format:
   `<type>: <short imperative description>` — add ` (#<issue-number>)` at the end whenever the change closes or relates to a tracked issue; omit it only when there truly is none.
   Allowed types: feat, fix, refactor, test, docs, chore.
   Example: `feat: scope /form editor to current user (#6)`
5. Report the commit hash.

## Completion criterion
Done when either: (a) a commit exists on the current branch, its message matches the format above, and references the relevant issue if one exists; or (b) you've explicitly said why you held off and what's needed from the user.
