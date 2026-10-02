#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$HOME/.fusion-production-env"

INSTRUMENTS="$ROOT/fusion_lab/data/production/instruments.v5.json"
TONES="$ROOT/fusion_lab/data/production/tone-profiles-v5.json"
PROFILES="$ROOT/fusion_lab/data/music_dna/genres"
OUT="$ROOT/fusion_lab/out/host-003-pit-v5"
PHONE="$HOME/storage/downloads/ChainsawTest"
ACTION="${1:-isolated}"
AMP_URI='http://guitarix.sourceforge.net/plugins/gx_amp#GUITARIX'

cd "$ROOT"
mkdir -p "$OUT" "$PHONE"

common=(
  --out "$OUT"
  --instrument-config "$INSTRUMENTS"
  --tone-config "$TONES"
  --profile-root "$PROFILES"
  --seed 1988
)

require_guitarix() {
  if ! command -v lv2file >/dev/null 2>&1; then
    echo "V5 REFUSE: lv2file is not installed" >&2
    exit 2
  fi
  if ! command -v lv2ls >/dev/null 2>&1; then
    echo "V5 REFUSE: lv2ls is not installed" >&2
    exit 2
  fi
  if ! lv2ls | grep -Fxq "$AMP_URI"; then
    echo "V5 REFUSE: Guitarix amp LV2 plugin is not installed: $AMP_URI" >&2
    exit 2
  fi
}

case "$ACTION" in
  analyze)
    python -m fusion_lab.music_dna.chainsaw_v5 analyze "${common[@]}"
    ;;

  isolated)
    require_guitarix
    python -m fusion_lab.music_dna.chainsaw_v5 isolated \
      "${common[@]}" --sample-rate 48000 --sfizz-render sfizz_render
    if [[ -f "$OUT/CHAINSAW_DIPLOMACY_V5_ISOLATED_GUITARS.wav" ]]; then
      cp "$OUT/CHAINSAW_DIPLOMACY_V5_ISOLATED_GUITARS.wav" \
        "$PHONE/CHAINSAW_DIPLOMACY_V5_ISOLATED_GUITARS.wav"
      echo "ISOLATED GUITAR READY FOR HUMAN REVIEW"
      echo "$PHONE/CHAINSAW_DIPLOMACY_V5_ISOLATED_GUITARS.wav"
    fi
    ;;

  review-pass)
    python -m fusion_lab.music_dna.chainsaw_v5 review \
      --gate "$OUT/v5-gate.json" --state PASS
    ;;

  review-adjust)
    python -m fusion_lab.music_dna.chainsaw_v5 review \
      --gate "$OUT/v5-gate.json" --state ADJUST
    ;;

  review-refuse)
    python -m fusion_lab.music_dna.chainsaw_v5 review \
      --gate "$OUT/v5-gate.json" --state REFUSE
    ;;

  full)
    require_guitarix
    python -m fusion_lab.music_dna.chainsaw_v5 full \
      "${common[@]}" --gate "$OUT/v5-gate.json" \
      --sample-rate 48000 --sfizz-render sfizz_render
    cp "$OUT/full/CHAINSAW_DIPLOMACY_INSTRUMENTAL.wav" \
      "$PHONE/CHAINSAW_DIPLOMACY_PIT_V5.wav"
    echo "V5 FULL RENDER COMPLETE"
    echo "$PHONE/CHAINSAW_DIPLOMACY_PIT_V5.wav"
    ;;

  *)
    echo "usage: $0 {analyze|isolated|review-pass|review-adjust|review-refuse|full}" >&2
    exit 2
    ;;
esac
