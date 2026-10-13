# port-office

Prepare container build inputs and consistent image tags for a reviewed distribution destination.

## What you can do

- Inspect build and tag-generation definitions.
- Choose the registered image namespace before publication.

## Current scope

Container publication remains disabled. Images have not been built or vulnerability-scanned as part of the documentation review.

Package distribution is not activated by this documentation. Use the checked-in source and the declared dependency versions; published availability must be verified separately.

## Getting started

Start with the implementation and examples linked below. Review registered configuration and prerequisites before running a command that writes state or contacts a service.

## Examples and interface details

## Distribution configuration

The planned image namespace is `ghcr.io/vpremises`, configurable through `IMAGE_NAMESPACE` in the bake file. No images have been published to that namespace by this migration. Build and authorize the base images before dependent Frappe images. The checked-in Dockerfiles are historical build examples; a full image build and vulnerability assessment remain prerequisites for release.

Publication is manual and disabled unless `CONTAINER_PUBLICATION_ENABLED` is explicitly set to `true`. Configure `CONTAINER_REGISTRY`, `CONTAINER_NAMESPACE`, and narrowly scoped `CONTAINER_USERNAME` / `CONTAINER_TOKEN` secrets only after approving the registry destination and package permissions. Source pushes do not publish images. Consumers set the image reference to an available immutable image digest before deployment.

## Documentation and source

[Interface reference](docs/interface-reference.md)

[Usage guide](docs/getting-started.md)

[Contributing](CONTRIBUTING.md) · [Security reporting](SECURITY.md) · [License](LICENSE) · [Attribution notices](NOTICE)

## Defined image catalog

These 11 entries describe checked-in Docker Bake targets, not released or supported images. Registry availability, immutable digests, full builds and vulnerability assessment must be verified before use. The namespace can be overridden with `IMAGE_NAMESPACE`; the table shows its checked-in default.

| Bake target | Planned image tag | Group | Dockerfile | Validation status |
| --- | --- | --- | --- | --- |
| `base-alpine-v3_19-p3_11_7-n20` | `ghcr.io/vpremises/base-alpine:v3.19-p3.11.7-n20` | `default` | [./base/alpine/v3.19-p3.11.7-n20/Dockerfile](./base/alpine/v3.19-p3.11.7-n20/Dockerfile) | ビルド定義あり・配布未確認 |
| `base-alpine-v3_19-p3_11_7-n18` | `ghcr.io/vpremises/base-alpine:v3.19-p3.11.7-n18` | `default` | [./base/alpine/v3.19-p3.11.7-n18/Dockerfile](./base/alpine/v3.19-p3.11.7-n18/Dockerfile) | ビルド定義あり・配布未確認 |
| `base-alpine-v3_18-p3_11_7-n18` | `ghcr.io/vpremises/base-alpine:v3.18-p3.11.7-n18` | `default` | [./base/alpine/v3.18-p3.11.7-n18/Dockerfile](./base/alpine/v3.18-p3.11.7-n18/Dockerfile) | ビルド定義あり・配布未確認 |
| `base-debian-bookworm-p3_11_7-n18` | `ghcr.io/vpremises/base-debian:bookworm-p3.11.7-n18` | `default` | [./base/debian/bookworm-p3.11.7-n18/Dockerfile](./base/debian/bookworm-p3.11.7-n18/Dockerfile) | ビルド定義あり・配布未確認 |
| `iac-tofu-v1_6_0` | `ghcr.io/vpremises/iac-tofu:v1.6.0` | `iac` | [./iac/tofu/v1.6.0/Dockerfile](./iac/tofu/v1.6.0/Dockerfile) | ビルド定義あり・配布未確認 |
| `iac-tofuformer-gcp-5_13_0` | `ghcr.io/vpremises/iac-tofuformer:gcp-5.13.0` | `iac` | [./iac/tofuformer/gcp-5.13.0/Dockerfile](./iac/tofuformer/gcp-5.13.0/Dockerfile) | 既知のimport不具合 (#2) |
| `iac-tofuformer-gcp-4_59_0` | `ghcr.io/vpremises/iac-tofuformer:gcp-4.59.0` | `iac` | [./iac/tofuformer/gcp-4.59.0/Dockerfile](./iac/tofuformer/gcp-4.59.0/Dockerfile) | 旧回避候補・未受入 |
| `traefik-v3_0_0-beta5-alpine` | `ghcr.io/vpremises/traefik-v3.0.0-beta5:alpine` | `frappe` | [./traefik/v3.0.0-beta5/alpine/Dockerfile](./traefik/v3.0.0-beta5/alpine/Dockerfile) | ビルド定義あり・配布未確認 |
| `traefik-v3_0_0-beta5-debian` | `ghcr.io/vpremises/traefik-v3.0.0-beta5:debian` | `frappe` | [./traefik/v3.0.0-beta5/debian/Dockerfile](./traefik/v3.0.0-beta5/debian/Dockerfile) | ビルド定義あり・配布未確認 |
| `frappe-v15_11_0-alpine` | `ghcr.io/vpremises/frappe-v15.11.0:alpine` | `frappe` | [./frappe/v15.11.0/alpine/Dockerfile](./frappe/v15.11.0/alpine/Dockerfile) | ビルド定義あり・配布未確認 |
| `frappe-v15_11_0-debian` | `ghcr.io/vpremises/frappe-v15.11.0:debian` | `frappe` | [./frappe/v15.11.0/debian/Dockerfile](./frappe/v15.11.0/debian/Dockerfile) | ビルド定義あり・配布未確認 |

Inspect a target without building or publishing:

```sh
docker buildx bake --print iac-tofu-v1_6_0
```

The Google Terraformer 5.13.0 target remains affected by [issue #2](https://github.com/vpremises/port-office/issues/2); the 4.59.0 variant is a historical workaround, not a current compatibility guarantee. The upstream importer is archived, so a maintained replacement and isolated acceptance are needed before activation. [Bazel adoption #4](https://github.com/vpremises/port-office/issues/4) remains a separate build-backend decision.
