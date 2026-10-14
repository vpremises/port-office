#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/../.."
[[ "${IMAGE_VERSION:-0.1.0}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || exit 2
candidate_dir=${1:?absolute new candidate directory required}
case "$candidate_dir" in /*) ;; *) exit 2 ;; esac
test ! -e "$candidate_dir"
mkdir -m 0700 -- "$candidate_dir"
export IMAGE_VERSION=${IMAGE_VERSION:-0.1.0}
export SOURCE_REVISION=${SOURCE_REVISION:-$(git rev-parse HEAD)}
export OCI_ARCHIVE="$candidate_dir/image.oci.tar"
export PLATFORMS=linux/amd64
docker buildx bake --allow "fs.write=$candidate_dir" --file docker-bake.hcl candidate
python3 scripts/release/runtime_archive.py convert "$OCI_ARCHIVE" "$candidate_dir/runtime.tar" "$SOURCE_REVISION" "$IMAGE_VERSION"
docker load --input "$candidate_dir/runtime.tar"
rm -- "$candidate_dir/runtime.tar"
./tests/verify-base.sh
docker save --output "$candidate_dir/tested-runtime.tar" "ghcr.io/vpremises/base-debian:$IMAGE_VERSION"
python3 scripts/release/runtime_archive.py verify "$OCI_ARCHIVE" "$candidate_dir/tested-runtime.tar" "$SOURCE_REVISION" "$IMAGE_VERSION"
rm -- "$candidate_dir/tested-runtime.tar"
# Compare the runtime imported from exact OCI blobs with the verified candidate.
python3 - "$OCI_ARCHIVE" "$SOURCE_REVISION" "$IMAGE_VERSION" <<'PY'
import json, subprocess, sys
import pathlib, tarfile, hashlib
sys.path.insert(0, 'scripts/release')
from oci_candidate import inspect_archive
identity = inspect_archive(*sys.argv[1:])
image = 'ghcr.io/vpremises/base-debian:' + sys.argv[3]
# Runtime config and every uncompressed layer were verified above. Docker IDs
# may identify a converted manifest, so they are not a portable config assertion.
print(json.dumps(identity))
# Trivy's OCI reader consumes a layout directory, not an OCI archive.
layout = pathlib.Path(sys.argv[1]).parent / 'layout'
layout.mkdir()
with tarfile.open(sys.argv[1]) as archive:
    for member in archive:
        name = member.name.removeprefix('./')
        target = layout / name
        if member.isdir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with archive.extractfile(member) as source, target.open('xb') as out:
            while block := source.read(1024 * 1024):
                out.write(block)
        if name.startswith('blobs/'):
            with target.open('rb') as stream:
                assert hashlib.file_digest(stream, 'sha256').hexdigest() == target.name
PY
tools_dir=$(mktemp -d)
trap 'rm -rf -- "$tools_dir"' EXIT
python3 scripts/release/install_trivy.py "$tools_dir/trivy"
# Scanner has the OCI input and public DB only; no host home, profiles, credentials or daemon socket.
mkdir -m 0777 "$candidate_dir/cache" "$candidate_dir/report"
docker run --rm --read-only --user "$(id -u):$(id -g)" \
  --cap-drop ALL --security-opt no-new-privileges:true --pids-limit 64 --memory 2g \
  --mount "type=bind,src=$tools_dir/trivy,dst=/tools/trivy,readonly" \
  --mount "type=bind,src=$candidate_dir/layout,dst=/input/layout,readonly" \
  --mount "type=bind,src=$candidate_dir/cache,dst=/cache" \
  --mount "type=bind,src=$candidate_dir/report,dst=/report" \
  --tmpfs /tmp:rw,nosuid,nodev,size=1g \
  --entrypoint /tools/trivy "ghcr.io/vpremises/base-debian:$IMAGE_VERSION" \
  image --quiet --input /input/layout --cache-dir /cache --scanners vuln \
  --list-all-pkgs --exit-on-eol 1 --timeout 10m --format json --output /report/scan.json
cp "$candidate_dir/cache/db/metadata.json" "$candidate_dir/database.json"
cp "$candidate_dir/report/scan.json" "$candidate_dir/scan.json"
cp scripts/release/vulnerability-exceptions.json "$candidate_dir/exceptions.json"
python3 scripts/release/candidate.py record \
  --archive "$OCI_ARCHIVE" --scan "$candidate_dir/scan.json" \
  --database "$candidate_dir/database.json" --exceptions "$candidate_dir/exceptions.json" \
  --source "$SOURCE_REVISION" --version "$IMAGE_VERSION" --receipt "$candidate_dir/receipt.json"
rm -rf -- "$candidate_dir/cache" "$candidate_dir/report" "$candidate_dir/layout"
