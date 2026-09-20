# Code review - evidence and criteria

## Evidence to gather (step 4)

Run only what the project already has (declared in its manifest, lockfile, config, or CI). Redirect output to `code/<name>` files. Read-only invocations only - no `--fix`, no `--write`, no installs, no network publishes.

| Evidence | Typical sources (use the project's own script if one exists) |
|---|---|
| Type check | `tsc --noEmit`, `astro check`, `cargo check`, `swift build`, Sorbet/Steep |
| Lint | the project's lint script; `cargo clippy`; `rubocop`; `swiftlint` |
| Dependency audit | `npm audit --json` / `pnpm audit --json`, `cargo audit`, `bundle audit`, `pip-audit` |
| Outdated | `npm outdated --json`, `cargo outdated`, `bundle outdated` |
| Secrets | `gitleaks detect --no-banner` if installed |
| Static analysis | `semgrep --config auto --json` if installed |
| Tests + coverage | the project's test script with its coverage flag, if it runs in a few minutes |
| Build + size | production build output; bundle analyzer or `dist/` sizes per asset |
| Structure | file/line counts per dir; the 20 largest source files; the 20 most-changed files (`git log --since=6.months --name-only --format= \| sort \| uniq -c \| sort -rn`) |
| Hygiene | count and locations of TODO/FIXME/HACK, skipped tests, lint-ignore comments |

Churn x size is the cheapest maintainability signal there is: a large file that changes every week is where judges should read closely. Put that list in `context.md`.

## Dimensions (one judge each)

Skip a dimension in `plan.md` when there is nothing to judge (e.g. no server, no auth -> security reduces to dependencies and secrets).

### security
Spend effort where models do well - **authorization and business logic** - and leave taint-style bugs (injection, XSS sinks) to static-analysis output, which you triage rather than re-derive. Walk: entry points (routes, handlers, IPC commands, webhooks, deep links) -> authn -> authz on every object access (can user A reach user B's record by id?) -> data flow of anything secret or user-supplied -> crypto and token handling -> config and deploy (CORS, CSP, cookie flags, debug flags, exposed env). For desktop/mobile shells: IPC/command allowlists, file-system and shell scopes, URL-scheme handlers, local storage of credentials.
Do not report without a demonstrated path: denial of service, missing rate limiting, generic "validate input", resource exhaustion, open redirects with no impact, dependency CVEs in code paths the project does not reach.

### performance
Evidence-led only: build output sizes, render-blocking or oversized assets, N+1 query shapes visible in code (loop containing a query/fetch), unbounded list rendering or queries without limits, missing indexes on columns used in `where`/`order` on large tables, synchronous work on a UI/main thread, cache headers on static assets. For web, lab targets: LCP <= 2.5 s, CLS <= 0.1, TBT as the lab proxy for INP. No finding without a measurement or a specific code path.

### architecture
Module boundaries and dependency direction (does UI reach into persistence? do cycles exist?), duplicated sources of truth for the same state, leaky abstractions that force edits in many places for one change (confirm with churn data), error-handling strategy consistency, config and secrets flow, and whether the structure fits what `context.md` says is planned next. Report structural problems that have a present cost. Do not report "could be more modular" or a preferred pattern.

### maintainability
Hotspots (large x high-churn files), functions doing several jobs, dead code and unused exports/deps, copy-paste clusters, comments or docs that contradict the code, inconsistent conventions *within* the project (not versus your preferences), lint-ignore and skipped-test accumulation.

### testing
What is actually protected: are the critical paths named in `context.md` covered by any test? Tests that assert nothing or only mock themselves, skipped or flaky tests, no test for a past bug fix visible in git history, missing CI enforcement. Coverage percentage alone is not a finding.

### dependencies
Reachable vulnerabilities (triaged from the audit file, clustered by upgrade path), abandoned or deprecated packages on a critical path, major versions behind on the framework/runtime with a known end-of-support date, duplicate libraries for one job, lockfile or engine mismatches with CI.
