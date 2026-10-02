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
