# Use the Debian base

Docker Engine and Docker Buildx are required. No adjacent repository or private registry is needed.

```sh
./local-build.sh base-debian --print
SOURCE_REVISION=$(git rev-parse HEAD) ./local-build.sh base-debian --load
./tests/verify-base.sh
```

Local builds never push. `IMAGE_NAMESPACE`, `IMAGE_VERSION`, `SOURCE_REVISION` and `PLATFORMS` are Bake variables; inspect the rendered definition before building. The initial supported acceptance platform is linux/amd64. Use one platform with `--load`.

A consuming product adds its own files, runtime and startup policy. After an official release, obtain and verify its registry digest, then use `FROM ghcr.io/vpremises/base-debian@sha256:<accepted-digest>`. There is no published digest for this source candidate. Application-specific root build steps may precede a final `USER 10001:10001`; credentials and operational data never belong in image layers.

The isolated checks cover non-root identity, work directory, CA bundle, locale/timezone, package-cache cleanup, absence of bundled product/provider tools, read-only startup and ordinary ephemeral work-directory writes. They do not claim real cloud-account or product compatibility.

See [image contract](interface-reference.md) and [owner responsibilities](base-image-purpose.ja.md).
