# port-office

Independent Docker base images maintained by vPremises. Products consume an accepted immutable image digest and own their application dependencies, startup, configuration and account permissions.

[目的・責務と独立運用](docs/base-image-purpose.ja.md) · [Usage](docs/getting-started.md) · [Image contract](docs/interface-reference.md)

## Current catalog

| Target | Purpose | Upstream | Runtime | Execution | Status |
| --- | --- | --- | --- | --- | --- |
| `base-debian` | Minimal Debian OS base | `debian:trixie-slim`, pinned multi-platform index in Dockerfile | No Python/Node/compiler or provider CLI | UID/GID 10001, `/workspace`, CA trust, UTF-8, UTC | 0.1.0 source candidate; registry publication not enabled |

`images/debian/Dockerfile` owns the image contract; `docker-bake.hcl` is the single build definition. The initial acceptance platform is `linux/amd64`. Other platforms and runtime images require their own acceptance before they enter this catalog.

```sh
./local-build.sh base-debian --print
./local-build.sh base-debian --load
./tests/verify-base.sh
```

Tests use disposable containers without network, host mounts, cloud credentials or the Docker socket inside the image. Source CI builds and tests without publishing images.

## Distribution and maintenance

The destination is `ghcr.io/vpremises/base-debian:<version>`. The [reviewed publication path](docs/reviewed-publication.md) prepares one OCI candidate, tests its image, verifies digest-bound SBOM/provenance, and requires a fresh vulnerability scan. Manual promotion copies the same reviewed archive without rebuilding, rejects conflicting tags and requires anonymous registry read-back. Publication remains disabled by default through `CONTAINER_PUBLICATION_ENABLED` and requires approval of the exact main source SHA and archive SHA256. Repository-scoped `GITHUB_TOKEN` is used only after verification. No image is currently declared published.

[Responsibility and source completion](RESPONSIBILITY.md) separates the completed source mechanisms from acceptance of a particular release candidate.

Pin the upstream digest and record output digests. Debian package updates are obtained during builds, so source equality alone does not imply identical image bytes. Review a new candidate and use a new image version when patching. Consumers update by digest in their own repositories; old tags are not overwritten.

## Removed historical scope

The previous mixed Python/Node bases, Frappe/Traefik products and OpenTofu/Terraformer toolboxes are removed from the current build and source tree. Their definitions remain in Git history at `627188c94e3dd3a04729960fe9b0c12c9d0e1acc`. They are not supported base images. The obsolete Bake generator is removed; edit the canonical Bake definition directly.

This purpose decision supersedes the Terraformer target in issue #2: its failing provider integration is retired here, not repaired. Required import capabilities belong in a separately selected tool/product owner. Docker Bake remains the selected backend; Bazel is not introduced.

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [License](LICENSE) · [Notices](NOTICE)
