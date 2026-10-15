#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/../.."
candidate_dir=${1:?candidate directory required}
expected=${2:?owner-reviewed OCI archive SHA256 required}
version=${3:?version required}
source=${4:?source required}
[[ "$expected" =~ ^[a-f0-9]{64}$ && "$source" =~ ^[a-f0-9]{40}$ ]] || exit 2
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || exit 2
test "${CONTAINER_PUBLICATION_ENABLED:-false}" = true
test "${CONTAINER_SOURCE_APPROVED_SHA:-}" = "$source"
test "${GITHUB_REPOSITORY:-}" = vpremises/port-office
case "${GITHUB_REF:-}" in
  refs/heads/main) ;; # Existing explicitly reviewed manual promotion.
  "refs/tags/v$version")
    test "${GITHUB_EVENT_NAME:-}" = push
    test "${GITHUB_RUN_ATTEMPT:-}" = 1
    ;; # Retries require explicit read-back; they cannot repeat promotion.
  *) exit 2 ;;
esac
test "$(git rev-parse HEAD)" = "$source"
python3 scripts/release/candidate.py verify --archive "$candidate_dir/image.oci.tar" \
  --scan "$candidate_dir/scan.json" --database "$candidate_dir/database.json" \
  --exceptions "$candidate_dir/exceptions.json" --receipt "$candidate_dir/receipt.json" \
  --source "$source" --version "$version" --expected-sha256 "$expected"
digest=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["registry_digest"])' "$candidate_dir/receipt.json")
image="ghcr.io/vpremises/base-debian:$version"
auth_dir=$(mktemp -d)
trap 'rm -rf -- "$auth_dir"' EXIT
printf '%s' '{"auths":{}}' > "$auth_dir/anonymous.json"
printf '%s' "${GH_TOKEN:?repository-scoped publication credential required}" | \
  skopeo login --authfile "$auth_dir/auth.json" --username "${GITHUB_ACTOR:?}" --password-stdin ghcr.io
if skopeo inspect --authfile "$auth_dir/auth.json" --raw "docker://$image" > "$auth_dir/existing.json" 2> "$auth_dir/error"; then
  # Recovery is verify-only. An already published matching candidate is never rewritten.
  test "$(skopeo manifest-digest "$auth_dir/existing.json")" = "$digest"
else
  if ! grep -Eq 'manifest unknown|name unknown|no such manifest' "$auth_dir/error"; then
    printf '%s\n' 'Registry absence could not be verified; promotion refused.' >&2
    exit 1
  fi
  skopeo copy --all --preserve-digests --authfile "$auth_dir/auth.json" \
    "oci-archive:$candidate_dir/image.oci.tar" "docker://$image"
fi
skopeo inspect --authfile "$auth_dir/auth.json" --raw "docker://$image" > "$auth_dir/published.json"
test "$(skopeo manifest-digest "$auth_dir/published.json")" = "$digest"
# First registration may require the owner to make the GHCR package public.
# A failure here is not reported as completed distribution; rerun verifies existing bytes only.
skopeo copy --all --preserve-digests --authfile "$auth_dir/anonymous.json" \
  "docker://ghcr.io/vpremises/base-debian@$digest" "oci-archive:$auth_dir/readback.tar"
python3 - "$auth_dir/readback.tar" "$source" "$version" "$digest" <<'PY'
import sys
sys.path.insert(0, 'scripts/release')
from oci_candidate import inspect_archive
readback = inspect_archive(sys.argv[1], sys.argv[2], sys.argv[3])
assert readback['registry_digest'] == sys.argv[4], 'anonymous read-back differs'
print('Promoted exact candidate; anonymous OCI/SBOM/provenance read-back verified')
PY
