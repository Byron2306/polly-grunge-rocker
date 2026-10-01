#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$HOME/.fusion-production-env"

INSTRUMENTS="$ROOT/fusion_lab/data/production/instruments.proot.json"
TONES="$ROOT/fusion_lab/data/production/tone-profiles.json"
OUT="$ROOT/fusion_lab/out/host-003-pit-v3"
PHONE="$HOME/storage/downloads/ChainsawTest"

cd "$ROOT"
mkdir -p "$PHONE"
rm -rf "$OUT"

printf '\n=========================================\n'
printf ' CHAINSAW DIPLOMACY PIT V3: REAL RIFF PATH\n'
printf '=========================================\n\n'

python -m fusion_lab production-check \
  --instrument-config "$INSTRUMENTS" \
  --tone-config "$TONES" \
  --sfizz-render sfizz_render \
  --sample-rate 48000

python -m fusion_lab render-host003-production \
  --out "$OUT" \
  --instrument-config "$INSTRUMENTS" \
  --tone-config "$TONES" \
  --seed 1988 \
  --sample-rate 48000 \
  --sfizz-render sfizz_render

cp "$OUT/CHAINSAW_DIPLOMACY_INSTRUMENTAL.wav" \
   "$PHONE/CHAINSAW_DIPLOMACY_PIT_V3.wav"
cp "$OUT/production-manifest.json" \
   "$PHONE/CHAINSAW_DIPLOMACY_PIT_V3_manifest.json"

printf '\n=========================================\n'
printf ' PIT V3 RENDER COMPLETE\n'
printf '=========================================\n'
ls -lh "$OUT/CHAINSAW_DIPLOMACY_INSTRUMENTAL.wav"
printf 'PHONE MIX: %s\n' "$PHONE/CHAINSAW_DIPLOMACY_PIT_V3.wav"
printf 'MANIFEST:  %s\n' "$PHONE/CHAINSAW_DIPLOMACY_PIT_V3_manifest.json"
