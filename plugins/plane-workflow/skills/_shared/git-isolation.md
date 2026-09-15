# Git isolation protocol (worktrees/branches)

Shared by `start-issue` and `continue-issue`. Read this once; each skill only
states what's specific to its own step.

## Default: branch off main, no worktree

Default to a plain branch per issue — `git checkout -b <issue-id>-<slug>` — off `main`, no PR
required, fast-forward-merged back at wrap-up. Working directly on `main` is the exception: only
when strictly necessary and explicitly authorized (e.g. the user says to skip the branch for a
trivial one-line fix). Worktrees stay opt-in on top of that — reach for one deliberately when this
session genuinely needs isolation, e.g. you know another agent is actively working this repo right
now, or the user asks for one.

## Creating isolation

- Plain branch (default): `git checkout -b <issue-id>-<slug>` off `main`.
- Worktree (deliberate, on top of the branch default): `EnterWorktree` (branch named after the
  issue ID, e.g. `proj-571-feature-name`). Always prompts for confirmation — reach for it only
  when this session genuinely needs concurrent-checkout isolation, not by default.

## Resuming existing isolation

- Worktree already exists: `EnterWorktree` with its `path` (from `git worktree list`).
- Plain branch already exists: `git checkout <branch>`.
- Before editing, rebase onto latest main: `git fetch origin && git rebase origin/main` — so you
  build on top of anything that landed since last session.

## Landing (fast-forward merge + cleanup)

From the primary checkout (`ExitWorktree` with `action: "keep"` first if inside a worktree, so the
branch survives for the merge). The exact commands depend on what the primary checkout's HEAD is
on right now, so check with `git branch --show-current` first. The rule in both cases is the same:
never run `git checkout main` as a landing step. A plain branch checkout has one `.git/HEAD` file
shared across every session working that checkout, so checking out `main` there silently moves
every concurrent session's apparent branch too, not just yours.

**HEAD is already `main`** (the common case after `ExitWorktree action: "keep"`, since the primary
checkout was never moved off `main` in the first place):

```bash
git pull --ff-only && git merge --ff-only <branch> && git push origin main
```

No `git checkout` needed here. HEAD is already where it needs to be, so the pull/merge/push
sequence never touches it.

