"""Describe scan evidence without converting an absent or rejected scan to success."""
from collections import Counter
import json
import os
from pathlib import Path
import sys


def summary(folder, outcome):
    scan = folder / 'scan.json'
    lines = ['# Independent Debian security acceptance', '',
        'Candidate gate: ' + ('accepted' if outcome == 'success' and scan.is_file() and
            (folder / 'receipt.json').is_file() else 'not accepted'),
        'This workflow does not publish images or grant vulnerability exceptions.', '']
    if not scan.is_file():
        return '\n'.join(lines + ['No completed scan available; security acceptance remains incomplete.']) + '\n'
    if scan.stat().st_size > 64 * 1024 ** 2:
        raise ValueError('Bounded scan required')
    report = json.loads(scan.read_text())
    counts = Counter()
    fixed = 0
    for result in report.get('Results', []):
        for item in result.get('Vulnerabilities') or []:
            severity = item.get('Severity', 'UNKNOWN')
            if severity not in ['UNKNOWN', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
                raise ValueError('Unknown severity representation')
            counts[severity] += 1
            fixed += bool(item.get('FixedVersion'))
    lines += ['| Severity | Observed findings |', '| --- | ---: |']
    lines += [f'| {severity} | {counts[severity]} |' for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']]
    lines += ['', f'Findings with an upstream fixed version: {fixed}.',
        'Counts are observations; the exact-image/OS/database/exception gate decides acceptance.']
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    text = summary(Path(sys.argv[1]), os.environ['GATE_OUTCOME'])
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as output:
        output.write(text)
