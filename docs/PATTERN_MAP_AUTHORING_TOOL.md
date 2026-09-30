# Pattern Map Authoring / Analysis Tool

The authoring tool turns local audio analysis plus explicit human review into validated `polly.pattern-map.v1` data.

Its governing rule is simple:

> **Confidence is not authority.**

Automatic analysis only creates suggestions. A candidate becomes export-authoritative only after an explicit `ACCEPT` or `ADJUST` correction. `REJECT` removes it from authoritative material. Unreviewed candidates never enter the exported Pattern Map.

## Operator loop

```text
stems/audio/MIDI hints
      ↓
advisory candidates + confidence
      ↓
listen / inspect / adjust
      ↓
explicit ACCEPT / REJECT / ADJUST
      ↓
validated deterministic Pattern Map
```

## V1 capabilities

- dependency-free PCM WAV parsing for 16/24/32-bit integer PCM
- mono downmix for multi-channel WAV input
- deterministic onset-energy candidates
- multiple tempo candidates, including visible half-time/double-time interpretations
- deterministic cross-layer alignment candidates
- all five semantic roles: DRUMS, BASS, RHYTHM_GUITAR, LEAD_KEYS, VOCALS
- human correction sessions
- export through the existing Pattern Map validator
- local CLI workflow

V1 does not claim to solve phrase, section or meter inference from arbitrary audio automatically. Those may be supplied or corrected by humans or structured hint input. Automatic analysis remains advisory.

## Build first

```bash
npm run build
```

## Analyze a WAV stem

```bash
node scripts/analyze-pattern-map.mjs \
  analyze-wav DRUMS path/to/drums.wav /tmp/drums-session.json
```

This creates a session with onset and tempo suggestions. It does not create authoritative gameplay events.

## Inspect a session

```bash
node scripts/analyze-pattern-map.mjs \
  inspect data/authoring/reference-grunge-authoring.json
```

The report shows role, candidate kind, confidence and current review state in plain operator-facing language.

## Review

Edit the session's `corrections` array. Each reviewed candidate gets exactly one decision:

- `ACCEPT` — use the candidate as reviewed;
- `REJECT` — exclude it;
- `ADJUST` — use it with explicitly corrected fields.

Tempo or meter candidates only replace a skeleton timing region when the correction includes `targetRegionIndex`. This prevents a high-confidence tempo guess from silently rewriting track truth.

## Export

```bash
node scripts/analyze-pattern-map.mjs \
  export \
  data/authoring/reference-grunge-authoring.json \
  data/pattern-maps/reference-grunge-v1.json \
  /tmp/reviewed-pattern-map.json
```

The export path uses the existing Pattern Map validation boundary. Invalid times, duplicate event IDs, broken alignment references or other malformed structure are refused rather than repaired silently.

## Boundary

This tool is local authoring infrastructure. It has no Phaser dependency, no gameplay authority, and no required cloud/model dependency. Audio-clock synchronization, combat timing bonuses, recruit learning and fusion realization remain later programme phases.
