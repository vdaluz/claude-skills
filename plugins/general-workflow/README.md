# general-workflow

Reusable Claude Code skills for planning, research, code review, and PRD writing. No external tools required — these work in any project.

## Install

```
/plugin install general-workflow@vdaluz-skills
```

After install, skills are available namespaced: `/general-workflow:roast`, `/general-workflow:research`, etc.

## Skills

| Skill | Description |
|---|---|
| `roast` | Critically review a plan, code, or diff — blunt, prioritized by severity |
| `research` | Research a topic across in-repo docs, official docs, and communities |
| `meta-improvement` | Update a rule or skill based on a mistake or better approach found during work |
| `fewer-fetch-prompts` | Add approved domains to the WebFetch allowlist to reduce permission prompts |
| `create-prd` | Create a PRD for a project or feature (outputs to Plane page or markdown file) |

### Optional integrations

- `create-prd` and `research` post to Plane if the [Plane MCP server](https://github.com/makeplane/plane-mcp-server) is configured — falls back to chat output otherwise.

## Manual install (without the marketplace)

Copy any skill directory into `~/.claude/skills/`:

```bash
cp -r plugins/general-workflow/skills/roast ~/.claude/skills/
```

Then invoke as `/roast` (no namespace prefix).
