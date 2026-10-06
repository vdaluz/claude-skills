# general-workflow

Reusable Claude Code skills for planning, research, code review, and PRD writing. Core skills need no external tools - see Optional integrations below for the three that do.

## Install

```
/plugin install general-workflow@vdaluz-skills
```

After install, skills are available namespaced: `/general-workflow:roast`, `/general-workflow:research`, etc.

## Skills

| Skill | Description |
|---|---|
| `roast` | Critically review a plan, code, or diff, blunt, prioritized by severity |
| `research` | Research a topic across in-repo docs, official docs, and communities |
| `meta-improvement` | Update a rule or skill based on a mistake or better approach found during work |
| `fewer-fetch-prompts` | Add approved domains to the WebFetch allowlist to reduce permission prompts |
| `fewer-permission-prompts` | Scan transcripts for repeated read-only commands and propose an allowlist |
| `create-prd` | Create a PRD for a project or feature (outputs to Plane page or markdown file) |
| `browser-verify` | Drive a real browser via Playwright MCP to verify a UI change before calling it done |
| `stale-repos` | Scan git repos under a root for stale branches/worktrees and offer safe cleanup |
| `project-review` | Whole-project code and/or design review ending in a capped, evidence-backed list of proposed issues |

### Optional integrations

- `create-prd` and `research` post to Plane if the fork-specific Plane MCP server is configured (see [plane-workflow's prerequisite](../plane-workflow/README.md#prerequisite-plane-mcp-server) - [vdaluz/plane-mcp-server](https://github.com/vdaluz/plane-mcp-server), not the official server), falling back to chat output otherwise.
- `browser-verify` requires the [Playwright MCP server](https://github.com/microsoft/playwright-mcp) configured; it doesn't work without it.
- `project-review` spawns two plugin agents, `review-judge` and `review-refuter` (in this plugin's `agents/`), which are pinned to `model: fable` so the judging runs on the strongest model regardless of the session's main model. They are only ever invoked by that skill. No Fable access: change `model:` in those two files to `opus` or `inherit`. Its `design` mode needs the [Playwright MCP server](https://github.com/microsoft/playwright-mcp); its `code` mode uses only tools the reviewed project already has. It writes evidence to a `.review/` directory and adds that to the project's `.gitignore` if it isn't ignored already. Manual install: also copy `agents/review-*.md` into `~/.claude/agents/`.
- `stale-repos` is workstation-local (reads your local filesystem), so it can't run as a cloud/scheduled routine.

## Manual install (without the marketplace)

Copy any skill directory into `~/.claude/skills/`:

```bash
cp -r plugins/general-workflow/skills/roast ~/.claude/skills/
```

Then invoke as `/roast` (no namespace prefix). `fewer-fetch-prompts`, `stale-repos`, and `fewer-permission-prompts` bundle their own scripts and invoke them via the `${CLAUDE_SKILL_DIR}` prefix, which resolves correctly for a manual copy too - no marketplace-only exception needed.
