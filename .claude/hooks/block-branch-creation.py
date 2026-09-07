#!/usr/bin/env python
"""PreToolUse guardrail: refuse shell commands that create a new git branch.

Claude Code runs this before every Bash / PowerShell tool call. It reads the
hook payload from stdin, inspects the command, and if the command would create
a branch it prints a PreToolUse "deny" decision and the agent never runs it.

Blocked:  git checkout -b / -B <name>
          git switch -c / -C / --create <name>
          git branch <name>            (creating, copying or force-creating)

Allowed:  git branch                   (bare listing)
          git branch -a / -r / --list / --contains / --merged / --show-current ...
          git branch -d / -D / -m / -M / -u / --edit-description <name>
          everything that is not a branch-creating git command

Inspired by the git-guardrails-claude-code project: a deterministic PreToolUse
hook that denies the action outright instead of leaving the model to decide.
"""

import json
import re
import sys

MESSAGE = (
    "Branch creation is blocked by the project PreToolUse hook in "
    ".claude/settings.json (.claude/hooks/block-branch-creation.py).\n\n"
    "Creating a git branch (git checkout -b, git switch -c, git branch <name>) "
    "is only allowed when the user has explicitly asked for a new branch in "
    "this conversation.\n\n"
    "Do NOT work around this: do not commit directly to main instead, and do "
    "not ask the user whether to create a branch. Continue the work on the "
    "current branch. If the task genuinely cannot proceed without a new "
    "branch, stop and explain to the user why a branch is needed and let them "
    "ask for it."
)

# git subcommand flags that consume the following token as their value.
BRANCH_VALUE_OPTS = {
    "--contains", "--no-contains", "--merged", "--no-merged", "--points-at",
    "--sort", "--format", "--set-upstream-to", "-u",
}
# Flags that mean "act on / read existing branches", never create.
BRANCH_MODIFY_OPTS = {
    "-d", "-D", "--delete", "-m", "-M", "--move", "--edit-description",
    "--unset-upstream", "--set-upstream-to", "-u",
}
BRANCH_LIST_OPTS = {
    "-a", "--all", "-r", "--remotes", "-l", "--list", "--show-current",
    "--contains", "--no-contains", "--merged", "--no-merged", "--points-at",
    "--format", "--sort",
}
# Flags that create a branch.
BRANCH_CREATE_OPTS = {"-c", "-C", "--copy"}

# git *global* options (before the subcommand) that take a value.
GIT_GLOBAL_VALUE_OPTS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}

OPERATORS = {"&&", "||", ";", "|", "&", "\n", "|&"}


def deny() -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": MESSAGE,
        }
    }))
    sys.exit(0)


def creates_branch(tokens: list[str]) -> bool:
    """Scan a token list for a branch-creating git invocation."""
    i = 0
    n = len(tokens)
    while i < n:
        if tokens[i] != "git":
            i += 1
            continue
        # Collect this git invocation's tokens up to the next shell operator.
        j = i + 1
        seg: list[str] = []
        while j < n and tokens[j] not in OPERATORS and tokens[j] != "git":
            seg.append(tokens[j])
            j += 1

        # Skip leading global options (e.g. `git -C repo checkout -b x`).
        k = 0
        while k < len(seg):
            tok = seg[k]
            if tok in GIT_GLOBAL_VALUE_OPTS:
                k += 2
            elif tok.startswith("-"):
                k += 1
            else:
                break
        sub = seg[k] if k < len(seg) else ""
        args = seg[k + 1:]

        if sub == "checkout":
            if any(a in ("-b", "-B") for a in args):
                return True
        elif sub == "switch":
            if any(a in ("-c", "-C", "--create", "--force-create") for a in args):
                return True
        elif sub == "branch":
            if _branch_args_create(args):
                return True

        i = j
    return False


def _branch_args_create(args: list[str]) -> bool:
    modifying = False
    skip_next = False
    positional = False
    for idx, tok in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if tok == "--":
            continue
        if tok in BRANCH_CREATE_OPTS:
            return True
        if tok in BRANCH_MODIFY_OPTS or tok in BRANCH_LIST_OPTS:
            modifying = True
            if tok in BRANCH_VALUE_OPTS:
                skip_next = True
            continue
        if tok.startswith("--") and "=" in tok:
            modifying = modifying or tok.split("=", 1)[0] in (
                BRANCH_VALUE_OPTS | BRANCH_MODIFY_OPTS | BRANCH_LIST_OPTS
            )
            continue
        if tok.startswith("-"):
            # unknown / harmless flag (-v, -q, -t, -f, --color, --column, ...)
            continue
        positional = True
    return positional and not modifying


def regex_fallback(command: str) -> bool:
    """Used only when the command cannot be tokenised (unbalanced quotes)."""
    for line in re.split(r"&&|\|\||;|\||\n|&", command):
        if re.search(r"\bgit\b.*\bcheckout\b.*(?:\s|^)-[bB]\b", line):
            return True
        if re.search(r"\bgit\b.*\bswitch\b.*(?:\s-[cC]\b|\s--create\b)", line):
            return True
        m = re.search(r"\bgit\s+branch\s+(.+)", line)
        if m:
            rest = m.group(1).split()
            if rest and (rest[0] in BRANCH_CREATE_OPTS or not rest[0].startswith("-")):
                if not any(o in rest for o in BRANCH_MODIFY_OPTS | BRANCH_LIST_OPTS):
                    return True
    return False


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # can't parse -> don't interfere

    tool = payload.get("tool_name", "")
    if tool not in ("Bash", "PowerShell"):
        sys.exit(0)

    command = (payload.get("tool_input") or {}).get("command", "")
    if not command or not command.strip():
        sys.exit(0)

    try:
        import shlex
        tokens = shlex.split(command, posix=True, comments=False)
        blocked = creates_branch(tokens)
    except ValueError:
        blocked = regex_fallback(command)

    if blocked:
        deny()
    sys.exit(0)


if __name__ == "__main__":
    main()
