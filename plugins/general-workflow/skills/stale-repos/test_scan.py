#!/usr/bin/env python3
"""
Stdlib-only fixture test for scan.py (META-111). Reproduces the reported data-loss bug
(remote renamed away from "origin" silently turned unmerged local commits into "prune-gone")
plus the other fixes from the same issue. Not wired into CI or pytest — a manual check /
future CI building block.

Run: python3 test_scan.py
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCAN = os.path.join(HERE, "scan.py")


def run(args, cwd=None, check=True):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed:\n{r.stderr}")
    return r


def git(repo, *args, check=True):
    return run(["git", "-C", repo, *args], check=check).stdout


def init_repo(path, initial_branch="main"):
    os.makedirs(path, exist_ok=True)
    run(["git", "init", "-q", "-b", initial_branch, path])
    git(path, "config", "user.email", "test@example.com")
    git(path, "config", "user.name", "Test")
    return path


def commit(path, msg, filename="f.txt"):
    with open(os.path.join(path, filename), "a") as fh:
        fh.write(msg + "\n")
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", msg)


def scan_json(root):
    r = run(["python3", SCAN, "--root", root])
    return json.loads(r.stdout)


def find(items, **kw):
    for it in items:
        if all(it.get(k) == v for k, v in kw.items()):
            return it
    return None


def test_renamed_remote_gone_ahead():
    """Exact reported repro: remote named "upstream" (not "origin"), a branch with a real
    local commit ahead of its upstream, upstream branch then deleted. Must resolve to
    review-gone-ahead with a real ahead count — never prune-gone / ahead=None."""
    with tempfile.TemporaryDirectory() as tmp:
        remote = init_repo(os.path.join(tmp, "remote"))
        commit(remote, "initial")

        root = os.path.join(tmp, "root")
        repo = init_repo(os.path.join(root, "repo1"))
        git(repo, "remote", "add", "upstream", remote)
        git(repo, "fetch", "-q", "upstream")
        git(repo, "checkout", "-q", "-b", "main", "upstream/main")
        git(repo, "branch", "-q", "--set-upstream-to=upstream/main", "main")

        git(remote, "checkout", "-q", "-b", "feature", "main")
        commit(remote, "feature work")
        git(repo, "fetch", "-q", "upstream")
        git(repo, "checkout", "-q", "-b", "feature", "upstream/feature")
        git(repo, "branch", "-q", "--set-upstream-to=upstream/feature", "feature")
        commit(repo, "extra local-only commit", filename="ahead.txt")

        # a control branch: genuinely merged, no extra commits — must stay prune-gone
        git(repo, "checkout", "-q", "main")
        git(remote, "checkout", "-q", "-b", "old-merged", "main")
        git(remote, "checkout", "-q", "main")
        git(repo, "fetch", "-q", "upstream")
        git(repo, "checkout", "-q", "-b", "old-merged", "upstream/old-merged")
        git(repo, "checkout", "-q", "main")

        # remote deletes both branches (squash-merge simulation), local prunes tracking refs
        git(remote, "branch", "-q", "-D", "feature")
        git(remote, "branch", "-q", "-D", "old-merged")
        git(repo, "fetch", "-q", "--prune", "upstream")

        data = scan_json(root)
        repo1 = find(data["repos"], name="repo1")
        assert repo1 is not None, "repo1 not discovered"
        assert repo1["remote"] == "upstream", f"remote resolution failed: {repo1['remote']!r}"

        feature = find(repo1["branches"], name="feature")
        assert feature["ahead"] not in (None, 0), f"ahead not detected: {feature}"
        assert feature["gone"] is True
        assert feature["verdict"] == "review-gone-ahead", \
            f"DATA-LOSS BUG: expected review-gone-ahead, got {feature['verdict']!r} (ahead={feature['ahead']})"

        old = find(repo1["branches"], name="old-merged")
        assert old["gone"] is True
        assert (old["ahead"] or 0) == 0
        assert old["verdict"] == "prune-gone", f"control case regressed: {old['verdict']!r}"

    print("PASS: test_renamed_remote_gone_ahead")


def test_missing_root_clean_error():
    r = run(["python3", SCAN, "--root", "/nonexistent-path-for-test-scan"], check=False)
    assert r.returncode != 0
    assert "Traceback" not in r.stderr, f"uncaught traceback instead of a clean error:\n{r.stderr}"
    assert "does not exist" in r.stderr, f"unexpected error text:\n{r.stderr}"
    print("PASS: test_missing_root_clean_error")


def test_prunable_worktree():
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, "root")
        repo = init_repo(os.path.join(root, "repo2"))
        commit(repo, "initial")
        wt_path = os.path.join(tmp, "wt-elsewhere")
        git(repo, "worktree", "add", "-q", "-b", "side", wt_path, "main")

        import shutil
        shutil.rmtree(wt_path)

        data = scan_json(root)
        repo2 = find(data["repos"], name="repo2")
        wt = find(repo2["worktrees"], branch="side")
        assert wt is not None, "worktree entry not found after directory removal"
        assert wt["verdict"] == "prunable", f"expected prunable, got {wt['verdict']!r}"

    print("PASS: test_prunable_worktree")


def test_default_branch_multi_segment_ref():
    """default_branch() must not truncate a ref like refs/remotes/upstream/release/2024
    down to just "2024" (old bug: .split('/')[-1])."""
    with tempfile.TemporaryDirectory() as tmp:
        remote = init_repo(os.path.join(tmp, "remote"), initial_branch="release/2024")
        commit(remote, "initial")

        root = os.path.join(tmp, "root")
        repo = init_repo(os.path.join(root, "repo3"))
        git(repo, "remote", "add", "origin", remote)
        git(repo, "fetch", "-q", "origin")
        git(repo, "remote", "set-head", "origin", "release/2024")
        git(repo, "checkout", "-q", "-b", "release/2024", "origin/release/2024")

        data = scan_json(root)
        repo3 = find(data["repos"], name="repo3")
        assert repo3["default"] == "release/2024", f"ref truncated: {repo3['default']!r}"

    print("PASS: test_default_branch_multi_segment_ref")


if __name__ == "__main__":
    tests = [
        test_renamed_remote_gone_ahead,
        test_missing_root_clean_error,
        test_prunable_worktree,
        test_default_branch_multi_segment_ref,
    ]
    failures = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failures += 1
            print(f"FAIL: {t.__name__}: {e}")
        except Exception as e:
            failures += 1
            print(f"ERROR: {t.__name__}: {e}")
    if failures:
        sys.exit(f"\n{failures} test(s) failed")
    print("\nAll tests passed.")
