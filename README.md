# claude-skills

A [Claude Code plugin marketplace](https://docs.anthropic.com/en/docs/claude-code/plugins) with shareable skills for Claude Code.

## Install

Add the marketplace, then install any plugin:

```
/plugin marketplace add vdaluz/claude-skills
/plugin install cmux-tools@vdaluz-skills
```

Skills are namespaced by plugin (e.g. `/cmux-tools:read-surface`).

## Plugins

### [cmux-tools](plugins/cmux-tools/)

Skills for [cmux](https://github.com/vdaluz/cmux) terminal multiplexer users.

**Prerequisite:** cmux installed and running; Claude launched inside a cmux session.

| Skill | Description |
|---|---|
| `read-surface` | Read a terminal pane or browser tab without running a separate command |

### [general-workflow](plugins/general-workflow/)

Reusable skills for planning, research, code review, and PRD writing. No external tools required.

| Skill | Description |
|---|---|
| `roast` | Critically review a plan, code, or diff — blunt, prioritized by severity |
| `plan-only` | Produce a concrete implementation plan without making any changes |
| `research` | Research a topic across in-repo docs, official docs, and communities |
| `audit-rules` | Audit CLAUDE.md files and skills across repos for redundancy and conflicts |
| `meta-improvement` | Update a rule or skill based on a mistake or better approach found during work |
| `summarize-active-rules` | Summarize which rules and skills are active in the current context |
| `fewer-fetch-prompts` | Add approved domains to the WebFetch allowlist to reduce permission prompts |
| `create-prd` | Create a PRD for a project or feature |
| `new-repo` | Scaffold a new repo with CLAUDE.md, baseline settings.json, and portfolio registration |

### [plane-workflow](plugins/plane-workflow/)

Skills for [Plane](https://plane.so) project management.

**Prerequisite:** [Plane MCP server](plugins/plane-workflow/README.md#prerequisite-plane-mcp-server) configured.

| Skill | Description |
|---|---|
| `start-issue` | Fetch a Plane issue, set it In Progress, and produce an implementation plan |
| `wrap-up-issue` | Commit, close the worktree, and mark a Plane issue Done |
| `continue-issue` | Resume work on an issue from a previous session by replaying Plane comments |
| `create-issue` | Create a new Plane issue in Backlog |
| `prd-to-issues` | Parse a PRD and create one Plane issue per spike and feature area |
| `spike-to-issues` | Convert a completed spike's findings into concrete implementation issues |

## Manual install (no marketplace)

Copy any skill directory into `~/.claude/skills/`:

```bash
cp -r plugins/cmux-tools/skills/read-surface ~/.claude/skills/
```

Then invoke as `/read-surface` (no namespace prefix).

## Contributing

PRs welcome. See [Anthropic's skill docs](https://docs.anthropic.com/en/docs/claude-code/skills) for the `SKILL.md` format.

## Author

Built by [Victor Da Luz](https://vdaluz.com).
