# Reviewed OCI publication

Source completion means the base contract and a default-disabled release path are testable. It does not mean an image with unresolved vulnerabilities has been accepted or published.

1. Merge source checks and record its full main commit SHA.
2. Dispatch `prepare-reviewed-base.yml` with a new semantic version. Docker Bake produces the tested daemon image and OCI archive in the same build. Isolated runtime checks bind the loaded image to the archive.
3. The bounded OCI inspector verifies source/version/owner, non-root identity, one accepted platform, every referenced digest, SBOM and provenance subjects. BuildKit attestations are not Sigstore signatures.
4. Trivy 0.75.0 scans that OCI layout inside a disposable non-root container. It receives no host home, account credentials or Docker socket. Its public database must be at most seven days old. Missing package inventory, end-of-life Debian, HIGH/CRITICAL (including unfixed) and UNKNOWN findings block acceptance.
5. Review the five evidence files: `image.oci.tar`, `scan.json`, `database.json`, `exceptions.json`, `receipt.json`. An exception must identify the exact vulnerability/package/version/severity, reviewer and reason, expire within seven days, and match an observed finding. The default exception list is empty.
6. Only after owner review, set `CONTAINER_SOURCE_APPROVED_SHA` to that exact main SHA and enable `CONTAINER_PUBLICATION_ENABLED`. Dispatch `publish.yml` with the successful candidate run, version and reviewed archive SHA256.
7. Promotion revalidates all evidence, expiry and source before registry authentication. It copies the existing archive with all attestations and preserved digests; it never rebuilds. Existing matching tags are verification-only recovery; differing tags are rejected.
8. Completion requires exact registry digest and anonymous OCI/SBOM/provenance read-back. A newly created private GHCR package needs owner visibility configuration before this can pass. Consumers pin the accepted digest in their own repositories.

The initial platform is `linux/amd64`. Other architectures, language runtimes and application images require separate contracts and acceptance. Publication is manual, repository-scoped and disabled by default; main changes do not publish images.

## Local checks

```sh
python3 -m unittest discover -s tests/release -v
bash -n scripts/release/prepare.sh scripts/release/promote.sh
IMAGE_VERSION=0.1.0 bash scripts/release/prepare.sh /tmp/new-port-office-candidate
```

The candidate directory must be new. Failed scans retain evidence for diagnosis; they do not produce an accepted receipt. Do not use an archive produced before the final source commit as its release candidate.
