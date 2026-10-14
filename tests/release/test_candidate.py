import copy
import datetime
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts/release'))
from oci_candidate import inspect_archive
from runtime_archive import convert, verify_saved_image
from security_summary import summary
from vulnerability_policy import accept_scan

SOURCE = 'a' * 40
NOW = datetime.datetime(2026, 10, 13, tzinfo=datetime.timezone.utc)
DATABASE = {'UpdatedAt': '2026-10-13T00:00:00Z'}
SCAN = {'SchemaVersion': 2, 'Metadata': {'OS': {'Family': 'debian', 'Name': '13', 'EOSL': False}},
        'Results': [{'Class': 'os-pkgs', 'Type': 'debian', 'Packages': [{'Name': 'libc6'}], 'Vulnerabilities': []}]}


def archive_fixture(path, mutate=None):
    files = {'oci-layout': b'{"imageLayoutVersion":"1.0.0"}'}
    def blob(value, media):
        data = value if isinstance(value, bytes) else json.dumps(value).encode()
        digest = hashlib.sha256(data).hexdigest()
        files['blobs/sha256/' + digest] = data
        return {'digest': 'sha256:' + digest, 'size': len(data), 'mediaType': media}
    layer_data = b'synthetic fixture layer; never executed'
    config = blob({'rootfs': {'type': 'layers', 'diff_ids': ['sha256:' + hashlib.sha256(layer_data).hexdigest()]},
        'config': {'User': '10001:10001', 'WorkingDir': '/workspace', 'Labels': {
        'org.opencontainers.image.revision': SOURCE, 'org.opencontainers.image.version': '0.1.0',
        'org.opencontainers.image.source': 'https://github.com/vpremises/port-office'}}}, 'application/vnd.oci.image.config.v1+json')
    layer = blob(layer_data, 'application/vnd.oci.image.layer.v1.tar')
    image = blob({'schemaVersion': 2, 'config': config, 'layers': [layer]}, 'application/vnd.oci.image.manifest.v1+json')
    statements = [blob({'predicateType': kind, 'subject': [{'digest': {'sha256': image['digest'][7:]}}]},
                       'application/vnd.in-toto+json') for kind in ['https://spdx.dev/Document', 'https://slsa.dev/provenance/v0.2']]
    attestation = blob({'schemaVersion': 2, 'config': blob({}, 'application/vnd.oci.image.config.v1+json'), 'layers': statements},
                       'application/vnd.oci.image.manifest.v1+json')
    image['platform'] = {'architecture': 'amd64', 'os': 'linux'}
    attestation['annotations'] = {'vnd.docker.reference.type': 'attestation-manifest'}
    nested = blob({'schemaVersion': 2, 'manifests': [image, attestation]}, 'application/vnd.oci.image.index.v1+json')
    files['index.json'] = json.dumps({'schemaVersion': 2, 'manifests': [nested]}).encode()
    if mutate:
        mutate(files)
    with tarfile.open(path, 'w') as archive:
        for name, data in files.items():
            member = tarfile.TarInfo(name); member.size = len(data)
            archive.addfile(member, io.BytesIO(data))


