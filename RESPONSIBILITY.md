# Responsibility and source completion

`port-office` owns independently maintained Docker OS base images. The initial product is a minimal Debian trixie image: CA trust, UTF-8/UTC, UID/GID 10001 and `/workspace`. Docker Bake is the canonical build definition.

Products own language runtimes, application packages, startup, persistence, provider authentication and deployment. This repository does not provision cloud accounts, deploy product sites or run maintenance timers. Historical Python/Node/product/toolbox sources remain in Git history rather than the supported tree.

## Completion criteria

- One canonical Dockerfile/Bake target, digest-pinned upstream and explicit platform contract.
- Disposable runtime tests for identity, filesystem expectations and absence of application runtimes.
- Source CI performs builds/tests without registry writes.
- A reviewed OCI candidate includes tested image bytes, digest-bound SBOM/provenance and a fresh fail-closed vulnerability scan.
- Manual, disabled-by-default promotion copies those exact bytes, rejects different existing tags and verifies anonymous registry read-back.
- Public usage, security reporting, Apache-2.0 licensing and third-party notices are maintained in this repository.

[Release acceptance](docs/reviewed-publication.md) describes the evidence and gates. Source tests establish these mechanisms; an actual candidate must independently satisfy them before distribution is called complete. Production deployment and unresolved upstream vulnerabilities are separate acceptance tasks, never silently treated as completed source work.
