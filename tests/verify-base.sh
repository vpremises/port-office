#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
image="${IMAGE_NAMESPACE:-ghcr.io/vpremises}/base-debian:${IMAGE_VERSION:-0.1.0}"
# No network, credentials, host mount, daemon socket or writable root filesystem.
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges:true "$image" sh -eu -c '
  test "$(id -u)" = 10001
  test "$(id -g)" = 10001
  test "$(pwd)" = /workspace
  test -s /etc/ssl/certs/ca-certificates.crt
  test "$LANG" = C.UTF-8
  test "$TZ" = Etc/UTC
  test "$(date +%z)" = +0000
  test -z "$(find /var/lib/apt/lists -type f -print -quit)"
  for executable in node npm python3 cc gcc terraform terraformer docker sudo; do
    if command -v "$executable" >/dev/null 2>&1; then exit 1; fi
  done
'
# Confirm the non-root work directory is writable in an ordinary ephemeral container.
docker run --rm --network none --cap-drop ALL \
  --security-opt no-new-privileges:true "$image" sh -eu -c \
  'touch /workspace/fixture; test -f /workspace/fixture'
printf '%s\n' 'Debian base acceptance passed (isolated containers only).'
