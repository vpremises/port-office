#!/usr/bin/env python3
"""Bind reviewed bytes and their scan, then verify the same bytes before promotion."""
import argparse
import datetime
import json
from pathlib import Path
from oci_candidate import file_digest, inspect_archive
from vulnerability_policy import accept_scan
from strict_json import load


def regular(path):
    value = Path(path)
    if value.is_symlink() or not value.is_file():
        raise ValueError('regular candidate evidence required')
    return value


def read(path):
    path = regular(path)
    if path.stat().st_size > 16 * 1024 ** 2:
        raise ValueError('evidence bound exceeded')
    with path.open() as stream:
        return load(stream)


def inspect(args):
    archive = regular(args.archive)
    identity = inspect_archive(archive, args.source, args.version)
    scan = read(args.scan)
    if scan.get('Metadata', {}).get('ImageID') != identity['config_digest']:
        raise ValueError('scan is for a different image')
    result = accept_scan(scan, read(args.database), read(args.exceptions),
                         datetime.datetime.now(datetime.timezone.utc))
    return {**identity, 'repository': 'vpremises/port-office', 'scanner': 'trivy@0.75.0',
            'scan_sha256': file_digest(args.scan), 'database_sha256': file_digest(args.database),
            'exceptions_sha256': file_digest(args.exceptions), 'scan_acceptance': result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['record', 'verify'])
    for field in ['archive', 'scan', 'database', 'exceptions', 'source', 'version', 'receipt']:
        parser.add_argument('--' + field, required=True)
    parser.add_argument('--expected-sha256')
    args = parser.parse_args()
    result = inspect(args)
    if args.mode == 'verify':
        if not args.expected_sha256 or result['archive_sha256'] != args.expected_sha256:
            raise ValueError('owner-reviewed archive mismatch')
        if read(args.receipt) != result:
            raise ValueError('changed candidate evidence')
    else:
        dest = Path(args.receipt)
        if dest.exists() or dest.is_symlink():
            raise ValueError('receipt must be new; evidence cannot be overwritten')
        with dest.open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    print(json.dumps({'accepted': True, 'archive_sha256': result['archive_sha256'],
                      'registry_digest': result['registry_digest']}))


if __name__ == '__main__':
    main()
