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

### Coming soon

- `general-workflow` — Reusable skills for planning, research, code review, and PRD writing (no external tools required).
- `plane-workflow` — Skills for [Plane](https://plane.so) project management (requires the Plane MCP server).

## Manual install (no marketplace)

Copy any skill directory into `~/.claude/skills/`:

```bash
cp -r plugins/cmux-tools/skills/read-surface ~/.claude/skills/
```

Then invoke as `/read-surface` (no namespace prefix).

## Contributing

PRs welcome. See [Anthropic's skill docs](https://docs.anthropic.com/en/docs/claude-code/skills) for the `SKILL.md` format.
