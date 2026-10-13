# Upstream multi-platform index resolved on 2026-10-13.
FROM debian:trixie-slim@sha256:a29215f6a35e51e22adffa17f89e9d2ef06214e64a2bad10d765c46aea49f11f

ARG IMAGE_VERSION=development
ARG SOURCE_REVISION=development
LABEL org.opencontainers.image.title="port-office Debian base" \
      org.opencontainers.image.description="Minimal Debian OS base with CA trust and non-root execution" \
      org.opencontainers.image.source="https://github.com/vpremises/port-office" \
      org.opencontainers.image.version="${IMAGE_VERSION}" \
      org.opencontainers.image.revision="${SOURCE_REVISION}"

ENV LANG=C.UTF-8 TZ=Etc/UTC
RUN set -eux; \
    apt-get update; \
    apt-get upgrade -y --no-install-recommends; \
    apt-get install -y --no-install-recommends ca-certificates; \
    rm -rf /var/lib/apt/lists/*; \
    groupadd --gid 10001 runtime; \
    useradd --uid 10001 --gid runtime --home-dir /workspace --no-create-home --shell /usr/sbin/nologin runtime; \
    install -d --owner runtime --group runtime --mode 0755 /workspace

USER 10001:10001
WORKDIR /workspace
CMD ["/bin/sh"]
