---
name: fewer-permission-prompts
description: Scan recent session transcripts for repeated read-only tool calls and propose an allowlist to reduce permission prompts.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/skills/fewer-permission-prompts/scripts/scan_tool_calls.py)
disable-model-invocation: true
---

# Fewer Permission Prompts

Look through the user's transcripts' MCP and bash tool calls, and based on those, make a prioritized list of patterns they should add to their permission allowlist to reduce permission prompts. Focus on read-only commands.

The format for permissions is: `Bash(foo*)`, `Bash(foo)`, `Bash(foo bar *)`, `mcp__slack__slack_read_thread`, etc.

Then, add these to the appropriate settings file (see Step 7).

## Steps

1. **Run the bundled scanner** to get raw tool-call frequencies across the user's recent transcripts (not just the current project):

   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/fewer-permission-prompts/scripts/scan_tool_calls.py
   ```

   It scans the 50 most-recently-modified `~/.claude/projects/**/*.jsonl` files, and prints `count  pattern` lines for every Bash command (as both a one-token form like `git` and a two-token form like `git status`) and every MCP tool name it saw in a `tool_use` block. This step is purely mechanical extraction - it does not judge which form is the meaningful pattern for a given command (some commands have real subcommands; for others the second token is just an argument, e.g. a filename), and it does not judge safety at all. That judgment is yours, in steps 2-3 below.

2. **Filter to read-only.** Keep only commands that don't mutate state. Examples of read-only: `ls`, `cat`, `pwd`, `git status`, `git log`, `git diff`, `git show`, `git branch`, `rg`, `grep`, `find`, `head`, `tail`, `wc`, `file`, `which`, `echo`, `date`, `gh pr view`, `gh pr list`, `gh pr diff`, `gh issue view`, `gh issue list`, `gh run list`, `gh run view`, `gh api` (GET), `bun run typecheck`, `bun run lint`, `bun run test` (for tests that don't mutate), `docker ps`, `docker logs`, `kubectl get`, `kubectl describe`, `ps`, `top`, `df`, `du`, `env`, `printenv`, any MCP tool with `read`/`get`/`list`/`search`/`view` in its name.

   Drop anything that writes, deletes, renames, pushes, merges, installs, or runs a build/test that has side effects. When in doubt, leave it out.

   **Never allowlist a pattern that grants arbitrary code execution.** A wildcard rule for any of these (e.g. `Bash(python3:*)`) is equivalent to allowing arbitrary code execution. This list is not exhaustive — apply the same rule to anything in the same category:
   - Interpreters: `python`/`python3`, `node`, `bun`, `deno`, `ruby`, `perl`, `php`, `lua`, etc.
   - Shells: `bash`, `sh`, `zsh`, `fish`, `eval`, `exec`, `ssh`, etc.
   - Package runners: `npx`, `bunx`, `uvx`, `uv run`, etc.
   - Task-runner wildcards: `npm run *`, `yarn run *`, `pnpm run *`, `bun run *`, `make *`, `just *`, `cargo run *`, `go run *`, etc. — an exact `Bash(bun run typecheck)` is fine, `Bash(bun run *)` is not
   - `gh api *`, `docker run`/`exec`, `kubectl exec`, `sudo`, and similar

3. **Drop commands Claude Code already auto-allows.** These don't need an allowlist entry — they never prompt. If you see any of these in the transcripts, skip them; don't suggest them to the user. Claude Code's own auto-allow list evolves across releases, so treat this as a starting point, not exhaustive — if you're unsure whether a command already never prompts, it's fine to just test it once rather than guess.

   - **Commonly auto-allowed (any args):** `cal`, `uptime`, `cat`, `head`, `tail`, `wc`, `stat`, `strings`, `hexdump`, `od`, `nl`, `id`, `uname`, `free`, `df`, `du`, `locale`, `groups`, `nproc`, `basename`, `dirname`, `realpath`, `cut`, `paste`, `tr`, `column`, `tac`, `rev`, `fold`, `expand`, `unexpand`, `fmt`, `comm`, `cmp`, `numfmt`, `readlink`, `diff`, `true`, `false`, `sleep`, `which`, `type`, `expr`, `seq`, `tsort`, `pr`, `echo`, `ls`, `cd`.
   - **Auto-allowed with zero args only:** `pwd`, `whoami`, `alias`.
   - **Auto-allowed exact forms:** `claude -h`, `claude --help`, `node -v`, `node --version`, `python --version`, `python3 --version`, `ip addr`.
   - **Auto-allowed with safe flags only:** `xargs`, `file`, `sed` (read-only expressions), `sort`, `man`, `help`, `netstat`, `ps`, `base64`, `grep`, `egrep`, `fgrep`, `sha256sum`, `sha1sum`, `md5sum`, `tree`, `date`, `hostname`, `lsof`, `pgrep`, `tput`, `ss`, `fd`, `fdfind`, `rg`, `jq`, `uniq`, `history`, `arch`, `ifconfig`, `find` (blocks `-delete`/`-exec`/`-execdir`/`-ok`/`-okdir`/`-fprint*`/`-fls`/`-files0-from`), `printf` (blocks any `-flag`), `test` (blocks `-v`/`-R`/`-a`/`-o`).
   - **All git read-only subcommands:** `git status`, `git log`, `git diff`, `git show`, `git blame`, `git branch`, `git tag`, `git remote`, `git ls-files`, `git ls-remote`, `git config --get`, `git rev-parse`, `git describe`, `git stash list`, `git reflog`, `git shortlog`, `git cat-file`, `git for-each-ref`, `git worktree list`, etc.
   - **All gh read-only subcommands:** `gh pr view`, `gh pr list`, `gh pr diff`, `gh pr checks`, `gh pr status`, `gh issue view`, `gh issue list`, `gh issue status`, `gh run view`, `gh run list`, `gh workflow list`, `gh workflow view`, `gh repo view`, `gh release view`, `gh release list`, `gh api` (GET), `gh auth status`, etc.
   - **Docker read-only subcommands:** `docker ps`, `docker images`, `docker logs`, `docker inspect`.

   The list above is a good-enough approximation of Claude Code's own built-in read-only allowlist; treat it as a starting point, not an exhaustive spec.

4. **Pick the pattern form.** Use the narrowest pattern that still covers the observed usage:
   - If the user runs many variants (`git log`, `git log --oneline`, `git log main..HEAD`): use `Bash(git log *)`. The space-before-`*` form and the `Bash(git log:*)` suffix form are documented as equivalent trailing wildcards — prefer the space form because it's what Claude Code's own permission dialog writes when you select "Yes, and don't ask again", and because `:*` is only recognized at the very end of a pattern while the space form also works mid-pattern.
   - If a single exact invocation is common: use `Bash(foo)` with no wildcard.
   - For MCP: use the full tool name verbatim (no wildcard needed; they're already specific).
   - Never widen a pattern to the point that it conflicts with the rules above (no arbitrary code execution, no mutation/side effects).

5. **Evaluate every candidate on safety, not occurrence count.** Do not skip a pattern just because it appeared fewer than 3 times. If it is read-only and safe, it will cause a prompt every future time it runs — that is sufficient reason to add it. Evaluate each candidate on:
   - Is it read-only? (see Step 2)
   - Is there a plausible reason it will be run again?
   - Is it already auto-allowed? (see Step 3)
   If all three check out, add it.

6. **Present the list to the user** as a markdown table with columns: rank, pattern, count, one-line description. Example:

   | # | Pattern | Count | Notes |
   |---|---------|-------|-------|
   | 1 | `Bash(git status *)` | 142 | repo status checks |
   | 2 | `Bash(gh pr view *)` | 87 | PR inspection |
   | 3 | `mcp__slack__slack_read_thread` | 54 | Slack thread reads |

7. **Write entries to the correct settings file.**

   **Default: `~/.claude/settings.json` (user-level).** Generic permissions — MCP tools, `ping`, `dig`, `gh pr view *`, and similar read-only commands — go here so they apply across all projects without duplication. Don't list `curl` or `make` as examples here without a narrow form attached: an unqualified `curl`/`make` example reads as endorsing a blanket wildcard, which step 2 above explicitly forbids for `make *` and step 2's mutation rule also covers unscoped `curl` (a POST/PUT/DELETE, or a write to disk via `-o`). A narrow, already-vetted form (e.g. `Bash(curl -sI *)`, `Bash(make validate)`) is fine to add here — the point is the pattern must be safety-vetted before landing in this generic-entries list, not that curl/make can never appear.

   **Exception: project-level `.claude/settings.json`** only when the pattern itself is tightly coupled to that specific project — i.e., the pattern literally contains a project-specific URL, hostname, or path. A pattern that fires identically in any project goes in the user-level file.

   Preserve existing keys and existing entries in `permissions.allow`; de-duplicate against what's already there; don't remove anything; don't reorder unrelated fields. Check `~/.claude/settings.json` first — many entries may already be covered globally, making a project-level duplicate unnecessary.

8. **Report back.** Tell the user what you added (count + a few examples), what was already in the allowlist, and what you skipped and why (e.g. "dropped `rm` and `git push` — not read-only; dropped `cat`/`ls`/`git status` — already auto-allowed, no rule needed").

Do not add anything to `permissions.deny` or `permissions.ask`. Do not touch any other settings field.
