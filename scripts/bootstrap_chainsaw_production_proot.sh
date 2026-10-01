#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ASSET_ROOT="${FUSION_INSTRUMENT_ROOT:-$HOME/fusion-instruments}"
BUILD_ROOT="${FUSION_BUILD_ROOT:-$HOME/.cache/polly-fusion-build}"
HELPER_VENV="$HOME/.cache/polly-fusion-bootstrap-venv"
RESET=0

if [[ "${1:-}" == "--reset" ]]; then
  RESET=1
fi

say() { printf '\n==> %s\n' "$*"; }
fail() { printf '\nBOOTSTRAP FAILED: %s\n' "$*" >&2; exit 2; }

if (( RESET )); then
  say "Resetting only Fusion production assets/cache"
  rm -rf "$ASSET_ROOT" "$BUILD_ROOT" "$HELPER_VENV"
  rm -f /tmp/chainsaw-*.wav
fi

say "Installing bootstrap dependencies"
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y \
  ca-certificates curl git unzip bzip2 p7zip-full \
  python3 python3-venv python3-pip ffmpeg sox

say "Building/checking pinned sfizz renderer"
export FUSION_BUILD_ROOT="$BUILD_ROOT"
bash "$REPO_ROOT/scripts/setup_fusion_production_proot.sh"
export PATH="$HOME/.local/bin:$PATH"
command -v sfizz_render >/dev/null 2>&1 || fail "sfizz_render not found"

say "Preparing asset directories"
mkdir -p "$ASSET_ROOT"/{guitar,bass,drums,ir}

say "Installing Growlybass v1.002"
GB_ZIP="$ASSET_ROOT/bass/Karoryfer.Growlybass.v1.002.zip"
GB_DIR="$ASSET_ROOT/bass/Growlybass"
if [[ ! -f "$GB_DIR/Growlybass/growlybass_angry.sfz" ]]; then
  rm -rf "$GB_DIR"
  curl -fL --retry 4 --retry-delay 2 \
    -o "$GB_ZIP" \
    https://github.com/sfzinstruments/karoryfer.growlybass/releases/download/v1.002/Karoryfer.Growlybass.v1.002.zip
  unzip -q "$GB_ZIP" -d "$GB_DIR"
  rm -f "$GB_ZIP"
fi
GB_SFZ="$GB_DIR/Growlybass/growlybass_angry.sfz"
[[ -f "$GB_SFZ" ]] || fail "Growlybass SFZ missing after install"

say "Installing Salamander Drumkit mappings + original sample archive"
SD_DIR="$ASSET_ROOT/drums/Salamander"
if [[ ! -d "$SD_DIR/.git" ]]; then
  rm -rf "$SD_DIR"
  git clone --depth 1 https://github.com/endolith/Salamander-Drumkit.git "$SD_DIR"
fi
SD_ARCHIVE="$SD_DIR/salamanderDrumkit.tar.bz2"
if [[ ! -f "$SD_DIR/OH/kick_OH_P_1.wav" ]]; then
  curl -fL --retry 4 --retry-delay 2 \
    -o "$SD_ARCHIVE" \
    https://archive.org/download/SalamanderDrumkit/salamanderDrumkit.tar.bz2
  tar -xjf "$SD_ARCHIVE" -C "$SD_DIR"
  rm -f "$SD_ARCHIVE"
fi
SD_SFZ="$SD_DIR/Salamander Drumkit.sfz"
[[ -f "$SD_SFZ" ]] || fail "Salamander SFZ missing after install"
[[ -f "$SD_DIR/OH/kick_OH_P_1.wav" ]] || fail "Salamander WAV samples missing after install"

say "Installing gdown helper in isolated bootstrap venv"
if [[ ! -x "$HELPER_VENV/bin/gdown" ]]; then
  rm -rf "$HELPER_VENV"
  python3 -m venv "$HELPER_VENV"
  "$HELPER_VENV/bin/pip" -q install --upgrade pip gdown
fi

say "Downloading Metal GTX"
MG_DIR="$ASSET_ROOT/guitar/Metal-GTX"
if ! find "$MG_DIR" -type f -iname '*.sfz' -print -quit 2>/dev/null | grep -q .; then
  rm -rf "$MG_DIR"
  mkdir -p "$MG_DIR"
  MG_ARCHIVE="$ASSET_ROOT/guitar/metal-gtx.download"
  rm -f "$MG_ARCHIVE"
  "$HELPER_VENV/bin/gdown" \
    1FurY3_x_tog_56irX1VDNyRCUt5JD7bO \
    -O "$MG_ARCHIVE"
  BYTES="$(stat -c %s "$MG_ARCHIVE" 2>/dev/null || echo 0)"
  (( BYTES > 500000000 )) || fail "Metal GTX download is suspiciously small (${BYTES} bytes)"
  7z x -y "$MG_ARCHIVE" -o"$MG_DIR" >/dev/null
  rm -f "$MG_ARCHIVE"
fi
MG_SFZ="$(find "$MG_DIR" -type f -iname '*.sfz' -print -quit)"
[[ -n "$MG_SFZ" && -f "$MG_SFZ" ]] || fail "Metal GTX SFZ missing after extraction"

say "Preparing Metal GTX sfizz compatibility patches"
MG_INDIVIDUAL="$MG_DIR/UI_METAL-GTX/Programs/Individual Patchs"
[[ -d "$MG_INDIVIDUAL" ]] || fail "Metal GTX individual patch directory missing"
if [[ ! -e "$MG_INDIVIDUAL/Samples" ]]; then
  ln -s ../../Samples "$MG_INDIVIDUAL/Samples"
fi
PYTHONPATH="$REPO_ROOT" python3 -m fusion_lab.metal_gtx_compat \
  --individual-root "$MG_INDIVIDUAL"
MG_CLEAN="$MG_INDIVIDUAL/SFIZZ_CLEAN"
[[ -L "$MG_CLEAN/Samples" ]] || fail "Metal GTX compatibility sample link missing"
[[ -f "$MG_CLEAN/METAL-GTX_Full/Mute_Down.sfz" ]] || fail "Metal GTX clean mute patch missing"
[[ -f "$MG_CLEAN/METAL-GTX_XTracking/Sus_Up.sfz" ]] || fail "Metal GTX clean xtracking patch missing"

say "Writing persistent environment helper"
cat > "$HOME/.fusion-production-env" <<EOF
export FUSION_INSTRUMENT_ROOT="$ASSET_ROOT"
export FUSION_METAL_GTX_CLEAN_ROOT="$MG_CLEAN"
export PATH="$HOME/.local/bin:\$PATH"
EOF

say "Verifying installed stack"
printf 'sfizz_render: %s\n' "$(command -v sfizz_render)"
printf 'Growlybass:   %s\n' "$GB_SFZ"
printf 'Salamander:  %s\n' "$SD_SFZ"
printf 'Metal GTX:   %s\n' "$MG_SFZ"
printf 'Metal clean: %s\n' "$MG_CLEAN"
printf 'Asset root:  %s\n' "$ASSET_ROOT"
printf '\nMetal GTX clean SFZ files:\n'
find "$MG_CLEAN" -type f -iname '*.sfz' -print | head -20

printf '\nBOOTSTRAP PASS\n'
printf 'Next shell command: source %s\n' "$HOME/.fusion-production-env"
printf 'NOTE: cabinet IR and final amp model remain authenticity-controlled setup steps.\n'
