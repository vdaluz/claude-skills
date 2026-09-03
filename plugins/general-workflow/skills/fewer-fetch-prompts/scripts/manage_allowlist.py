#!/usr/bin/env python3
"""Read or update the WebFetch domain allowlist in ~/.claude/settings.json.

Usage:
    manage_allowlist.py list
    manage_allowlist.py add <domain> [<domain> ...]

`add` backs up settings.json (timestamped, alongside the original) before
rewriting it, then reports what was actually added and re-reads the file
to confirm.
"""

import json
import os
import re
import shutil
import sys
from datetime import datetime

SETTINGS_PATH = os.path.join(os.path.expanduser('~'), '.claude', 'settings.json')
DOMAIN_RE = re.compile(r'^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$')


def load():
    try:
        with open(SETTINGS_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        sys.exit(f'Error: {SETTINGS_PATH} contains invalid JSON: {e}')


def webfetch_entries(settings):
    return [p for p in settings.get('permissions', {}).get('allow', []) if p.startswith('WebFetch')]


def cmd_list():
    settings = load()
    entries = webfetch_entries(settings)
    print(f'{len(entries)} WebFetch domains already allowed:')
    for e in sorted(entries):
        print(' ', e)


def cmd_add(domains):
    settings = load()
    allow = settings.setdefault('permissions', {}).setdefault('allow', [])

    valid_domains = []
    for domain in domains:
        if DOMAIN_RE.match(domain):
            valid_domains.append(domain)
        else:
            print(f'Skipping invalid domain: {domain!r} (must be a bare hostname, no scheme/path/port)')

    if not valid_domains:
        sys.exit('No valid domains to add.')

    if os.path.exists(SETTINGS_PATH):
        backup_path = f'{SETTINGS_PATH}.bak-{datetime.now():%Y%m%d%H%M%S}'
        shutil.copy2(SETTINGS_PATH, backup_path)
        print(f'Backed up settings.json to {backup_path}')
    else:
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        print(f'{SETTINGS_PATH} does not exist yet; creating it.')

    added = []
    for domain in valid_domains:
        entry = f'WebFetch(domain:{domain})'
        if entry not in allow:
            allow.append(entry)
            added.append(entry)

    with open(SETTINGS_PATH, 'w') as f:
        json.dump(settings, f, indent=4)

    print(f'Added {len(added)} entries:')
    for a in added:
        print(' ', a)

    fresh = webfetch_entries(load())
    print(f'\nVerified: {len(fresh)} WebFetch domains now in allowlist:')
    for e in sorted(fresh):
        print(' ', e)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ('list', 'add'):
        sys.exit(__doc__)
    if sys.argv[1] == 'list':
        cmd_list()
    else:
        domains = sys.argv[2:]
        if not domains:
            sys.exit('add requires at least one domain')
        cmd_add(domains)


if __name__ == '__main__':
    main()