**HEAD is on anything other than `main`** (your own issue branch, or, in the primary checkout of a
worktree landing, a concurrent session's unrelated plain branch):

```bash
git fetch origin main:main && git fetch . <branch>:main && git push origin main
```

Sync `main` from the remote first. Skipping this and going straight to `git fetch . <branch>:main`
risks setting local `main` to `<branch>`'s tip while origin has moved ahead underneath it, which
fails the push and leaves local `main` diverged from `origin/main` (recover with `git fetch .
origin/main:main -f`). Neither fetch touches HEAD or the working tree, so this is safe regardless
of whose branch is currently checked out **in the primary** — but `git fetch . <branch>:main`
still refuses outright if `main` is checked out in *any* linked worktree, not just the primary
(check `git worktree list` first if you're unsure) — if it is, run the on-`main` sequence from
that worktree instead. Do not run `git fetch . <branch>:main` while
HEAD is on `main` itself: git refuses outright (`fatal: refusing to fetch into branch
'refs/heads/main' checked out at ...`). That's the on-`main` case above, not this one.

If main moved since you branched, each path fails at a different point. Rebase and retry:

- **On-`main` path:** the `git merge --ff-only <branch>` step refuses (diverging branches can't
  fast-forward) because `origin/main` moved ahead of local `main` during the pull. If `<branch>`
  lives in a worktree, re-enter it (`EnterWorktree` with its path from `git worktree list`), run
  `git fetch origin && git rebase main` there — the local `main` ref, not `origin/main`. Since the
  preceding `git pull --ff-only` already brought local `main` up to date with `origin/main`,
  rebasing onto local `main` covers both a moved origin and an already-present unpushed local
  commit in the same step. `ExitWorktree action: "keep"` again, then retry the on-`main` sequence
  from the primary.
  - If `git pull --ff-only` itself refuses instead of the merge step, local `main` has an unpushed
    commit from another session and origin has diverged from it too. Stop and coordinate with that
    session — never rebase or reset `main` in a shared primary to force past this.
  - (Running `git rebase main` directly in the primary itself is always a no-op here, since HEAD
    there is already `main`.) If `<branch>` is a plain branch and
    not checked out anywhere, rebase it from a scratch worktree instead of checking it out in the
    primary (`git worktree add <tmp-path> <branch>`, rebase there, `git worktree remove
    <tmp-path>`). Checking out `<branch>` directly in a shared primary is the same HEAD-hijack
    hazard this section opened with, just moving HEAD the other direction.
- **Off-`main` path:** the `git fetch . <branch>:main` step itself refuses (non-fast-forward).
  Check `git branch --show-current` in the checkout where `<branch>` lives before rebasing "in
  place" — if that checkout's HEAD is actually on `<branch>`, rebase it there (`git fetch origin
  && git rebase origin/main`); if HEAD is on something else (a concurrent session's own branch, in
  the primary checkout of a worktree landing), rebasing "in place" would rebase that other branch,
  not `<branch>` — rebase `<branch>` from a scratch worktree instead (`git worktree add <tmp-path>
  <branch>`, `git fetch origin && git rebase origin/main` there, `git worktree remove <tmp-path>`).
  Either way, then retry the off-`main` sequence above. A rebase rewrites the working tree of the
  checkout it runs in — the scratch-worktree path avoids that shared-checkout hazard entirely.

Then clean up:
- Worktree: `git worktree remove <path>` (add `--force` only if it refuses over the now-merged
  branch). Confirm with `git worktree list` that it's gone. Never `rm -rf` a worktree directory
  directly: that deletes the files but leaves git's own `.git/worktrees/<name>` registration
  dangling. `git worktree remove` is what actually deregisters it.
- Remote branch: `git push origin --delete <branch>`, then `git fetch --prune`. Both are safe
  regardless of what's checked out. If the remote branch is already gone (GitHub auto-deleted it),
  skip this step.
- Local branch: `git branch -d <branch>` (`-D` if rebased) only if `<branch>` is not the branch
  currently checked out in this checkout (check with `git branch --show-current`). Deleting the
  checked-out branch always fails (`error: cannot delete branch '<branch>' used by worktree at
  '<path>'`), and checking out something else first just to force the delete recreates the same
  HEAD-hijack hazard the sequences above exist to avoid. In that case, leave the local ref in
  place. It's fully merged into `main`, so it's inert clutter, not a risk, and it deletes cleanly
  the next time `main` is naturally checked out there for unrelated reasons.

  **If `<branch>` is not checked out anywhere but `-d` still refuses** ("not fully merged"), this
  happens whenever the primary's HEAD sits on a third branch unrelated to both `main` and
  `<branch>` (a concurrent session's own work left checked out there), since `git branch -d` with
  no upstream configured checks merge status against current HEAD, not against `main`. Verify
  ancestry independently before falling back to force-delete, as two separate standalone commands,
  never chained: first `git merge-base --is-ancestor <branch> origin/main`; only if that succeeds,
  `git branch -D <branch>` as its own call. If the ancestry check fails, stop. The refusal is real,
  not spurious.
- Confirm: `git branch -a` shows `main`/`origin/main` plus, in the plain-branch case, the
  already-merged local branch left behind above. That's expected, not a sign cleanup failed.

Skip all of the above only in the rare case you worked directly on `main` (explicitly authorized
exception — see Default above).

**Scratch/verification checkouts** (e.g. building a package for `npm pack` testing) go through
this same `EnterWorktree`/`git worktree add`+`remove` path too, not a hand-made sibling directory
like `../<repo>-worktrees/<name>` — there's no tooling reason to use that shape, and it's the kind
of directory that goes stale and orphaned if created by hand instead.

## Encrypted or binary config merge conflicts

If your project has a file git can't auto-merge (an encrypted secrets blob, a lockfile with
binary sections), a rebase/merge conflict there needs manual handling — do **not** edit the
conflict markers directly. Decrypt or otherwise render both sides to a mergeable form, merge
keeping both branches' changes, then re-encrypt/re-derive before continuing. If you know up front
that a change will touch such a file, note the risk early and rebase right before landing to
minimize the conflict window.
