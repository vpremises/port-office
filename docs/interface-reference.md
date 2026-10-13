# Image and build contract

## Debian base

- Source: `images/debian/Dockerfile`.
- Upstream: digest-pinned Debian trixie-slim OCI index; repository source does not execute arbitrary upstream installer scripts.
- Additional OS package: CA certificates, maintained through Debian's package repositories.
- Runtime user/group: numeric 10001; home and working directory `/workspace`; no privileged entrypoint.
- Locale/timezone: `C.UTF-8`, `Etc/UTC`.
- Default command: `/bin/sh`. A product selects its own command.
- Excluded: application code, Python/Node toolchains, provider APIs, service/timer state and secrets.

## Build

`docker-bake.hcl` owns target `base-debian` and default group. `IMAGE_NAMESPACE` defaults to `ghcr.io/vpremises`, `IMAGE_VERSION` to candidate `0.1.0`, and `PLATFORMS` to `linux/amd64`. `SOURCE_REVISION` is an OCI label; owner CI sets the exact GitHub source revision. Local development defaults to `development`.

`local-build.sh [base-debian] [--print|--load]` rejects other targets, extra arguments and push modes. No script regenerates the Bake file from arbitrary directories. Test with `tests/verify-base.sh` after loading the candidate.

## Release

Owner publication is manually dispatched from main, disabled unless `CONTAINER_PUBLICATION_ENABLED=true`, and requires successful main source acceptance. It publishes only the base, requests SBOM/provenance and authenticates with the repository's scoped GitHub token. It refuses existing version tags and ambiguous registry failures. It does not publish product images or cloud toolboxes.

Before enabling the first release, record vulnerability acceptance, reviewed source/version, output digest and provenance expectations. Read back the official registry artifact and evidence after publication. Set a new patch version for changes; preserve accepted immutable digests for rollback. A source candidate and a successful build are not evidence of registry availability.
