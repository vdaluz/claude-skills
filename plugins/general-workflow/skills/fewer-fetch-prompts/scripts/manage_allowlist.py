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
import shutil
import sys
from datetime import datetime

SETTINGS_PATH = os.path.join(os.path.expanduser('~'), '.claude', 'settings.json')


def load():
    with open(SETTINGS_PATH) as f:
        return json.load(f)


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

    backup_path = f'{SETTINGS_PATH}.bak-{datetime.now():%Y%m%d%H%M%S}'
    shutil.copy2(SETTINGS_PATH, backup_path)

    added = []
    for domain in domains:
        entry = f'WebFetch(domain:{domain})'
        if entry not in allow:
            allow.append(entry)
            added.append(entry)

    with open(SETTINGS_PATH, 'w') as f:
        json.dump(settings, f, indent=4)

    print(f'Backed up settings.json to {backup_path}')
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
