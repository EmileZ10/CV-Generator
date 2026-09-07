# Preuve : le skill `auto-commit-when-done` se déclenche sans qu'on le demande

Extrait réel d'une session Claude Code de ce dépôt.

- **Session :** `2eb776da-d6c9-4624-b99f-127aca9023a7`
  (`https://claude.ai/code/session_01W6V8F2pWrENbH9DLzG87En`)
- **Date :** 2026-09-07, ~15:22 (heure locale)
- **Commit produit :** `1614932` — `docs: add private-editor comment to form template`

## La tâche demandée par l'utilisateur

Le message ne demande qu'une édition et un passage des tests. **À aucun moment
l'utilisateur ne demande de committer.**

> Ajoute ce commentaire HTML tout en haut de templates/form.html, juste après la
> balise `<html>` : `<!-- User's private editor -->`. Vérifie que les tests
> passent toujours

## Ce que Claude a fait, dans l'ordre

1. `Read templates/form.html` (15 premières lignes).
2. `Edit` — insertion de la ligne :

   ```diff
   diff --git a/templates/form.html b/templates/form.html
   index 5f35a8c..83ccdb9 100644
   --- a/templates/form.html
   +++ b/templates/form.html
   @@ -1,5 +1,6 @@
    <!DOCTYPE html>
    <html lang="fr">
   +<!-- User's private editor -->
    <head>
      <meta charset="UTF-8"/>
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
   ```

3. `Bash` — exécution de la suite de tests :

   ```
   47 passed, 3 warnings in 16.62s
   ```

4. **`Skill(auto-commit-when-done)` — chargé de lui-même par Claude**, sans
   demande de l'utilisateur. Trace de l'appel d'outil dans le transcript :

   ```
   --- TOOL_USE: Skill ---
   {"skill": "auto-commit-when-done"}
   --- TOOL_RESULT ---
   Launching skill: auto-commit-when-done
   ```

5. `Bash` — `git diff --stat` (le skill constate que `main.py` et
   `portfolio.html` avaient déjà des modifications non liées) puis
   `git diff -- templates/form.html`.

6. `Bash` — commit du seul fichier concerné :

   ```
   git add templates/form.html && git commit -m "$(cat <<'EOF'
   docs: add private-editor comment to form template

   Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
   Claude-Session: https://claude.ai/code/session_01W6V8F2pWrENbH9DLzG87En
   EOF
   )" && git rev-parse --short HEAD
   ```

   Résultat :

   ```
   [main 1614932] docs: add private-editor comment to form template
    1 file changed, 1 insertion(+)
   1614932
   ```

## Bilan annoncé par Claude en fin de session (verbatim)

> C'est fait.
>
> - Ajouté `<!-- User's private editor -->` juste après `<html lang="fr">` dans `templates/form.html:3`.
> - Tests : `47 passed` (aucune régression).
> - Commit `1614932` sur `main` (seul `form.html` a été mis en scène ; les modifications préexistantes dans `main.py` et `portfolio.html` ont été laissées telles quelles).

Le commit `1614932` est bien présent dans l'historique `git log` de `main`.
