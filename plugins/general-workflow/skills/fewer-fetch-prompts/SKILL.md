---
name: fewer-fetch-prompts
description: Scan session history and add approved domains to the WebFetch allowlist to reduce permission prompts. Run when WebFetch approvals are becoming friction.
---

Scan Claude Code session transcripts for frequently fetched domains, filter to safe public ones, and add them to `~/.claude/settings.json` so WebFetch no longer prompts for approved domains.

## When to use

Run when WebFetch approval prompts are becoming friction. Re-run periodically as new domains accumulate. Run after adding a new repo or project to your workflow.

Trigger: `/fewer-fetch-prompts`

---

## Steps

### 1. Scan transcripts for WebFetch domains

Run this scan. It parses actual WebFetch tool_use calls from JSONL transcripts — not just any URL mentioned in text — so it reflects domains Claude actually fetched:

```python
import json, glob, os
from urllib.parse import urlparse
from collections import Counter

home = os.path.expanduser('~')
domains = Counter()
for f in glob.glob(f'{home}/.claude/projects/**/*.jsonl', recursive=True):
    try:
        with open(f) as fp:
            for line in fp:
                try:
                    entry = json.loads(line)
                    content = entry.get('message', {}).get('content', [])
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get('type') == 'tool_use' and block.get('name') == 'WebFetch':
                                url = block.get('input', {}).get('url', '')
                                if url:
                                    parsed = urlparse(url)
                                    domain = parsed.netloc.lower().split(':')[0]
                                    if domain:
                                        domains[domain] += 1
                except:
                    pass
    except:
        pass

for domain, count in domains.most_common(50):
    print(f'{count:4d}  {domain}')
```

If the above returns few results, fall back to the broader URL scan:

```python
import json, glob, re, os
from collections import Counter

home = os.path.expanduser('~')
domains = Counter()
for f in glob.glob(f'{home}/.claude/projects/**/*.jsonl', recursive=True):
    try:
        with open(f) as fp:
            for line in fp:
                try:
                    msg = json.loads(line)
                    for url in re.findall(r'https?://([^/"\s\'\\]+)', json.dumps(msg)):
                        domain = url.split('/')[0].lower().split(':')[0]
                        if '.' in domain:
                            domains[domain] += 1
                except:
                    pass
    except:
        pass

for domain, count in domains.most_common(50):
    print(f'{count:4d}  {domain}')
```

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

```python
import json, os

settings_path = os.path.join(os.path.expanduser('~'), '.claude', 'settings.json')
with open(settings_path) as f:
    s = json.load(f)
existing = [p for p in s.get('permissions', {}).get('allow', []) if p.startswith('WebFetch')]
print('Already allowed:')
for e in existing: print(' ', e)
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

```python
import json, os

approved_domains = [
    # Fill from user-confirmed list
]

settings_path = os.path.join(os.path.expanduser('~'), '.claude', 'settings.json')
with open(settings_path) as f:
    settings = json.load(f)

allow = settings.setdefault('permissions', {}).setdefault('allow', [])

added = []
for domain in approved_domains:
    entry = f'WebFetch(domain:{domain})'
    if entry not in allow:
        allow.append(entry)
        added.append(entry)

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=4)

print(f'Added {len(added)} entries:')
for a in added:
    print(' ', a)
```

### 6. Verify

```python
import json, os

settings_path = os.path.join(os.path.expanduser('~'), '.claude', 'settings.json')
with open(settings_path) as f:
    s = json.load(f)
fetch = [p for p in s.get('permissions', {}).get('allow', []) if p.startswith('WebFetch')]
print(f'{len(fetch)} WebFetch domains in allowlist:')
for f in sorted(fetch): print(' ', f)
```

Confirm the entries are present and no internal/private domains slipped in.

---

## Notes

- **Wildcards don't work**: `WebFetch(domain:*)` is a known Claude Code bug — still prompts per domain. Must be explicit per domain.
- **Subdomains are not inherited**: `WebFetch(domain:grafana.com)` does NOT cover `grafana.yourdomain.net`. Internal subdomains should be filtered in step 2.
- **Global only**: This skill writes to `~/.claude/settings.json`, covering all projects. There is no project-local mode.
- **Re-run anytime**: Run `/fewer-fetch-prompts` after adding new projects to pick up newly accumulated domains.
