# Git isolation protocol (worktrees/branches)

Shared by `start-issue`, `continue-issue`, and `wrap-up-issue`. Read this once; each skill only
states what's specific to its own step.

## Default: work directly on main

Isolation used to be mandatory when a large backlog meant several agents worked a repo at once;
that pressure is gone. Default to working directly on `main` unless this session genuinely needs
isolation — e.g. you know another agent is actively working this repo right now, or the user asks
for one.

## Creating isolation

- Worktree: `EnterWorktree` (branch named after the issue ID, e.g. `lab-571-apprise-mailrise`).
  Always prompts for confirmation now — reach for it deliberately, not by default.
- Plain branch (no worktree): `git checkout -b <issue-id>-<slug>`.

## Resuming existing isolation

- Worktree already exists: `EnterWorktree` with its `path` (from `git worktree list`).
- Plain branch already exists: `git checkout <branch>`.
- Before editing, rebase onto latest main: `git fetch origin && git rebase origin/main` — so you
  build on top of anything that landed since last session.

## Landing (fast-forward merge + cleanup)

From the primary checkout (`ExitWorktree` with `action: "keep"` first if inside a worktree, so the
branch survives for the merge):

```bash
git checkout main && git pull --ff-only && git merge --ff-only <branch> && git push origin main
```

If `--ff-only` is refused, main moved during wrap-up — rebase the branch again and retry.

Then clean up:
- Worktree: `git worktree remove <path>` (add `--force` only if it refuses over the now-merged
  branch). Confirm with `git worktree list` that it's gone.
- Branch: delete both local and remote — `git branch -d <branch>` (`-D` if rebased), `git push
  origin --delete <branch>`, `git fetch --prune`. If the remote branch is already gone (GitHub
  auto-deleted it), skip the remote delete but always delete local. Confirm `git branch -a` shows
  only `main`/`origin/main`.

Skip all of the above if you worked directly on `main`.

## `iac/ansible/group_vars/all/vault.yml` merge conflicts

A single encrypted blob — git cannot auto-merge it, so a rebase/merge conflict here needs manual
handling: do **not** edit the conflict markers. Decrypt both sides, merge the plaintext keeping
both branches' changes, re-encrypt, then continue. Full protocol:
`~/Repos/vdaluz-kb/infrastructure/ansible-vault-merge-conflicts.md`. If you know up front that a
change will touch this file, note the risk early — keep the edit small and rebase right before
landing to minimize the conflict window.