class CandidateTests(unittest.TestCase):
    def test_security_summary_preserves_failure_and_absent_scan_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            self.assertIn('security acceptance remains incomplete', summary(folder, 'failure'))
            (folder / 'scan.json').write_text(json.dumps(SCAN))
            text = summary(folder, 'failure')
            self.assertIn('Candidate gate: not accepted', text)
            self.assertIn('| HIGH | 0 |', text)
            (folder / 'receipt.json').write_text('{}')
            self.assertIn('Candidate gate: accepted', summary(folder, 'success'))

    def test_runtime_import_preserves_exact_config_and_layers_without_attestations(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / 'candidate.tar'
            runtime = Path(directory) / 'runtime.tar'
            archive_fixture(candidate)
            identity = convert(candidate, runtime, SOURCE, '0.1.0')
            self.assertEqual(verify_saved_image(candidate, runtime, SOURCE, '0.1.0'), identity)
            with tarfile.open(candidate) as original, tarfile.open(runtime) as imported:
                manifest = json.load(imported.extractfile('manifest.json'))[0]
                self.assertEqual(manifest['Config'], 'blobs/sha256/' + identity['config_digest'][7:])
                self.assertEqual(manifest['RepoTags'], ['ghcr.io/vpremises/base-debian:0.1.0'])
                for name in [manifest['Config'], *manifest['Layers']]:
                    self.assertEqual(imported.extractfile(name).read(), original.extractfile(name).read())
                self.assertEqual(len(imported.getmembers()), 2 + len(manifest['Layers']))
            with self.assertRaises(ValueError): convert(candidate, runtime, SOURCE, '0.1.0')

    def test_runtime_verification_rejects_loaded_config_or_layer_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / 'candidate.tar'
            runtime = Path(directory) / 'runtime.tar'
            archive_fixture(candidate)
            convert(candidate, runtime, SOURCE, '0.1.0')
            with tarfile.open(runtime) as original:
                files = {member.name: original.extractfile(member).read() for member in original}
            manifest = json.loads(files['manifest.json'])[0]
            for name in [manifest['Config'], manifest['Layers'][0]]:
                changed = Path(directory) / ('changed-' + str(len(name)) + '.tar')
                with tarfile.open(changed, 'w') as target:
                    for path, data in files.items():
                        if path == name: data = b'changed'
                        member = tarfile.TarInfo(path); member.size = len(data)
                        target.addfile(member, io.BytesIO(data))
                with self.assertRaises(ValueError): verify_saved_image(candidate, changed, SOURCE, '0.1.0')

    def test_runtime_import_rejects_unverified_candidate_before_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / 'candidate.tar'
            runtime = Path(directory) / 'runtime.tar'
            archive_fixture(candidate)
            with self.assertRaises(ValueError): convert(candidate, runtime, 'b' * 40, '0.1.0')
            self.assertFalse(runtime.exists())

    def inspect(self, mutate=None, source=SOURCE):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'candidate.tar'; archive_fixture(path, mutate)
            return inspect_archive(path, source, '0.1.0')

    def test_accepts_bound_image_and_attestations(self):
        self.assertEqual(self.inspect()['platform'], 'linux/amd64')

    def test_rejects_changed_source(self):
        with self.assertRaises(ValueError): self.inspect(source='b' * 40)

    def test_rejects_traversal(self):
        with self.assertRaises(ValueError): self.inspect(lambda files: files.update({'../token': b'not-a-secret'}))

    def test_rejects_digest_tampering(self):
        def tamper(files):
            name = next(n for n in files if n.startswith('blobs/'))
            files[name] = b'changed'
        with self.assertRaises(ValueError): self.inspect(tamper)

    def test_rejects_unreferenced_blob(self):
        data = b'unrelated data'
        with self.assertRaises(ValueError): self.inspect(lambda files: files.update({'blobs/sha256/' + hashlib.sha256(data).hexdigest(): data}))

    def test_accepts_observed_inventory(self):
        self.assertEqual(accept_scan(SCAN, DATABASE, [], NOW)['observations'], 0)

    def test_stale_future_and_unobserved_scans_are_rejected(self):
        for database in [{'UpdatedAt': '2026-10-01T00:00:00Z'}, {'UpdatedAt': '2026-10-14T00:00:00Z'}]:
            with self.assertRaises(ValueError): accept_scan(SCAN, database, [], NOW)
        for changed in [{'SchemaVersion': 2}, {**SCAN, 'Results': []}]:
            with self.assertRaises(ValueError): accept_scan(changed, DATABASE, [], NOW)

    def test_unfixed_high_is_rejected_and_only_exact_expiring_exception_works(self):
        scan = copy.deepcopy(SCAN)
        scan['Results'][0]['Vulnerabilities'] = [{'VulnerabilityID': 'CVE-2026-12345', 'PkgName': 'libc6',
                                                'InstalledVersion': '1', 'Severity': 'HIGH'}]
        with self.assertRaises(ValueError): accept_scan(scan, DATABASE, [], NOW)
        exception = {'vulnerability': 'CVE-2026-12345', 'package': 'libc6', 'version': '1', 'severity': 'HIGH',
                     'expires': '2026-10-15', 'reviewer': 'fixture reviewer', 'reason': 'synthetic policy test'}
        self.assertEqual(accept_scan(scan, DATABASE, [exception], NOW)['reviewed_exceptions'], 1)
        for change in [{'version': '2'}, {'expires': '2026-10-12'}, {'expires': '2026-10-21'}]:
            with self.assertRaises(ValueError): accept_scan(scan, DATABASE, [{**exception, **change}], NOW)


if __name__ == '__main__':
    unittest.main()
