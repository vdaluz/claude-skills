---
name: new-repo
description: Scaffold a new repo under ~/Repos with a CLAUDE.md, baseline .claude/settings.json, and registration in the root portfolio inventory (Repos/CLAUDE.md table + repo-audit-config.yml). Use when the user asks to create, init, scaffold, or set up a new repo/project under ~/Repos.
---

Scaffold a new repo so it starts with working Claude Code config instead of being invisible to the portfolio-level tooling (audit-rules, the root CLAUDE.md table) until someone notices the gap later.

Arguments: repo path (under `~/Repos/`), a one-line identity (what the project is + primary tech stack), and whether it has (or needs) a Plane project.

## Steps

1. **Confirm the repo exists** (or is about to). If it doesn't exist yet, ask whether to `git init` it or whether the user will clone/create it first — don't assume.

2. **Write `<repo>/CLAUDE.md`** from this template, filling in the identity and commands from what the user told you (or inferred from `package.json`/`Cargo.toml`/`go.mod`/etc. if the repo already has code):

   ```markdown
   # CLAUDE.md

   This file provides guidance to Claude Code when working in this repository.

   ## What this repo is

   <one or two sentences: what the project is, primary tech stack>

   ## Commands

   ```bash
   <primary dev commands: build/test/run/lint>
   ```

   ## Workflow

   <worktree/branch policy. Default to the global standing rule (direct-to-main,
   worktree isolation is opt-in) unless the user says this repo needs feature
   branches — state explicitly either way, don't leave it implicit.>

   ## Cross-project knowledge base

   See Knowledge Base in the global (`~/.claude/CLAUDE.md`) rules for the
   canonical KB location and search command.
   ```

   If the repo has a dedicated Plane project, add a line noting the project identifier (e.g. "Tracked in Plane under the FOO project").

3. **Write `<repo>/.claude/settings.json`** with a generic, low-risk baseline — read-only git and network diagnostics only. Don't copy homelab-v3's ansible/pvesh-specific entries; those are homelab-specific, not a generic baseline:

   ```json
   {
     "$schema": "https://json.schemastore.org/claude-code-settings.json",
     "permissions": {
       "allow": [
         "Bash(git status:*)",
         "Bash(git log:*)",
         "Bash(git diff:*)",
         "Bash(git show:*)",
         "Bash(git branch:*)",
         "Bash(dig:*)",
         "Bash(nslookup:*)",
         "Bash(ping:*)",
         "Bash(gh search:*)"
       ]
     }
   }
   ```

   Add repo-specific entries (build tool, test runner, etc.) on top of this baseline once you know what they are — don't leave the file generic if the repo's actual dev loop is already known.

   **Do not add a `deny` block or a `.gitignore` entry for `settings.local.json`.** The user-level deny set (`~/.claude/settings.json`) already applies to every repo, and `~/.config/git/ignore` already has a global `**/.claude/settings.local.json` pattern covering every repo — both would be pure duplication here. Verify this is still true (`git -C <repo> check-ignore -v .claude/settings.local.json` should print a match against `~/.config/git/ignore`) before skipping the step; if it ever stops being true, add the per-repo `.gitignore` line instead.

4. **Register in the root portfolio table** (`~/Repos/CLAUDE.md`): add a row to the `| Directory | Type | Status |` table with the repo's directory, a short type/stack description, and status (`Active` unless told otherwise). If it has a Plane project, note the identifier in the Status column (e.g. `Active — Plane: FOO`), matching the existing convention.

5. **Register in `~/Repos/repo-audit-config.yml`**: add an entry under `repos:` with `path`, `identifier` (the Plane project identifier, or `null` if none), and `description`.

6. **Report**: list every file created/edited, and flag anything you inferred rather than were told (identity, commands, Plane identifier) so the user can correct it.

## Exported copy

This skill is also exported to the `general-workflow` plugin in `~/Repos/claude-skills` (`plugins/general-workflow/skills/new-repo/`). If you edit this canonical copy, the export drifts until someone re-syncs it — see META-16's spike findings on marketplace/canonical drift before assuming the export is current.
