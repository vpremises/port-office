# port-office interface reference

Use the [usage guide](getting-started.md) for the first steps. This reference preserves the current interface details and operational limits. Run command examples from the repository root, after preparing the exact declared dependencies and registered configuration.

## Tagging Rules/Tools

### Image Tag Format
- Docker images are tagged based on their directory paths. The tag format is: `username/dir1-dir2:dir3`, where:
   - `dir1`: App name of the top-level directory set.
    - the ```base``` directory is a little special for depends on other directory.
   - `dir2`: Additional info of the dir1 to dir3.
   - `dir3`: Mainly set the version.

#### bubbles-out.sh
Build bake file script generates Docker image tags based on the directory structure of Dockerfiles, specifically designed for a hierarchical directory structure.

```
./bubbles-out.sh [registry/namespace]
```

After exec the script. Bake file for Github Action out `bocker-bake.hcl` in same directory.

```
cat docker-bake.hcl
```

#### Example Structure

```

├── base
│ ├── alpine
│ │ └── v1.0 (-> ghcr.io/vpremises/base-alpine:v1)
│ │   └── Dockerfile
│ └── debian
│   └── v1.0
│     └── Dockerfile
└── app
  ├── service1
  │ └── v1.0
  │   └── Dockerfile
  └── service2
    └── v1.0
      └── Dockerfile
```

### Local build

If want to build a specific file locally, run the following command:

```
./local-build.sh [target name in hcl file]
```

## Distribution configuration

The planned image namespace is `ghcr.io/vpremises`, configurable through `IMAGE_NAMESPACE` in the bake file. No images have been published to that namespace by this migration. Build and authorize the base images before dependent Frappe images. The checked-in Dockerfiles are historical build examples; a full image build and vulnerability assessment remain prerequisites for release.

Publication is manual and disabled unless `CONTAINER_PUBLICATION_ENABLED` is explicitly set to `true`. Configure `CONTAINER_REGISTRY`, `CONTAINER_NAMESPACE`, and narrowly scoped `CONTAINER_USERNAME` / `CONTAINER_TOKEN` secrets only after approving the registry destination and package permissions. Source pushes do not publish images. Consumers set the image reference to an available immutable image digest before deployment.
