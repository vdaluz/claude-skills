#!/usr/bin/env python3
"""
Deterministic, read-only staleness scanner for git repos under a root (default ~/Repos).

Emits structured JSON (default) or a grouped text summary (--text) describing, per repo,
every local branch and worktree with the signals needed to judge staleness, plus a verdict.

Design: this script is the deterministic core. It NEVER mutates anything (no fetch unless
--fetch, no delete ever). The calling Claude skill does grouping, judgment, and — only behind
explicit confirmation — the destructive cleanup via prompted git commands.

Refinements baked in:
  1. "gone" upstream is detected via `%(upstream:track)` == [gone], NOT `@{u}` presence
     (rev-parse @{u} still returns the configured name after the remote ref is deleted).
     [gone] is also the only reliable proxy for squash-merged branches.
  2. Worktree branch is always read from `worktree list --porcelain`, never the directory name
     (directory names drift from the branch they hold).
  3. The remote name is never assumed to be "origin" — it's resolved per repo (remote HEAD
     symref, or the default branch's own configured upstream remote), so a renamed remote
     doesn't silently blank out ahead/behind counts. When no remote can be resolved at all,
     ahead/behind stay `None` (unknown) rather than being coerced to 0 — an unknown count can
     never produce a `prune-*` verdict, only a `review-*` one.

Usage:
  scan.py [--root ~/Repos] [--age-days 60] [--fetch] [--text] [PATH ...]
"""
import argparse, json, os, subprocess, sys, time


def sh(args):
    try:
        r = subprocess.run(args, capture_output=True, text=True)
        return r.stdout.strip()
    except Exception:
        return ""


def ok(args):
    try:
        return subprocess.run(args, capture_output=True, text=True).returncode == 0
    except Exception:
        return False


def is_repo(path):
    return os.path.isdir(os.path.join(path, ".git")) or os.path.isfile(os.path.join(path, ".git"))


def discover(root, explicit):
    if explicit:
        return [os.path.abspath(os.path.expanduser(p)) for p in explicit if is_repo(os.path.expanduser(p))]
    root = os.path.expanduser(root)
    if not os.path.isdir(root):
        sys.exit(f"error: root path {root!r} does not exist (pass --root to point at your repos)")
    out = []
    for name in sorted(os.listdir(root)):
        p = os.path.join(root, name)
        if os.path.isdir(p) and is_repo(p):
            out.append(p)
    return out


def local_default_branch(repo):
    for b in ("main", "master"):
        if ok(["git", "-C", repo, "show-ref", "--verify", "--quiet", f"refs/heads/{b}"]):
            return b
    return None


def resolve_remote_and_default(repo):
    """Never assume the remote is named "origin" — a rename (origin -> upstream) must still
    resolve correctly, since ahead/behind against the wrong (or a nonexistent) remote is what
    silently turns "has unmerged commits" into "safe to prune"."""
    for ref in sh(["git", "-C", repo, "for-each-ref", "--format=%(refname)",
                   "refs/remotes/*/HEAD"]).splitlines():
        target = sh(["git", "-C", repo, "symbolic-ref", "--quiet", ref])
        prefix = ref[:-len("HEAD")]  # "refs/remotes/<remote>/"
        if target and target.startswith(prefix):
            remote = prefix[len("refs/remotes/"):].rstrip("/")
            return remote, target[len(prefix):]
    # no remote HEAD symref recorded (e.g. remote added without `git remote set-head`) — fall
    # back to a local main/master and whatever remote it's tracking, if any.
    defb = local_default_branch(repo)
    if defb:
        remote = sh(["git", "-C", repo, "for-each-ref", "--format=%(upstream:remotename)",
                    f"refs/heads/{defb}"]) or None
        return remote, defb
    return None, None


def base_ref_for(repo, remote, defb):
    """The ref to diff branches against: remote/defb when that ref actually exists locally,
    else the local defb branch itself, else None (genuinely unknown — never silently 0)."""
    if not defb:
        return None
    if remote:
        candidate = f"{remote}/{defb}"
        if ok(["git", "-C", repo, "rev-parse", "--verify", "--quiet", candidate]):
            return candidate
    return f"refs/heads/{defb}"


