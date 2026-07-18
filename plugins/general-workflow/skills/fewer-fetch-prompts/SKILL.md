---
name: fewer-fetch-prompts
description: Scan session history and add approved domains to the WebFetch allowlist to reduce permission prompts. Trigger phrases- "reduce WebFetch prompts", "fewer fetch prompts", "WebFetch keeps asking", "add domains to the allowlist", "tune WebFetch permissions". Run when WebFetch approvals are becoming friction.
allowed-tools: Bash(python3 *)
---

Scan Claude Code session transcripts for frequently fetched domains, filter to safe public ones, and add them to `~/.claude/settings.json` so WebFetch no longer prompts for approved domains.

## When to use

Run when WebFetch approval prompts are becoming friction. Re-run periodically as new domains accumulate. Run after adding a new repo or project to your workflow.

Trigger: `/fewer-fetch-prompts`

---

## Steps

### 1. Scan transcripts for WebFetch domains

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fewer-fetch-prompts/scripts/scan_domains.py
```

Parses actual WebFetch tool_use calls from JSONL transcripts — not just any URL mentioned in text — so it reflects domains Claude actually fetched. If that yields few results, the script automatically falls back to a broader raw-URL scan and reports which mode it used.

**Note:** this depends on the transcript JSONL schema, which is Claude Code version-specific and may drift across releases. If the scan comes back empty on a version where it previously worked, that's the first thing to check, not "no domains fetched."

### 2. Filter: exclude these categories automatically

Remove from candidates without asking:

**Internal / private domains:**
- Anything ending in `.lan`, `.local`, `.internal`
- Your own private domains (e.g. `*.yourdomain.com` pointing to internal services)
- `127.0.0.1`, `localhost`, and anything matching RFC-1918 ranges (`10.\d+`, `192.168.\d+`, `172.(1[6-9]|2\d|3[01])\.\d+`)

**User-generated content (high prompt-injection risk — keep on prompt):**
- `github.com`
- `api.github.com`
- `raw.githubusercontent.com`
- `avatars.githubusercontent.com`
- `gist.github.com`

**Noisy / low-value (keep on prompt unless user says otherwise):**
- `medium.com` (user-authored posts, moderate risk)
- `discord.com` (varies)

**Malformed entries:** anything without a real TLD, with `{{`, with port numbers that look internal (`:8080`, `:9090`, `:3000`, `:8000`).

### 3. Read existing allowlist

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fewer-fetch-prompts/scripts/manage_allowlist.py list
```

Remove any candidates already in the allowlist.

### 4. Present candidates to user

Show the filtered, ranked list with counts. Group into tiers:

**Tier 1 — Official documentation (safe to add):**
Official project/vendor docs sites. Non-user-generated. Recommend adding all.

**Tier 2 — Moderated community forums (generally safe):**
Community sites with moderation. Slightly more exposure. Recommend adding with a note.

**Tier 3 — User content / blogs (ask user):**
Medium, dev.to, Reddit, Stack Overflow, etc. User should decide per-site.

Ask: "Add all Tier 1 and Tier 2? Which Tier 3 domains do you want to include?"

### 5. Write to ~/.claude/settings.json

Once user confirms the list:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fewer-fetch-prompts/scripts/manage_allowlist.py add <domain1> <domain2> ...
```

This backs up `settings.json` (timestamped, alongside the original) before rewriting it, adds the approved domains, writes the file, then re-reads and prints the full allowlist to confirm — steps 5 and 6 in one call.

### 6. Verify

The `add` command's own output already includes verification (re-reads the file after writing). Confirm the entries are present and no internal/private domains slipped in.

---

## Notes

- **Wildcards don't work**: `WebFetch(domain:*)` is a confirmed, still-open Claude Code bug — [anthropics/claude-code#9329](https://github.com/anthropics/claude-code/issues/9329) (last updated 2026-03-29, checked 2026-07-18) — still prompts per domain. Must be explicit per domain.
- **Subdomains are not inherited**: `WebFetch(domain:grafana.com)` does NOT cover `grafana.yourdomain.net`. Internal subdomains should be filtered in step 2.
- **Global only**: This skill writes to `~/.claude/settings.json`, covering all projects. There is no project-local mode.
- **Re-run anytime**: Run `/fewer-fetch-prompts` after adding new projects to pick up newly accumulated domains.
- **`json.dump(indent=4)` renormalizes formatting**: the rewrite in `manage_allowlist.py` reformats the whole file to 4-space indent, which can shift unrelated whitespace/ordering even though it doesn't change values. The pre-write backup exists specifically so this is recoverable, not just theoretically safe.
