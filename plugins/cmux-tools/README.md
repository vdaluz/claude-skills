# cmux-tools

Skills for [cmux](https://github.com/vdaluz/cmux) terminal multiplexer users.

## Prerequisite

[cmux](https://github.com/vdaluz/cmux) must be installed and running. Claude Code must be launched inside a cmux session (the `$CMUX_SURFACE_ID` environment variable must be set).

## Install

```
/plugin install cmux-tools@vdaluz-skills
```

After install, skills are available namespaced: `/cmux-tools:read-surface`.

## Skills

### `read-surface`

Reads what's visible on a cmux surface (terminal pane or browser tab) without running a separate command. Use it to check if a server is already running, read recent log output, or inspect what the browser is showing — before running commands that might interfere with running processes.

```
/cmux-tools:read-surface
```

## Manual install (without the marketplace)

Copy the skill directory into your user-level skills folder:

```bash
cp -r plugins/cmux-tools/skills/read-surface ~/.claude/skills/
```

Then invoke as `/read-surface` (no namespace prefix).
