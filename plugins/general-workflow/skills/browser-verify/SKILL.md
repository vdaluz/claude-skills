---
name: browser-verify
description: Interactively drive a real browser (via the Playwright MCP server, configured to use your actual installed browser) to verify a UI/frontend change works, per the "use the feature in a browser before reporting complete" rule. Use for any repo that ships a web UI reachable via a local dev server, after making a UI or frontend change, before marking that work done. Not framework-specific — the mechanism is generic (navigate to a dev-server URL, drive it, screenshot it).
---

Verify a UI/frontend change by actually driving it in a browser, not just building/linting it.

Arguments: what changed (1 sentence), the page(s)/flow it affects.

## Prerequisite

This skill depends on the `playwright` MCP server. For it to launch your real installed browser (recommended, so what you see matches what a user sees, rather than Playwright's bundled Chromium): `npx @playwright/mcp@latest --browser chrome` (or your browser of choice), configured user-level in your Claude Code MCP config. If the `browser_*` MCP tools aren't available, the server didn't load — check `claude mcp list` and confirm the target browser is installed.

## Steps

1. **Start the dev server** for the repo being changed:
   - Check the repo's own CLAUDE.md, `package.json` scripts, or `bin/` directory for the dev entrypoint.
   - **If the project deploys via Cloudflare Workers and its `wrangler.toml`/`wrangler.jsonc` sets `run_worker_first`**: a plain framework dev server often cannot correctly serve static assets under that flag — it doesn't emulate Cloudflare's worker-then-asset routing. Use the project's build+`wrangler dev` path instead (a dedicated `dev:full`-style script if the project has one, or `npm run build && npx wrangler dev --config dist/server/wrangler.json` as a fallback).
   - If no such flag is present, the plain framework dev command (`npm run dev`, `bin/dev`, etc.) usually works normally.

2. **Navigate** to the affected page with the `browser_navigate` tool.

3. **Inspect** with `browser_snapshot` (accessibility-tree snapshot — fast, text-only, prefer this over a screenshot for confirming structure/content/state).

4. **Exercise the actual change**: click, type, or otherwise interact with whatever changed (`browser_click`, `browser_type`, etc.) — don't just load the page and stop. Test the golden path and at least one edge case (empty state, error state, dark mode toggle, etc. — whatever applies).

5. **Screenshot** (`browser_take_screenshot`) when the change is visual (layout, styling, color) — a snapshot alone won't catch a visual regression.

6. **Check console errors**: the MCP server surfaces console messages — look for anything unexpected before declaring success.

7. **Report evidence**: include what you navigated to, what you interacted with, and the snapshot/screenshot result. Never claim a UI change "works" from a successful build alone.

8. **Close the browser** (`browser_close`) once verification is done. Do this on the error/early-exit path too — if you abandon this skill partway through because something failed, close the browser before reporting the failure, don't leave it open.

## Known limitation

Some Playwright MCP setups launch the browser detached, in its own process group, by design — an abnormal session end (terminal force-quit, crash, `kill -9`) can still leave an orphaned browser instance behind even when `browser_close` was called correctly on every prior run. Calling `browser_close` still matters: it closes the browser promptly within a still-open session instead of leaving it resident for the rest of a long-lived session.

**If orphaned browser instances accumulate** (visible in your Dock/taskbar, not opened by you): check whether the MCP server uses a distinct user-data-dir/profile from your normal browser profile — if so, those orphaned instances can be safely killed by matching on that profile path without touching normal browsing windows, e.g.:
```bash
pkill -f "user-data-dir=<your-playwright-mcp-cache-path>"
```

## Out of scope

- **Native app shells (e.g. Tauri, Electron)**: these open a native webview window, not a normal browser tab — Playwright MCP generally can't attach to it via a `--browser` flag pointed at a real browser. Use the project's own in-process browser-mode test runner (if it has one) for that case instead.
- **Automated CI test suites**: this skill is for interactive, in-session verification. It doesn't replace or duplicate accessibility linting or content-check test suites already running in CI.
- **Automated real-browser checks that need to run unattended (CI, pre-commit)**: not this skill's job — it requires an interactive session. If a project needs an automated rendering check, a headless real-browser test runner (e.g. Vitest browser mode with a Playwright provider) is the better fit for that unattended case.
