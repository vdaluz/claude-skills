# plane-workflow

Claude Code skills for [Plane](https://plane.so) project management — start issues, wrap them up, convert PRDs and spikes into issues, and resume work across sessions.

## Prerequisite: Plane MCP server

These skills use the Plane MCP server. Install and configure it before use:

```bash
# Install the Plane MCP server
claude mcp add plane -- npx -y mcp-server-plane

# Or with explicit workspace slug
claude mcp add plane -- npx -y mcp-server-plane --workspace-slug your-workspace-slug
```

You'll need a Plane API key. Get it from **Plane → Settings → API tokens**. Set it as an environment variable:

```bash
export PLANE_API_TOKEN=your_api_token
```

Or configure it in `~/.claude/settings.json` under `env`.

## Install

```
/plugin install plane-workflow@vdaluz-skills
```

After install, skills are available namespaced: `/plane-workflow:start-issue`, `/plane-workflow:continue-issue`, etc.

## Skills

| Skill | Description |
|---|---|
| `start-issue` | Fetch a Plane issue, set it In Progress, and produce an implementation plan |
| `continue-issue` | Resume work on an issue from a previous session by replaying Plane comments |
| `create-issue` | Create a new Plane issue in Backlog |
| `prd-to-issues` | Parse a PRD and create one Plane issue per spike and feature area |
| `spike-to-issues` | Convert a completed spike's findings into concrete implementation issues |

## Optional integrations

- **cmux**: `start-issue` optionally uses the [cmux](https://github.com/vdaluz/cmux) terminal multiplexer to inject the session rename command. Not required — the rename command is always printed to chat.
- **`pbcopy`** (macOS): the session rename step optionally copies the rename command to clipboard. Falls back gracefully on non-macOS systems.

## Manual install (without the marketplace)

Copy any skill directory into `~/.claude/skills/`:

```bash
cp -r plugins/plane-workflow/skills/start-issue ~/.claude/skills/
```

Then invoke as `/start-issue` (no namespace prefix).
