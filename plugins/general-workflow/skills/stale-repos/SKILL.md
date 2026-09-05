---
name: stale-repos
description: Scan the git repos in a root directory's immediate subdirectories for stale branches/worktrees, report by verdict, offer safe opt-in cleanup.
argument-hint: "[--fetch] [--age-days N] [--root PATH] [--prune]"
effort: low
disable-model-invocation: true
---

Scan the git repos in a root directory's immediate subdirectories (default `~/Repos`) for stale branches and worktrees, report them grouped by verdict, and offer safe opt-in cleanup. Nested repos (a repo inside a repo) are not walked into — only direct children of the root.

Arguments (optional): `--fetch` (refresh remotes first), `--age-days N` (default 60), `--root PATH`, or specific repo paths — all passed through to `scan.py`. `--prune` (enable cleanup) is a **skill-level** switch only: it decides whether you do Step 3 below, and is never passed to `scan.py` (which has no such flag).

This skill is **workstation-local** — it reads the local filesystem, so it cannot run as a cloud/scheduled routine.

## Core principle

A deterministic Python scanner (`scan.py`, bundled in this skill dir) does all detection and emits JSON. You (Claude) do grouping, judgment, and — only behind explicit confirmation — the destructive cleanup. The scanner never mutates anything (except the optional `--fetch`); every delete is a separate prompted git command you run after the user approves.

**Never use `cd <dir> && git`** — always `git -C <repo> …` (the compound form can trigger extra permission prompts). The scanner already follows this.

## Step 1 — Scan (always read-only)

Run the bundled scanner. Default is JSON; use `--text` for a quick human view.

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/stale-repos/scan.py
```

Flags to pass through from the user's request:
- `--fetch` — `git fetch --prune` each repo first. OFF by default (network + slow across many repos). Turn on when the user wants accurate gone/behind state or hasn't fetched recently.
- `--age-days N` — age threshold for the report-only `review-old` signal (default 60). Age never triggers a prune on its own.
- `--root PATH` / trailing `PATH …` — scan somewhere other than `~/Repos`, or specific repos.

## Step 2 — Present the report

Parse the JSON and group by repo, then by verdict. Lead with the prune candidates, then the review items, and state what's protected so the user trusts the scan. Verdicts:

| Verdict | Meaning | Action |
|---|---|---|
| `prune-merged` | branch/worktree merged into default, no local commits ahead | **safe to clean** |
| `prune-gone` | upstream deleted, confirmed no local commits ahead (squash-merge + remote delete) | **safe to clean** |
| `review-gone-ahead` | upstream gone AND commits ahead — usually a squash-merged branch (looks "ahead" but is merged); occasionally real unmerged work | **You (Claude) do the verification, but never run `-D` without asking first.** Check whether the work is already on `<default>`: a squash/merge commit referencing the branch's issue/PR in `git -C <repo> log <default>`, AND/OR the branch's changed files/content present in the `<default>` tree (`git -C <repo> grep`, `ls-tree`, `show <default>:<file>`). Then present that evidence to the user and get explicit per-item confirmation before deleting with `-D` — this is the one verdict whose deletion can destroy real unmerged work, so it never skips the confirmation step even when your own verification looks conclusive. |
| `review-gone-unknown` | upstream gone but ahead/behind can't be determined (no resolvable default branch or remote for this repo) | review — same treatment as `review-gone-ahead`: never auto-prune, confirm with the user before any delete |
| `review-behind` | behind default, not confirmed merged | review — may be unmerged stale work |
| `review-detached` | detached-HEAD worktree | review, never auto-clean |
| `review-old` | older than `--age-days`, nothing else | report only |
| `active` | commits ahead, not merged | **protect** — live work |
| `protected-default` / `protected-current` / `protected-primary` | the default branch, the current branch, or a primary checkout | **protect** |
| `blocked-dirty` / `blocked-locked` | worktree has uncommitted changes or is locked | **never clean** |
| `prunable` | worktree's administrative entry still exists but its directory is gone from disk | admin tidy only — `git worktree prune` (never `worktree remove`, the path doesn't exist) |
| `in-worktree` | branch is checked out in a worktree | clean the worktree first, then the branch |
| `bare` / `keep` | bare repo / nothing notable | skip |

If `--prune` was not requested, stop here — report only, and tell the user they can re-run with `--prune` to clean up.

## Step 3 — Cleanup (only when `--prune` given)

**Reviewed-batch model, not per-item-from-scratch.** Present the full prune plan in one list, let the user exclude anything, then execute. Order matters:

1. **Worktrees first.** A branch checked out in a worktree can't be deleted until the worktree is gone. For each `prune-*` worktree the user kept in the plan:
   ```
   git -C <repo> worktree remove <path>
   ```
   (add `--force` only if the user explicitly accepts it; never force a `blocked-dirty`/`blocked-locked` one.)
2. **Then branches.** For each `prune-*` branch (now including any freed by worktree removal):
   ```
   git -C <repo> branch -d <branch>
   ```
   Use `-d` (safe — refuses unmerged). A `review-gone-ahead` or `review-gone-unknown` branch is never included in this batch — per the verdict table, those need your own verification plus a separate, explicit per-item user confirmation before `-D` (git can't see squash-merges, so `-d` will wrongly refuse even once merged). Do that as its own deliberate step, not folded into the batch prune. A confirmed one needs its worktree removed first if it's checked out in one.
3. **Prunable worktrees:** for each `prunable` entry (administrative record whose directory is already gone from disk), run `git -C <repo> worktree prune` — never `worktree remove <path>`, the path doesn't exist. Safe and non-destructive (no working tree to lose).

**Hard guards (never auto-clean, regardless of `--prune`):** the default branch, the current branch, any primary checkout, anything `active`, `blocked-dirty`, `blocked-locked`, `review-*`. These require the user to act deliberately, item by item.

After cleanup, re-run Step 1 read-only and show the user the now-clean state as verification.

## Notes

- If you keep an allowlist of pre-approved commands, allowlist only the read-only git verbs the scanner uses. The destructive verbs (`branch -d/-D`, `worktree remove`, `push --delete`) should stay prompted, not allowlisted.
- This skill never deletes remote branches. Remote cleanup is out of scope (deliberate — avoids touching shared state).
- The scanner is pure read-only by default; the only network it does is the optional `--fetch`.
