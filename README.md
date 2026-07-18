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
| `research` | Research a topic across in-repo docs, official docs, and communities |
| `meta-improvement` | Update a rule or skill based on a mistake or better approach found during work |
| `fewer-fetch-prompts` | Add approved domains to the WebFetch allowlist to reduce permission prompts |
| `create-prd` | Create a PRD for a project or feature |

### [plane-workflow](plugins/plane-workflow/)

Skills for [Plane](https://plane.so) project management.

**Prerequisite:** [Plane MCP server](plugins/plane-workflow/README.md#prerequisite-plane-mcp-server) configured.

| Skill | Description |
|---|---|
| `start-issue` | Fetch a Plane issue, set it In Progress, and produce an implementation plan |
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

## Maintainer: export checklist

Skills here are hand-copied from a personal canonical `~/.claude/skills` and edited down for a
public audience. Before exporting or re-syncing a skill, check for:

- [ ] Local absolute paths (`/Users/<name>/...`) — genericize or remove.
- [ ] Personal memory-file references (a specific cached-IDs filename, etc.) — describe the
      pattern generically ("a cached reference file, if you keep one") instead of naming it.
- [ ] Hardcoded project/issue-ID prefixes presented as universal (e.g. `LAB-`, `WQ1K-`) — fine as
      one illustrative example among others, not fine as the only case handled.
- [ ] References to skills or shared files that don't exist in this repo — `grep -rn
      "<skill-name>" plugins/` for anything you're about to remove, and grep the file you're
      exporting for its own cross-references before publishing it.
- [ ] OS-specific hard gates (e.g. `pbcopy`) without a documented fallback for other platforms.
- [ ] Personal infrastructure specifics (specific internal tool names, specific config file paths
      from one person's setup) presented as general guidance.
- [ ] Time-sensitive internal narration ("used to be mandatory, now it isn't") — state the current
      policy plainly instead of narrating its history.
- [ ] README skill-count tables (root and per-plugin) match the actual directory contents.

## Author

Built by [Victor Da Luz](https://vdaluz.com).
