# plane-workflow

Claude Code skills for [Plane](https://plane.so) project management — start issues, convert PRDs and spikes into issues, and resume work across sessions.

## Prerequisite: Plane MCP server

These skills use the [official Plane MCP server](https://github.com/makeplane/plane-mcp-server). Install and configure it before use ([`uv`](https://docs.astral.sh/uv/) required):

```bash
# Install the Plane MCP server
claude mcp add plane -- uvx plane-mcp-server stdio
```

You'll need a Plane API key and your workspace slug. Get the key from **Plane → Settings → API tokens**. Set them as environment variables:

```bash
export PLANE_API_KEY=your_api_key
export PLANE_WORKSPACE_SLUG=your-workspace-slug
```

Or configure them in `~/.claude/settings.json` under `env`. For a self-hosted Plane instance, also set `PLANE_BASE_URL` (defaults to `https://api.plane.so`). Full reference: [developers.plane.so/dev-tools/mcp-server](https://developers.plane.so/dev-tools/mcp-server).

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
