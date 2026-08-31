#!/usr/bin/env python3
"""Scan Claude Code session transcripts for tool-call frequencies.

Extracts Bash commands (as both a one-token and a two-token leading form)
and MCP tool names from tool_use blocks across the user's recent session
transcripts, and prints raw counts.

Deliberately extraction-only: this does NOT judge which pattern form is
meaningful (some commands have real subcommands, like `git status`; others
don't, like `cat notes.txt`, where the second token is just an argument),
and does NOT classify anything as read-only or already-auto-allowed. Both
are model judgment calls - see fewer-permission-prompts/SKILL.md steps 2-3.
Baking either into this script would mean it silently drifts out of sync
with Claude Code's own evolving auto-allow list, with nothing to catch it.
"""

import json
import glob
import os
import re
from collections import Counter

TRANSCRIPTS_GLOB = os.path.join(os.path.expanduser('~'), '.claude', 'projects', '**', '*.jsonl')
MAX_FILES = 50


def command_forms(segment):
    tokens = segment.strip().split()
    i = 0
    while i < len(tokens) and re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', tokens[i]):
        i += 1
    while i < len(tokens) and tokens[i] == 'sudo':
        i += 1
    if i < len(tokens) and tokens[i] == 'timeout' and i + 1 < len(tokens):
        i += 2
    if i >= len(tokens):
        return []
    forms = [tokens[i]]
    if i + 1 < len(tokens):
        forms.append(f'{tokens[i]} {tokens[i + 1]}')
    return forms


def scan():
    counts = Counter()
    files = sorted(glob.glob(TRANSCRIPTS_GLOB, recursive=True), key=os.path.getmtime, reverse=True)[:MAX_FILES]
    for f in files:
        try:
            with open(f) as fp:
                for line in fp:
                    try:
                        entry = json.loads(line)
                        content = entry.get('message', {}).get('content', [])
                        if not isinstance(content, list):
                            continue
                        for block in content:
                            if not (isinstance(block, dict) and block.get('type') == 'tool_use'):
                                continue
                            name = block.get('name', '')
                            if name == 'Bash':
                                cmd = block.get('input', {}).get('command', '')
                                for segment in re.split(r'&&|\|\||;|\|', cmd):
                                    for form in command_forms(segment):
                                        counts[f'Bash: {form}'] += 1
                            elif name.startswith('mcp__'):
                                counts[name] += 1
                    except Exception:
                        pass
        except OSError:
            pass
    return counts


def main():
    counts = scan()
    for pattern, count in counts.most_common(200):
        print(f'{count:5d}  {pattern}')


if __name__ == '__main__':
    main()
