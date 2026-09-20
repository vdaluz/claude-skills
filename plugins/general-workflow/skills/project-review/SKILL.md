---
name: project-review
description: Run a whole-project review - code, design, or both - that ends in a capped, evidence-backed list of proposed tracker issues for the user to approve. Gathers deterministic evidence into a gitignored .review/ directory, then has fresh-context judge subagents assess it. Manual only - this is an expensive multi-agent run.
argument-hint: "[code|design|both] [focus-or-scope] [--gather-only]"
disable-model-invocation: true
effort: high
---

Review a whole project (not a diff) and produce a short list of proposed issues worth filing.

Arguments: mode - `code`, `design`, or `both` (default `code`); optional focus or scope (a directory, a flow, "auth only"); `--gather-only` stops after step 4 so another session can judge the `.review/` directory.

**Your role is collector and coordinator, not reviewer.** You gather neutral evidence and hand it to judges that have never seen your reasoning. Do not write your own opinions of the project into any file the judges read - a reviewer who is shown someone else's framing anchors on it.

This skill never edits project source. The only tracked file it may touch is `.gitignore` (step 1). It never files issues - step 9 hands off to the user and a tracker skill.

## Steps

**1. Run directory and gitignore (before writing anything).**

- Run dir: `.review/<YYYY-MM-DD>-<mode>/` at the repo root. Layout is in `${CLAUDE_SKILL_DIR}/references/finding-schema.md`
- In a git repo, run `git check-ignore -q .review`. If it is not ignored, append `.review/` to the repo's `.gitignore` and tell the user you did. Evidence can contain screenshots of local data and tool output with paths and tokens - it must never be committed.

**2. Orient - cheap, read-only.** Write `context.md` containing facts only:

- Stack, entry points, size (file and line counts per top-level dir), how it is built, tested, run, and deployed - from CLAUDE.md, README, manifests, CI config.
- Documented conventions and deliberate decisions (so judges do not report them).
- `REVIEW.md` at the repo root, if present: its do-not-report list and severity definitions apply as written. A `## project-review` section may give the dev-server command, routes/flows to cover, and auth/seed steps.
- Do-not-report list: REVIEW.md entries + `.review/rejected.md` (findings declined in earlier runs) + titles of open tracker issues, if an issue tracker is reachable + anything CI already enforces.
- For `design`/`both`: the list of routes, key flows, and UI states that exist.

**3. Evidence plan, then the advisor.** Read the reference for the mode: `${CLAUDE_SKILL_DIR}/references/code.md` and/or `${CLAUDE_SKILL_DIR}/references/design.md` - then draft `plan.md`: which tools you will run (only ones already installed or declared by the project), which routes x viewports x themes x states you will capture, which dimensions will be judged, and what you are skipping and why. If an advisor tool is available, **consult the advisor now**, before gathering, and apply its corrections to `plan.md`. No advisor: continue. If the plan needs something only the user can provide (credentials, seed data, a device, a tool install), ask once, now.

**4. Gather evidence - deterministic first.** Follow the mode reference. Write raw tool output to files in the run dir; keep it out of your own context (redirect to file, then read only summaries/counts). Never install a tool, never pass `--fix`, never run anything that mutates the project or a remote. A tool that is absent or fails is recorded in `plan.md` as "not available" - not worked around. Stop any dev server and close any browser you started, on the failure path too.

With `--gather-only`: stop here and report the run dir path and what was captured.

**5. Judge - one fresh-context subagent per dimension, in parallel.** Use the `general-workflow:review-judge` agent (it pins its own model; do not override it). Give each one only: its dimension, the criteria file path and section, the finding-schema path, the run dir path, the repo root, and the do-not-report list. Do **not** include your impressions, suspicions, or a summary of what you saw. Save each reply verbatim to `judged/<dimension>.md`.

If that agent type is unavailable (manual install without the plugin's `agents/`), use a general-purpose subagent with the contents of the agent file as its instructions and the strongest model available to you, and say so in the final report.

**6. Verify.** Concatenate all candidates into `judged/candidates.md` with stable ids (`C1`.. for code, `D1`.. for design). Send them to `general-workflow:review-refuter` in batches of at most 10. Then:

- Drop `refuted`. Drop anything whose post-verification confidence is under 80. Merge `duplicate-of`. Apply downgrades.
- Rank by severity, then confidence. **Cap: 15 findings per mode.** Collapse minor findings to at most 5, reporting the rest as "plus N similar" inside the closest finding.
- Do not pad to reach the cap. Three real findings is a better result than fifteen.

**7. Write `findings.md`** in the schema format, plus a short header: mode, date, what was and was not covered (from `plan.md`), per-dimension health lines, and counts (candidates -> confirmed -> reported).

**8. Advisor, second checkpoint.** If an advisor tool is available, print the final list (ids, titles, severities, one-line evidence) and consult the advisor: is any severity inflated, is any finding really two, is a whole area of `plan.md` unaccounted for? Apply corrections to `findings.md`. Make the file durable before this call, not after.

**9. Present and stop.** In chat: the coverage header, then a numbered list - id, severity, title, one-line evidence, effort. Then the path to `findings.md`. Ask which findings the user wants filed. Do not file anything. If the plane-workflow plugin is installed, `review-to-issues` takes `findings.md` and the user's selection; otherwise any tracker skill or the user can file from the file.

## Rules

- Never claim coverage you did not gather evidence for. "Performance: not assessed - no build output or Lighthouse available" is a correct report line.
- Design review from screenshots is a consistency and measurable-accessibility pass, not a usability study. Say so in the header. Issues that only appear across a multi-step flow need the flow captured step by step, or they are out of scope.
- Native app shells (Tauri/Electron webviews, iOS/macOS apps) cannot be driven through a browser MCP. Use the project's own UI driver or test runner if it has one, or screenshots the user supplies; otherwise mark design evidence "not available" for that surface.
- Identical inputs can produce different findings between runs. The refuter pass and the cap exist to keep the output stable; do not loosen them to "find more".
