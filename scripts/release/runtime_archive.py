"""Produce a Docker-load view of the verified OCI image without rebuilding it."""
import io
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tarfile
from oci_candidate import inspect_archive
from strict_json import load


def convert(source_archive, destination, source, version):
    identity = inspect_archive(source_archive, source, version)
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise ValueError('New runtime archive path required')
    with tarfile.open(source_archive, 'r:*') as archive:
        entries = {member.name.removeprefix('./'): member for member in archive if member.isfile()}
        manifest = load(archive.extractfile(entries['blobs/sha256/' + identity['manifest_digest'][7:]]))
        config = 'blobs/sha256/' + identity['config_digest'][7:]
        layers = ['blobs/sha256/' + layer['digest'][7:] for layer in manifest['layers']]
        document = [{'Config': config, 'RepoTags': ['ghcr.io/vpremises/base-debian:' + version], 'Layers': layers}]
        # Copy only already validated config/layer bytes; never extract layer contents.
        with destination.open('xb') as stream, tarfile.open(fileobj=stream, mode='w') as target:
            for name in [config, *dict.fromkeys(layers)]:
                member = entries[name]
                entry = tarfile.TarInfo(name)
                entry.size = member.size
                entry.mode = 0o644
                target.addfile(entry, archive.extractfile(member))
            data = json.dumps(document).encode()
            entry = tarfile.TarInfo('manifest.json')
            entry.size = len(data)
            target.addfile(entry, io.BytesIO(data))
    return identity


def verify_saved_image(source_archive, saved_archive, source, version):
    identity = inspect_archive(source_archive, source, version)
    with tarfile.open(saved_archive, 'r:*') as archive:
        manifests = load(archive.extractfile('manifest.json'))
        if len(manifests) != 1:
            raise ValueError('One tested runtime image required')
        manifest = manifests[0]
        config_bytes = archive.extractfile(manifest['Config']).read(4 * 1024 ** 2 + 1)
        if len(config_bytes) > 4 * 1024 ** 2 or 'sha256:' + hashlib.sha256(config_bytes).hexdigest() != identity['config_digest']:
            raise ValueError('Tested runtime config differs from OCI candidate')
        config = json.loads(config_bytes)
        diff_ids = config['rootfs']['diff_ids']
        if not 1 <= len(diff_ids) <= 128 or len(manifest['Layers']) != len(diff_ids):
            raise ValueError('Tested runtime layer count differs')
        total = 0
        for name, expected in zip(manifest['Layers'], diff_ids):
            stream = io.BufferedReader(archive.extractfile(name))
            if stream.peek(2)[:2] == b'\x1f\x8b':
                stream = gzip.GzipFile(fileobj=stream)
            digest = hashlib.sha256()
            while block := stream.read(1024 * 1024):
                total += len(block)
                if total > 1024 ** 3:
                    raise ValueError('Tested runtime layer bound exceeded')
                digest.update(block)
            if 'sha256:' + digest.hexdigest() != expected:
                raise ValueError('Tested runtime layer differs from OCI candidate')
    return identity


if __name__ == '__main__':
    function = verify_saved_image if sys.argv[1] == 'verify' else convert
    print(json.dumps(function(*sys.argv[2:])))