def count(repo, rng):
    c = sh(["git", "-C", repo, "rev-list", "--count", rng])
    try:
        return int(c)
    except ValueError:
        return None


def scan_repo(repo, age_days, do_fetch):
    name = os.path.basename(repo)
    if do_fetch:
        subprocess.run(["git", "-C", repo, "fetch", "--all", "--prune", "--quiet"],
                       capture_output=True, text=True)
    remote, defb = resolve_remote_and_default(repo)
    base_ref = base_ref_for(repo, remote, defb)
    cur = sh(["git", "-C", repo, "branch", "--show-current"])
    now = time.time()

    # branches checked out in a worktree (can't be deleted while checked out)
    wt_porc = sh(["git", "-C", repo, "worktree", "list", "--porcelain"])
    wt_blocks = [b for b in wt_porc.split("\n\n") if b.strip()]

    def parse_wt(block):
        d = {}
        for line in block.splitlines():
            parts = line.split(" ", 1)
            d[parts[0]] = parts[1] if len(parts) > 1 else True
        return d

    wt_dicts = [parse_wt(b) for b in wt_blocks]
    checked_out = set()
    for d in wt_dicts:
        br = d.get("branch", "")
        if isinstance(br, str):
            checked_out.add(br.replace("refs/heads/", ""))

    merged = set()
    if defb:
        for ln in sh(["git", "-C", repo, "branch", "--merged", f"refs/heads/{defb}"]).splitlines():
            merged.add(ln.replace("*", "").replace("+", "").strip())

    # track state per branch via for-each-ref (gives [gone]/[ahead]/[behind])
    track = {}
    fmt = "%(refname:short)\t%(upstream:track)"
    for ln in sh(["git", "-C", repo, "for-each-ref", "--format", fmt, "refs/heads"]).splitlines():
        if "\t" in ln:
            b, t = ln.split("\t", 1)
        else:
            b, t = ln, ""
        track[b] = t

    branches = []
    for b in sh(["git", "-C", repo, "for-each-ref", "--sort=committerdate",
                 "--format=%(refname:short)", "refs/heads"]).splitlines():
        ts = sh(["git", "-C", repo, "log", "-1", "--format=%ct", b])
        age = int((now - int(ts)) / 86400) if ts.isdigit() else None
        ahead = count(repo, f"{base_ref}..{b}") if base_ref else None
        behind = count(repo, f"{b}..{base_ref}") if base_ref else None
        gone = "[gone]" in track.get(b, "")
        is_merged = b in merged
        in_wt = b in checked_out
        v = branch_verdict(b, defb, cur, gone, is_merged, ahead, behind, age, age_days, in_wt)
        branches.append(dict(name=b, age_days=age, ahead=ahead, behind=behind,
                             merged=is_merged, gone=gone, current=(b == cur),
                             in_worktree=in_wt, verdict=v))

    worktrees = []
    for i, d in enumerate(wt_dicts):
        path = d.get("worktree", "")
        br = d.get("branch", "")
        br = br.replace("refs/heads/", "") if isinstance(br, str) else ""
        detached = "detached" in d
        bare = "bare" in d
        locked = "locked" in d
        missing = bool(path) and not bare and not os.path.isdir(path)
        prunable = missing or ("prunable" in d)
        dirty = bool(sh(["git", "-C", path, "status", "--porcelain"])) if (path and not bare and not missing) else False
        ahead = count(repo, f"{base_ref}..{br}") if (br and base_ref) else None
        behind = count(repo, f"{br}..{base_ref}") if (br and base_ref) else None
        gone = "[gone]" in track.get(br, "")
        is_merged = br in merged
        primary = (i == 0)
        v = worktree_verdict(br, defb, primary, detached, bare, locked, dirty,
                             gone, is_merged, ahead, behind, prunable)
        worktrees.append(dict(path=path, name=os.path.basename(path), branch=br or None,
                              primary=primary, detached=detached, bare=bare, locked=locked,
                              dirty=dirty, prunable=prunable, ahead=ahead, behind=behind,
                              merged=is_merged, gone=gone, verdict=v))

    return dict(name=name, path=repo, default=defb, remote=remote, current=cur,
                branches=branches, worktrees=worktrees)


