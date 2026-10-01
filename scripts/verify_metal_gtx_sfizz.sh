#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$HOME/.fusion-production-env"

CLEAN="${FUSION_METAL_GTX_CLEAN_ROOT:?FUSION_METAL_GTX_CLEAN_ROOT not set}"
MIDI_ROOT="$ROOT/fusion_lab/out/host-003-pit-v2/midi"
OUT="${TMPDIR:-/tmp}/metal-gtx-sfizz-verify"
mkdir -p "$OUT"

MUTE_MIDI="$MIDI_ROOT/rhythm_L_Mute_Down.mid"
SUS_MIDI="$MIDI_ROOT/rhythm_L_Sus_Down.mid"

[[ -f "$MUTE_MIDI" ]] || { echo "METAL_GTX_VERIFY_MISSING_MIDI: $MUTE_MIDI" >&2; exit 2; }
[[ -f "$SUS_MIDI" ]] || { echo "METAL_GTX_VERIFY_MISSING_MIDI: $SUS_MIDI" >&2; exit 2; }

render_and_peak() {
  local art="$1"
  local midi="$2"
  local wav="$OUT/${art}.wav"

  sfizz_render \
    --use-eot \
    --sfz "$CLEAN/METAL-GTX_Full/${art}.sfz" \
    --midi "$midi" \
    --wav "$wav" \
    --samplerate 48000 >/dev/null 2>&1

  ffmpeg -hide_banner -nostats \
    -i "$wav" \
    -af astats=metadata=1:reset=0 \
    -f null - 2>&1 \
    | awk '/Peak level dB:/ {v=$NF} END {print v}'
}

mute_peak="$(render_and_peak Mute_Down "$MUTE_MIDI")"
sus_peak="$(render_and_peak Sus_Down "$SUS_MIDI")"

printf 'Mute_Down peak dB: %s\n' "$mute_peak"
printf 'Sus_Down  peak dB: %s\n' "$sus_peak"

python3 - "$mute_peak" "$sus_peak" <<'PY'
import sys
mute = float(sys.argv[1])
sus = float(sys.argv[2])
threshold = -60.0
if mute <= threshold:
    raise SystemExit(f"METAL_GTX_VERIFY_REFUSE: Mute_Down is effectively silent ({mute:.2f} dB)")
if sus <= threshold:
    raise SystemExit(f"METAL_GTX_VERIFY_REFUSE: Sus_Down is effectively silent ({sus:.2f} dB)")
print("METAL GTX SFIZZ VERIFY PASS")
PY
