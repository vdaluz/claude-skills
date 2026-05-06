---
name: read-surface
description: Read a cmux surface to observe terminal output, logs, or browser state without running separate commands. Use when checking what's already visible in another pane.
---

Observe what's on a cmux surface — terminal or browser — in the current or any workspace.

**Context:** The user almost always works inside cmux. You are running inside a cmux Claude surface (`$CMUX_SURFACE_ID`). Use this to observe other panes before running duplicate commands — e.g. check if a server is already running, read a log tail, or inspect what a browser is showing.

**Exception:** The review-alerts scheduled job runs outside cmux (LaunchAgent). Do not assume cmux is available in that context.

## 1. Discover surfaces

```bash
cmux tree --all
```

Returns a tree: windows → workspaces → panes → surfaces. Each surface shows:
- Type: `[terminal]` or `[browser]`
- Name/title: "Terminal", "bin/dev", "Claude", "VS Code", "Dashboard — …"
- `◀ here` = your current Claude surface — skip it
- URL for browser surfaces

Typical workspace layout:
| Pane | Surface(s) | What it contains |
|---|---|---|
| pane:1 (focused) | Claude `[terminal]` | You — skip |
| pane:2 | VS Code `[browser]` + code server `[terminal]` | Editor |
| pane:3 | Terminal `[terminal]` | User's general shell |
| pane:4 | bin/dev or named `[terminal]` | Dev server / logs |
| pane:N | Named `[browser]` | App UI |

## 2a. Read a terminal surface

```bash
cmux read-screen --surface surface:N --lines 50
```

Add `--scrollback` to include content scrolled off screen:

```bash
cmux read-screen --surface surface:N --scrollback --lines 100
```

When unsure which surface has what you're looking for, read candidates in parallel.

## 2b. Read a browser surface

```bash
# Accessibility/DOM snapshot — best for reading content and state
cmux browser snapshot --surface surface:N

# Just the current URL
cmux browser url --surface surface:N

# Visible text only
cmux browser get text --surface surface:N

# Screenshot
cmux browser screenshot --surface surface:N --json

# Wait for a condition before reading (e.g. after a navigation)
cmux browser wait --surface surface:N --load-state complete
cmux browser wait --surface surface:N --url-contains "/dashboard"
```

## When to use this instead of running a command

| Situation | Do this |
|---|---|
| Is a dev server already running? | `read-screen` the "bin/dev" surface |
| What do the recent logs show? | `read-screen` the relevant terminal |
| What is the browser showing right now? | `browser snapshot` the browser surface |
| Did a previous command succeed? | `read-screen` the terminal it ran in |
| Does the UI reflect a change I just made? | `browser snapshot` or `browser get text` |

Prefer reading existing surfaces over re-running commands — re-running can interfere with running processes or produce misleading output.
