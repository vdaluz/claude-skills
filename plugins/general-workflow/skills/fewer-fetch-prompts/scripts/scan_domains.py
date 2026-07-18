#!/usr/bin/env python3
"""Scan Claude Code session transcripts for fetched domains.

Primary pass parses actual WebFetch tool_use calls from JSONL transcripts
(reflects domains Claude actually fetched, not just any URL mentioned in
text). If that yields few results -- WebFetch calls may be stored
differently across Claude Code versions -- falls back to a broader raw-URL
scan automatically.
"""

import json
import glob
import re
import os
from urllib.parse import urlparse
from collections import Counter

TRANSCRIPTS_GLOB = os.path.join(os.path.expanduser('~'), '.claude', 'projects', '**', '*.jsonl')
FALLBACK_THRESHOLD = 5


def scan_tool_use():
    domains = Counter()
    for f in glob.glob(TRANSCRIPTS_GLOB, recursive=True):
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
                                        domain = urlparse(url).netloc.lower().split(':')[0]
                                        if domain:
                                            domains[domain] += 1
                    except Exception:
                        pass
        except OSError:
            pass
    return domains


def scan_raw_urls():
    domains = Counter()
    for f in glob.glob(TRANSCRIPTS_GLOB, recursive=True):
        try:
            with open(f) as fp:
                for line in fp:
                    try:
                        msg = json.loads(line)
                        for url in re.findall(r'https?://([^/"\s\'\\]+)', json.dumps(msg)):
                            domain = url.split('/')[0].lower().split(':')[0]
                            if '.' in domain:
                                domains[domain] += 1
                    except Exception:
                        pass
        except OSError:
            pass
    return domains


def main():
    domains = scan_tool_use()
    mode = 'tool_use'
    if len(domains) < FALLBACK_THRESHOLD:
        fallback = scan_raw_urls()
        if len(fallback) > len(domains):
            domains = fallback
            mode = 'raw_url_fallback'

    print(f'# scan mode: {mode}')
    for domain, count in domains.most_common(50):
        print(f'{count:4d}  {domain}')


if __name__ == '__main__':
    main()
