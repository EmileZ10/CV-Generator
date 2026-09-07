# Preuve : le hook `block-branch-creation.py` refuse une création de branche

Extrait réel d'une session Claude Code de ce dépôt.

- **Session :** `7ca7bedb-1f79-4e2d-bc07-c0598d5936d2`
- **Date :** 2026-09-07, ~17:10 (heure locale)
- **Commit associé :** `c8acf7e` — `chore: block git branch creation via PreToolUse hook`

Dans cette session, l'utilisateur a demandé la création du hook, puis Claude l'a
vérifié en exécutant une vraie commande de création de branche.

## 1. La commande git tapée pour tester

```
git branch claude-hook-selftest 2>&1; echo "exit=$?"
```

## 2. Le message de refus renvoyé (verbatim, à la place de la sortie git)

```
Branch creation is blocked by the project PreToolUse hook in .claude/settings.json (.claude/hooks/block-branch-creation.py).

Creating a git branch (git checkout -b, git switch -c, git branch <name>) is only allowed when the user has explicitly asked for a new branch in this conversation.

Do NOT work around this: do not commit directly to main instead, and do not ask the user whether to create a branch. Continue the work on the current branch. If the task genuinely cannot proceed without a new branch, stop and explain to the user why a branch is needed and let them ask for it.
```

La commande `git branch claude-hook-selftest` n'a jamais été exécutée : le hook
`PreToolUse` l'a interceptée avant.

## 3. La décision brute émise par le hook

Simulation de l'invocation exacte du hook, dans la même session, sur
`git switch -c wip` :

```json
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Branch creation is blocked by the project PreToolUse hook in .claude/settings.json (.claude/hooks/block-branch-creation.py).\n\nCreating a git branch (git checkout -b, git switch -c, git ..."}}
```

Le champ décisif est `"permissionDecision": "deny"`, avec la raison ci-dessus dans
`"permissionDecisionReason"`. À l'inverse, une commande autorisée
(`git branch --show-current`) produit une sortie vide et `exit=0` (= autorisée).

## 4. Confirmation qu'aucune branche n'a été créée

Juste après le refus, dans la même session :

```
git branch; echo "---"; git status --short --branch | head -1
```

Résultat :

```
* main
---
## main...origin/main [ahead 2]
```

Une seule branche, `main`. Pas de `claude-hook-selftest`.

## Bilan annoncé par Claude (verbatim)

> C'est en place et vérifié (le hook a bloqué un `git branch` de test réel,
> aucune branche créée, `47 passed`). Commit `c8acf7e`.
