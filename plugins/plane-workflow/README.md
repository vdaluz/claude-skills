# plane-workflow

Claude Code skills for [Plane](https://plane.so) project management — start issues, convert PRDs and spikes into issues, and resume work across sessions.

## Prerequisite: Plane MCP server

These skills call flat, per-operation tools (`list_work_items`, `create_work_item`, and so on). That shape comes from [vdaluz/plane-mcp-server](https://github.com/vdaluz/plane-mcp-server), a fork of the official server - not the official [makeplane/plane-mcp-server](https://github.com/makeplane/plane-mcp-server), which as of 0.3 consolidates every work-item operation behind a single `workitem` tool with an `action` argument. The two aren't interchangeable: these skills won't work against the official server. Install the fork instead ([`uv`](https://docs.astral.sh/uv/) required):

```bash
# Install the Plane MCP server (fork with the flat tool surface these skills need)
claude mcp add plane -- uvx --from git+https://github.com/vdaluz/plane-mcp-server@v0.2.11 plane-mcp-server stdio
```

You'll need a Plane API key and your workspace slug. Get the key from **Plane → Settings → API tokens**. Set them as environment variables:

```bash
export PLANE_API_KEY=your_api_key
export PLANE_WORKSPACE_SLUG=your-workspace-slug
```

Or configure them in `~/.claude/settings.json` under `env`. For a self-hosted Plane instance, also set `PLANE_BASE_URL` (defaults to `https://api.plane.so`). [developers.plane.so/dev-tools/mcp-server](https://developers.plane.so/dev-tools/mcp-server) documents the official server's consolidated tools, not this fork's flat ones - useful for API concepts, not for matching tool names.

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
| `whats-next` | Show what's next for a Plane project across In Progress/Todo/Backlog/Blocked |
| `pick-next-issue` | Recommend 3 ranked next-issue candidates instead of a raw list |
| `reprioritize-backlog` | Reorder a Backlog by dependency + urgency, applied only after explicit approval |

## Optional integrations

- **A browser-verification skill** (e.g. general-workflow's `browser-verify`): if you have one installed, `start-issue` points to it for exercising UI changes before marking them done. Not required - the UI-verification step works without it, just less thoroughly.

## Manual install (without the marketplace)

Copy the skill directory *and* `skills/_shared` into `~/.claude/skills/` - most skills here reference files in `_shared/`, and the `${CLAUDE_PLUGIN_ROOT}` prefix those references use only resolves inside a marketplace install. In a manual copy, `_shared/` needs to land at `~/.claude/skills/_shared/` instead:

```bash
cp -r plugins/plane-workflow/skills/start-issue ~/.claude/skills/
cp -r plugins/plane-workflow/skills/_shared ~/.claude/skills/
```

Then invoke as `/start-issue` (no namespace prefix).
