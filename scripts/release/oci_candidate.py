"""Inspect a bounded OCI archive without extracting or executing layer contents."""
import hashlib
from strict_json import load
import re
import tarfile


def file_digest(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inspect_archive(path, source, version):
    if not re.fullmatch(r'[a-f0-9]{40}', source) or not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('exact source and release version required')
    with tarfile.open(path, 'r:*') as archive:
        entries = {}
        total = 0
        for member in archive:
            name = member.name.removeprefix('./')
            if name in entries or not re.fullmatch(r'(?:index\.json|oci-layout|blobs(?:/sha256(?:/[a-f0-9]{64})?)?)/?', name):
                raise ValueError('unexpected or duplicate archive path')
            if not (member.isfile() or member.isdir()) or member.size < 0:
                raise ValueError('links and special files are rejected')
            total += member.size
            if total > 1024 ** 3 or len(entries) >= 10000:
                raise ValueError('archive bound exceeded')
            entries[name] = member

        def read_json(name):
            member = entries[name]
            if not member.isfile() or member.size > 4 * 1024 ** 2:
                raise ValueError('bounded regular JSON required')
            return load(archive.extractfile(member))

        if read_json('oci-layout') != {'imageLayoutVersion': '1.0.0'}:
            raise ValueError('unsupported OCI layout')
        visited = set()

        def descriptor(item):
            digest = item.get('digest', '')
            if not re.fullmatch(r'sha256:[a-f0-9]{64}', digest):
                raise ValueError('SHA256 descriptor required')
            name = 'blobs/sha256/' + digest[7:]
            member = entries[name]
            if not member.isfile() or member.size != item['size']:
                raise ValueError('descriptor size mismatch')
            if digest not in visited:
                if hashlib.file_digest(archive.extractfile(member), 'sha256').hexdigest() != digest[7:]:
                    raise ValueError('descriptor digest mismatch')
                visited.add(digest)
            return name

        index = read_json('index.json')
        if index.get('schemaVersion') != 2 or not 1 <= len(index.get('manifests', [])) <= 16:
            raise ValueError('bounded OCI image index required')
        if len(index['manifests']) != 1:
            raise ValueError('single candidate tag required')
        registry_digest = index['manifests'][0]['digest']
        images, predicates, statements = [], set(), []

        def image_descriptors(items, depth=0):
            if depth > 4 or len(items) > 16:
                raise ValueError('nested index bound exceeded')
            for item in items:
                value = read_json(descriptor(item))
                if 'manifests' in value:
                    yield from image_descriptors(value['manifests'], depth + 1)
                else:
                    yield item, value

        for item, manifest in image_descriptors(index['manifests']):
            if manifest.get('schemaVersion') != 2:
                raise ValueError('unsupported image manifest')
            config_name = descriptor(manifest['config'])
            layers = manifest.get('layers', [])
            if not layers or len(layers) > 128:
                raise ValueError('bounded layers required')
            for layer in layers:
                layer_name = descriptor(layer)
                if layer.get('mediaType') == 'application/vnd.in-toto+json':
                    statement = read_json(layer_name)
                    predicates.add(statement.get('predicateType'))
                    statements.append(statement)
            if item.get('platform') == {'architecture': 'amd64', 'os': 'linux'}:
                config = read_json(config_name)
                labels = config.get('config', {}).get('Labels', {})
                if labels.get('org.opencontainers.image.revision') != source or labels.get('org.opencontainers.image.version') != version:
                    raise ValueError('image source/version mismatch')
                if labels.get('org.opencontainers.image.source') != 'https://github.com/vpremises/port-office':
                    raise ValueError('image owner mismatch')
                if config['config'].get('User') != '10001:10001' or config['config'].get('WorkingDir') != '/workspace':
                    raise ValueError('runtime identity mismatch')
                images.append({'manifest_digest': item['digest'], 'config_digest': manifest['config']['digest']})
            elif item.get('annotations', {}).get('vnd.docker.reference.type') != 'attestation-manifest':
                raise ValueError('unsupported unaccepted platform')
        if len(images) != 1 or not {'https://spdx.dev/Document', 'https://slsa.dev/provenance/v0.2'} <= predicates:
            raise ValueError('one accepted image, SBOM and provenance required')
        image = images[0]
        for statement in statements:
            if not any(s.get('digest', {}).get('sha256') == image['manifest_digest'][7:]
                       for s in statement.get('subject', [])):
                raise ValueError('attestation subject mismatch')
        blobs = {name for name, member in entries.items() if member.isfile() and name.startswith('blobs/')}
        if blobs != {'blobs/sha256/' + d[7:] for d in visited}:
            raise ValueError('unreferenced blob rejected')
        # Attestations are BuildKit statements; they are not a claim of a Sigstore signature.
        return {'archive_sha256': file_digest(path), 'registry_digest': registry_digest,
                'manifest_digest': image['manifest_digest'],
                'config_digest': image['config_digest'], 'source': source, 'version': version,
                'platform': 'linux/amd64', 'predicates': sorted(predicates)}
