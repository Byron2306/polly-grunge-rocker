# Pattern Map Foundation

The Pattern Map foundation is the deterministic musical truth layer for Polly Grunge Rocker.

It is intentionally data/query only.

## What it provides

- canonical five-role grammar: drums, bass, rhythm guitar, lead/keys and vocals
- tempo, meter and section regions
- per-role pattern events
- cross-layer alignment events
- structural and temporal validation
- safe JSON loading
- explicit track-time queries for beat, section, nearby role events and alignments
- a reference Grunge Pattern Map
- a human-readable inspector CLI

## Boundary

This phase does **not** provide:

- an audio clock
- WebAudio synchronization
- combat timing bonuses
- musical lane changes
- ally behavior
- recruit learning
- coherence scoring
- fusion techniques

Pattern Map modules must not depend on Phaser, WebAudio or wall-clock time such as `Date.now()`.
Callers provide explicit track time. Later audio systems will attach to that boundary without rewriting the domain model.

## Why this exists

Everything later depends on one deterministic answer to:

> At this exact point in the track, what is happening musically?

The foundation makes that answer queryable and testable before gameplay begins reacting to it.

## Reference inspector

After a production build:

```bash
node scripts/inspect-pattern-map.mjs data/pattern-maps/reference-grunge-v1.json 2000
```

The reference map should report the current tempo, meter, section, beat, events for all five roles, and the `full-band-lock-1` alignment at 2000ms.

## Next programme

The next programme is Pattern Map authoring/analysis tooling. Automatic analysis remains advisory. Human-authored or human-corrected musical truth stays authoritative.
