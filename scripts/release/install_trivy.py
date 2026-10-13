#!/usr/bin/env python3
"""Install a public, checksum-pinned scanner into a task-specific tools directory."""
import hashlib
import io
from pathlib import Path
import sys
import tarfile
import urllib.request

URL = 'https://github.com/aquasecurity/trivy/releases/download/v0.75.0/trivy_0.75.0_Linux-64bit.tar.gz'
SHA256 = 'c6e65abddb348e25f10549df887045629cf28cc72453cd1c63acb717316b3f3f'


def main():
    dest = Path(sys.argv[1])
    if dest.exists() or dest.is_symlink():
        raise ValueError('new scanner path required')
    with urllib.request.urlopen(URL, timeout=120) as response:
        data = response.read(200 * 1024 ** 2 + 1)
    if len(data) > 200 * 1024 ** 2 or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('scanner archive checksum mismatch')
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        member = archive.getmember('trivy')
        if not member.isfile() or member.size > 256 * 1024 ** 2:
            raise ValueError('bounded regular scanner required')
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open('xb') as stream:
            stream.write(archive.extractfile(member).read())
    dest.chmod(0o755)
    print('Installed checksum-verified trivy@0.75.0')


if __name__ == '__main__':
    main()
