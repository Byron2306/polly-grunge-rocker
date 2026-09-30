#!/usr/bin/env bash
set -euo pipefail

SFIZZ_VERSION="1.2.3"
PREFIX="${FUSION_PRODUCTION_PREFIX:-$HOME/.local}"
SRC_ROOT="${FUSION_BUILD_ROOT:-$HOME/.cache/polly-fusion-build}"
SFIZZ_SRC="$SRC_ROOT/sfizz-$SFIZZ_VERSION"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y git cmake ninja-build build-essential pkg-config libsndfile1-dev libsamplerate0-dev ffmpeg sox ca-certificates

mkdir -p "$SRC_ROOT" "$PREFIX/bin"

if command -v sfizz_render >/dev/null 2>&1; then
  echo "sfizz_render=$(command -v sfizz_render)"
  exit 0
fi

if [ ! -d "$SFIZZ_SRC/.git" ]; then
  git clone --recursive --branch "$SFIZZ_VERSION" https://github.com/sfztools/sfizz.git "$SFIZZ_SRC"
else
  git -C "$SFIZZ_SRC" fetch --tags
  git -C "$SFIZZ_SRC" checkout "$SFIZZ_VERSION"
  git -C "$SFIZZ_SRC" submodule update --init --recursive
fi

cmake -S "$SFIZZ_SRC" -B "$SFIZZ_SRC/build" \
  -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DSFIZZ_RENDER=ON \
  -DSFIZZ_JACK=OFF \
  -DSFIZZ_TESTS=OFF \
  -DSFIZZ_DEMOS=OFF \
  -DBUILD_TESTING=OFF
cmake --build "$SFIZZ_SRC/build" --target sfizz_render

BIN="$(find "$SFIZZ_SRC/build" -type f -name sfizz_render -perm -111 | head -n 1 || true)"
if [ -z "$BIN" ]; then
  echo "PRODUCTION_SETUP_FAILED: sfizz_render not found after build" >&2
  exit 2
fi
install -m 0755 "$BIN" "$PREFIX/bin/sfizz_render"

if [ ! -x "$PREFIX/bin/sfizz_render" ]; then
  echo "PRODUCTION_SETUP_FAILED: renderer install missing" >&2
  exit 2
fi

echo "sfizz_version=$SFIZZ_VERSION"
echo "sfizz_render=$PREFIX/bin/sfizz_render"
echo "NOTE: third-party SFZ/sample libraries are NOT downloaded by this script."
echo "Set FUSION_INSTRUMENT_ROOT to your manually acquired instrument-library root."
