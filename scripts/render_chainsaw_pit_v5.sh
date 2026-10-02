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
CAPS_SO='/usr/lib/ladspa/caps.so'

cd "$ROOT"
mkdir -p "$OUT" "$PHONE"

common=(
  --out "$OUT"
  --instrument-config "$INSTRUMENTS"
  --tone-config "$TONES"
  --profile-root "$PROFILES"
  --seed 1988
)

require_caps() {
  if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "V5 REFUSE: ffmpeg is not installed" >&2
    exit 2
  fi
  if [[ ! -f "$CAPS_SO" ]]; then
    echo "V5 REFUSE: CAPS LADSPA plugin is not installed: $CAPS_SO" >&2
    exit 2
  fi
  if command -v analyseplugin >/dev/null 2>&1; then
    if ! analyseplugin "$CAPS_SO" AmpVTS 2>/dev/null | grep -Fq 'Plugin Label: "AmpVTS"'; then
      echo "V5 REFUSE: CAPS AmpVTS plugin is unavailable" >&2
      exit 2
    fi
    if ! analyseplugin "$CAPS_SO" CabinetIV 2>/dev/null | grep -Fq 'Plugin Label: "CabinetIV"'; then
      echo "V5 REFUSE: CAPS CabinetIV plugin is unavailable" >&2
      exit 2
    fi
  fi
}

diagnose_articulation_wavs() {
  echo "--- V5 articulation WAV diagnostics ---" >&2
  local found=0
  for side in rhythm_guitar_L rhythm_guitar_R; do
    local dir="$OUT/articulations/$side"
    [[ -d "$dir" ]] || continue
    for wav in "$dir"/*.wav; do
      [[ -e "$wav" ]] || continue
      found=1
      echo "[$side] $(basename "$wav")" >&2
      ls -lh "$wav" >&2 || true
      if command -v ffprobe >/dev/null 2>&1; then
        ffprobe -v error \
          -show_entries stream=codec_name,sample_rate,channels:format=format_name,duration,size \
          -of default=noprint_wrappers=1 "$wav" >&2 || \
          echo "FFPROBE_INVALID_AUDIO: $wav" >&2
      fi
    done
  done
  if [[ "$found" -eq 0 ]]; then
    echo "NO_ARTICULATION_WAVS_FOUND" >&2
  fi
  echo "--- end diagnostics ---" >&2
}

case "$ACTION" in
  analyze)
    python -m fusion_lab.music_dna.chainsaw_v5 analyze "${common[@]}"
    ;;

  isolated)
    require_caps
    if ! python -m fusion_lab.music_dna.chainsaw_v5 isolated \
      "${common[@]}" --sample-rate 48000 --sfizz-render sfizz_render; then
      diagnose_articulation_wavs
      exit 1
    fi
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
    require_caps
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
