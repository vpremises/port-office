#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
target=${1:-base-debian}
case "$target" in
  base-debian) ;;
  *) printf '%s\n' 'Usage: ./local-build.sh [base-debian] [--print|--load]' >&2; exit 2 ;;
esac
mode=${2:---load}
case "$mode" in
  --print|--load) ;;
  *) printf '%s\n' 'Local mode must be --print or --load; publication uses the owner workflow.' >&2; exit 2 ;;
esac
[[ $# -le 2 ]] || exit 2
exec docker buildx bake --file docker-bake.hcl "$target" "$mode"