def branch_verdict(b, defb, cur, gone, merged, ahead, behind, age, age_days, in_wt):
    if defb and b == defb:
        return "protected-default"
    if b == cur:
        return "protected-current"
    if in_wt:
        # checked out elsewhere: judge by the worktree; deleting the branch needs the worktree gone first
        return "in-worktree"
    if gone and ahead is None:
        return "review-gone-unknown"     # upstream deleted, can't confirm no local commits — never auto-prune
    if (ahead or 0) > 0 and gone:
        return "review-gone-ahead"       # remote deleted but local commits exist
    if (ahead or 0) > 0 and not merged:
        return "active"                  # unmerged local work — protect
    if gone:
        return "prune-gone"              # upstream deleted (squash-merge proxy), confirmed no local-only work
    if merged and (ahead or 0) == 0:
        return "prune-merged"
    if (behind or 0) > 0 and (ahead or 0) == 0:
        return "review-behind"
    if age is not None and age >= age_days and (ahead or 0) == 0:
        return "review-old"
    return "keep"


def worktree_verdict(br, defb, primary, detached, bare, locked, dirty, gone, merged, ahead, behind, prunable):
    if bare:
        return "bare"
    if primary or (defb and br == defb):
        return "protected-primary"
    if prunable:
        return "prunable"                # administrative entry, working directory is gone
    if dirty:
        return "blocked-dirty"
    if locked:
        return "blocked-locked"
    if detached:
        return "review-detached"
    if gone and ahead is None:
        return "review-gone-unknown"
    if (ahead or 0) > 0 and gone:
        return "review-gone-ahead"
    if (ahead or 0) > 0 and not merged:
        return "active"
    if gone:
        return "prune-gone"
    if merged and (ahead or 0) == 0:
        return "prune-merged"
    if (behind or 0) > 0 and (ahead or 0) == 0:
        return "review-behind"
    return "keep"


PRUNE = {"prune-gone", "prune-merged"}


def text_report(data):
    out = []
    for r in data["repos"]:
        wt_prune = [w for w in r["worktrees"] if w["verdict"] in PRUNE]
        wt_prunable = [w for w in r["worktrees"] if w["verdict"] == "prunable"]
        br_prune = [b for b in r["branches"] if b["verdict"] in PRUNE]
        review = [x for x in r["worktrees"] + r["branches"]
                  if x["verdict"].startswith("review")]
        if not (wt_prune or wt_prunable or br_prune or review):
            continue
        out.append(f"\n### {r['name']}  (default: {r['default']}, remote: {r['remote']})")
        if wt_prune:
            out.append("  worktrees to prune:")
            for w in wt_prune:
                out.append(f"    - {w['name']:<34} [{w['branch']}] behind={w['behind']} ahead={w['ahead']} → {w['verdict']}")
        if wt_prunable:
            out.append("  worktrees with a missing directory (admin cleanup only — `git worktree prune`):")
            for w in wt_prunable:
                out.append(f"    - {w['name']:<34} [{w['branch']}] path={w['path']}")
        if br_prune:
            out.append("  branches to prune:")
            for b in br_prune:
                out.append(f"    - {b['name']:<40} behind={b['behind']} → {b['verdict']}")
        if review:
            out.append("  needs review (NOT auto-pruned):")
            for x in review:
                label = x.get("name")
                out.append(f"    - {label:<40} → {x['verdict']}")
    if not out:
        return "All clean — nothing stale found."
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", help="specific repo paths (default: all under --root)")
    ap.add_argument("--root", default="~/Repos")
    ap.add_argument("--age-days", type=int, default=60)
    ap.add_argument("--fetch", action="store_true", help="git fetch --prune first (network, slower)")
    ap.add_argument("--text", action="store_true", help="human summary instead of JSON")
    args = ap.parse_args()

    repos = discover(args.root, args.paths)
    data = {"root": os.path.expanduser(args.root), "age_days": args.age_days,
            "fetched": args.fetch, "repos": [scan_repo(r, args.age_days, args.fetch) for r in repos]}

    if args.text:
        print(text_report(data))
    else:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
