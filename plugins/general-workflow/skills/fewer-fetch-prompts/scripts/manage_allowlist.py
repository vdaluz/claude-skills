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
# Matches the RFC-1918/loopback exclusion the parent skill's step 2 already applies to
# candidates it surfaces - this script is a second entry point (a user can run `add`
# directly) that needs the same exclusion, since DOMAIN_RE's hostname syntax check
# doesn't distinguish a dotted IP literal from a real domain.
PRIVATE_IPV4_RE = re.compile(
    r'^(127\.0\.0\.1|10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})$'
)


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
    if not isinstance(allow, list):
        sys.exit(f'Error: permissions.allow in {SETTINGS_PATH} is not a list '
                  f'({type(allow).__name__}) - fix that by hand before running add.')

    valid_domains = []
    for domain in domains:
        if not DOMAIN_RE.match(domain):
            print(f'Skipping invalid domain: {domain!r} (must be a bare hostname, no scheme/path/port)')
        elif PRIVATE_IPV4_RE.match(domain):
            print(f'Skipping private/internal address: {domain!r} '
                  f'(RFC-1918/loopback - use a hostname if you need an internal service allowed)')
        else:
            valid_domains.append(domain)

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
