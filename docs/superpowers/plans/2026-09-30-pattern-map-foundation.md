# Pattern Map Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the deterministic, testable Pattern Map data model and query layer that all later music-driven combat systems can safely depend on.

**Architecture:** Pattern Map is pure domain data with no Phaser or audio-engine dependency. A validated map describes global timing regions, musical layers, pattern events and cross-layer alignment events. Runtime code queries musical position from an explicit track time supplied by the caller, so later audio synchronization can attach without rewriting the model.

**Tech Stack:** TypeScript 5.9.x, Node test runner, existing Polly simulation/test conventions.

**Spec:** `docs/superpowers/specs/2026-09-30-pattern-map-combat-architecture.md`

## Global Constraints

- Music theory vocabulary must not be required for gameplay.
- Pattern Map data must support global timing plus drums, bass, rhythm guitar, lead/keys and vocals.
- Human-authored/corrected data is authoritative; automatic analysis is advisory only.
- Pattern Map foundation must have no Phaser dependency.
- Pattern Map foundation must have no WebAudio dependency.
- Existing Phase 1/2 combat timings and behavior remain unchanged.
- Generated or imported map data must be rejected when temporal ordering or references are invalid.
- Later systems must be able to query musical state from explicit track time without using `Date.now()`.

## Review Focus

1. **Tempo/meter boundary timestamps:** a query exactly on a region boundary resolves to the new region, never ambiguously to both.
2. **Malformed imported maps:** overlapping timing regions, negative times, missing layers, duplicate IDs and invalid event references fail validation with actionable errors.
3. **Sparse tracks:** a valid map may omit events in a layer or have long rests without query failure.
4. **Cross-layer alignments:** an alignment referencing unknown or temporally incompatible event IDs is rejected.
5. **Floating-point audio time:** millisecond conversion and beat-position queries stay stable around exact beat boundaries.

---

## File Structure

### Create

- `src/music/patternMap/types.ts`
  - canonical Pattern Map types and role names
- `src/music/patternMap/validate.ts`
  - structural and temporal validation
- `src/music/patternMap/query.ts`
  - deterministic time → musical-position and event-window queries
- `src/music/patternMap/load.ts`
  - JSON parsing + validation boundary
- `src/music/patternMap/fixtures.ts`
  - small in-code reference map used by tests and later integration spikes
- `scripts/inspect-pattern-map.ts`
  - human-readable CLI inspection of a Pattern Map JSON file
- `tests/pattern-map-types.test.ts`
- `tests/pattern-map-validation.test.ts`
- `tests/pattern-map-query.test.ts`
- `tests/pattern-map-load.test.ts`
- `tests/pattern-map-inspector.test.ts`

### Do Not Modify

- `src/sim/player.ts`
- `src/sim/enemies.ts`
- `src/sim/world.ts`
- combat constants
- Phaser scene/render code

This phase is deliberately isolated from gameplay.

---

### Task 1: Canonical Pattern Map Types

**Files:**
- Create: `src/music/patternMap/types.ts`
- Create: `tests/pattern-map-types.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `type MusicalRole = 'DRUMS'|'BASS'|'RHYTHM_GUITAR'|'LEAD_KEYS'|'VOCALS'`
  - `interface TempoRegion`
  - `interface MeterRegion`
  - `interface Section`
  - `type PatternEventKind`
  - `interface PatternEvent`
  - `interface LayerMap`
  - `interface AlignmentEvent`
  - `interface PatternMap`

- [ ] **Step 1: Write the failing type/fixture test**

Create a minimal map containing:
- one tempo region at 120 BPM
- one 4/4 meter region
- one section
- all five layer keys
- one drums event
- one lead event
- one alignment referencing both events

Assert the fixture can be constructed using the exported interfaces and the five canonical role strings.

- [ ] **Step 2: Run the focused test**

Run:
```bash
npm test -- tests/pattern-map-types.test.ts
```

Expected: FAIL because `src/music/patternMap/types.ts` does not exist.

- [ ] **Step 3: Implement the canonical types**

Required exact fields:

```ts
export type MusicalRole =
  | 'DRUMS'
  | 'BASS'
  | 'RHYTHM_GUITAR'
  | 'LEAD_KEYS'
  | 'VOCALS';

export interface TempoRegion {
  startMs:number;
  endMs:number;
  bpm:number;
}

export interface MeterRegion {
  startMs:number;
  endMs:number;
  numerator:number;
  denominator:number;
}

export interface Section {
  id:string;
  label:string;
  startMs:number;
  endMs:number;
}

export type PatternEventKind =
  | 'ONSET'
  | 'ACCENT'
  | 'CELL'
  | 'PHRASE_START'
  | 'PHRASE_END'
  | 'FILL'
  | 'REST'
  | 'TENSION'
  | 'RESOLUTION';

export interface PatternEvent {
  id:string;
  role:MusicalRole;
  kind:PatternEventKind;
  startMs:number;
  endMs:number;
  strength:number;
  patternId?:string;
}

export interface LayerMap {
  role:MusicalRole;
  events:PatternEvent[];
}

export interface AlignmentEvent {
  id:string;
  startMs:number;
  endMs:number;
  eventIds:string[];
  label?:string;
}

export interface PatternMap {
  schema:'polly.pattern-map.v1';
  trackId:string;
  durationMs:number;
  tempoRegions:TempoRegion[];
  meterRegions:MeterRegion[];
  sections:Section[];
  layers:Record<MusicalRole,LayerMap>;
  alignments:AlignmentEvent[];
}
```

`strength` is normalized to the inclusive range `0..1`; validation belongs in Task 2.

- [ ] **Step 4: Run focused test**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/music/patternMap/types.ts tests/pattern-map-types.test.ts
git commit -m "feat: define pattern map domain types"
```

---

### Task 2: Structural and Temporal Validation

**Files:**
- Create: `src/music/patternMap/validate.ts`
- Create: `tests/pattern-map-validation.test.ts`

**Interfaces:**
- Consumes: `PatternMap`, `MusicalRole` from Task 1.
- Produces:
  - `interface PatternMapValidationIssue { code:string; path:string; message:string }`
  - `interface PatternMapValidationResult { ok:boolean; issues:PatternMapValidationIssue[] }`
  - `validatePatternMap(map:PatternMap):PatternMapValidationResult`
  - `assertValidPatternMap(map:PatternMap):void`

- [ ] **Step 1: Write failing validation tests**

Cover:
- valid minimal map → `ok === true`
- negative `startMs`
- `endMs <= startMs`
- tempo `bpm <= 0`
- meter numerator/denominator `< 1`
- `strength < 0` or `> 1`
- duplicate event IDs across different layers
- missing one of the five canonical layers
- overlapping tempo regions
- overlapping meter regions
- alignment references unknown event ID
- alignment references events whose time ranges do not intersect the alignment window

Each invalid case must assert at least one stable `code`.

Required codes:
- `NEGATIVE_TIME`
- `INVALID_RANGE`
- `INVALID_BPM`
- `INVALID_METER`
- `INVALID_STRENGTH`
- `DUPLICATE_ID`
- `MISSING_LAYER`
- `OVERLAPPING_REGION`
- `UNKNOWN_EVENT`
- `INCOMPATIBLE_ALIGNMENT`

- [ ] **Step 2: Run focused test**

Expected: FAIL because validation functions do not exist.

- [ ] **Step 3: Implement validation**

Validation must:
- collect all issues rather than throw on the first issue
- keep output order deterministic
- treat touching region boundaries (`previous.endMs === next.startMs`) as valid
- require every event and region to fall within `0..durationMs`
- require exactly one `LayerMap` entry per canonical role

`assertValidPatternMap()` throws one `Error` whose message includes every issue code and path.

- [ ] **Step 4: Run validation tests**

Expected: PASS.

- [ ] **Step 5: Run all Pattern Map tests so far**

```bash
npm test -- tests/pattern-map-types.test.ts tests/pattern-map-validation.test.ts
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/music/patternMap/validate.ts tests/pattern-map-validation.test.ts
git commit -m "feat: validate pattern map structure"
```

---

### Task 3: Deterministic Musical Position Queries

**Files:**
- Create: `src/music/patternMap/query.ts`
- Create: `tests/pattern-map-query.test.ts`

**Interfaces:**
- Consumes: validated `PatternMap`.
- Produces:
  - `interface MusicalPosition`
  - `positionAt(map:PatternMap, trackTimeMs:number):MusicalPosition`
  - `eventsAt(map:PatternMap, role:MusicalRole, trackTimeMs:number, toleranceMs:number):PatternEvent[]`
  - `alignmentsAt(map:PatternMap, trackTimeMs:number, toleranceMs:number):AlignmentEvent[]`

Exact `MusicalPosition` fields:

```ts
export interface MusicalPosition {
  trackTimeMs:number;
  tempoBpm:number;
  meterNumerator:number;
  meterDenominator:number;
  beatIndex:number;
  beatPhase:number;
  sectionId:string|null;
}
```

- [ ] **Step 1: Write failing query tests**

Reference fixture:
- duration `8000`
- 120 BPM from `0..4000`
- 60 BPM from `4000..8000`
- 4/4 across whole track

Assert:
- `positionAt(map, 0).beatIndex === 0`
- at 120 BPM, `500ms` advances exactly one beat
- query at exactly `4000ms` uses the **60 BPM** region
- `beatPhase` is stable near boundaries
- query rejects `trackTimeMs < 0` and `trackTimeMs > durationMs`
- empty/sparse layers return `[]`
- `eventsAt()` honors inclusive tolerance without returning unrelated events
- `alignmentsAt()` returns only alignments inside the requested window

- [ ] **Step 2: Run focused test**

Expected: FAIL.

- [ ] **Step 3: Implement deterministic queries**

Rules:
- region starts are inclusive
- region ends are exclusive, except the map's final `durationMs` endpoint
- tempo changes reset beat integration from the new region boundary
- `beatPhase` is normalized `0 <= phase < 1`, except exact `durationMs` may report the final boundary as phase `0`
- no wall-clock calls
- no `Date.now()`
- no audio-engine reads

- [ ] **Step 4: Run focused test**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/music/patternMap/query.ts tests/pattern-map-query.test.ts
git commit -m "feat: query deterministic musical position"
```

---

### Task 4: Safe JSON Loading Boundary

**Files:**
- Create: `src/music/patternMap/load.ts`
- Create: `tests/pattern-map-load.test.ts`

**Interfaces:**
- Consumes: `PatternMap`, `assertValidPatternMap()`.
- Produces:
  - `parsePatternMapJson(json:string):PatternMap`

- [ ] **Step 1: Write failing loader tests**

Cover:
- valid JSON map returns a `PatternMap`
- malformed JSON throws with prefix `PATTERN_MAP_JSON:`
- wrong schema throws with `PATTERN_MAP_SCHEMA:`
- structurally invalid map throws with `PATTERN_MAP_VALIDATION:`
- arbitrary object missing canonical layers is rejected
- duplicate IDs from imported JSON are rejected

- [ ] **Step 2: Run focused test**

Expected: FAIL.

- [ ] **Step 3: Implement the JSON boundary**

`parsePatternMapJson()` must:
1. parse JSON
2. reject non-object values
3. require `schema === 'polly.pattern-map.v1'`
4. validate
5. return the typed object only after successful validation

Do not silently repair imported data.

- [ ] **Step 4: Run focused test**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/music/patternMap/load.ts tests/pattern-map-load.test.ts
git commit -m "feat: load validated pattern maps"
```

---

### Task 5: Reference Fixture and Human Inspector

**Files:**
- Create: `src/music/patternMap/fixtures.ts`
- Create: `scripts/inspect-pattern-map.ts`
- Create: `tests/pattern-map-inspector.test.ts`
- Create: `data/pattern-maps/reference-grunge-v1.json`

**Interfaces:**
- Consumes:
  - `PatternMap`
  - `parsePatternMapJson()`
  - `positionAt()`
- Produces:
  - `REFERENCE_GRUNGE_PATTERN_MAP:PatternMap`
  - CLI:
    - `node dist/scripts/inspect-pattern-map.js <file> [timeMs]`

- [ ] **Step 1: Write failing reference-fixture tests**

The reference map must contain:
- all five roles
- at least one event per role
- at least one `RESOLUTION`
- at least one alignment containing 3+ event IDs
- two sections
- duration >= 8000ms

Assert the fixture validates.

- [ ] **Step 2: Write failing inspector test**

Given the reference JSON and `timeMs=2000`, assert inspector output includes:
- track ID
- BPM
- meter
- current section
- current beat index
- nearby event IDs grouped by role
- nearby alignment IDs

The test may invoke an exported formatter rather than spawning a process.

Required helper:
```ts
formatPatternMapInspection(map:PatternMap, trackTimeMs:number):string
```

- [ ] **Step 3: Run focused tests**

Expected: FAIL.

- [ ] **Step 4: Implement fixture and inspector**

CLI behavior:
- missing file path → non-zero exit
- invalid map → print validation error and non-zero exit
- omitted `timeMs` → use `0`
- invalid/out-of-range `timeMs` → non-zero exit
- no ANSI requirement

- [ ] **Step 5: Run focused tests**

Expected: PASS.

- [ ] **Step 6: Build TypeScript**

```bash
npm run build
```

Expected: PASS.

- [ ] **Step 7: Inspect the reference map manually**

```bash
node dist/scripts/inspect-pattern-map.js data/pattern-maps/reference-grunge-v1.json 2000
```

Expected: readable musical position plus nearby role events/alignment information.

- [ ] **Step 8: Commit**

```bash
git add \
  src/music/patternMap/fixtures.ts \
  scripts/inspect-pattern-map.ts \
  tests/pattern-map-inspector.test.ts \
  data/pattern-maps/reference-grunge-v1.json

git commit -m "feat: add reference pattern map inspector"
```

---

### Task 6: Foundation Gauntlet and Boundary Contract

**Files:**
- Create: `tests/pattern-map-foundation-gauntlet.test.ts`
- Modify: `README.md` only if the project README already has a developer-tooling section; otherwise create `docs/PATTERN_MAP_FOUNDATION.md`

**Interfaces:**
- Consumes all Tasks 1–5.
- Produces no new runtime API.

- [ ] **Step 1: Write the foundation gauntlet**

Single test must:
1. load the reference JSON through `parsePatternMapJson()`
2. query positions before and after a tempo-region boundary
3. query every musical role
4. query an alignment
5. verify no Pattern Map module imports Phaser
6. verify no Pattern Map module contains `Date.now`
7. verify malformed alignment data is refused

- [ ] **Step 2: Run the complete Pattern Map suite**

```bash
npm test -- tests/pattern-map-*.test.ts
```

Expected: PASS.

- [ ] **Step 3: Run the existing full suite**

```bash
npm test
```

Expected: all existing combat/render/mobile tests remain PASS.

- [ ] **Step 4: Build**

```bash
npm run build
```

Expected: PASS.

- [ ] **Step 5: Document the foundation boundary**

Document:
- Pattern Map is data/query only
- no audio clock yet
- no timing bonuses yet
- no lane changes yet
- no ally behavior yet
- next programme is authoring/analysis tooling

- [ ] **Step 6: Commit**

```bash
git add tests/pattern-map-foundation-gauntlet.test.ts docs/PATTERN_MAP_FOUNDATION.md
git commit -m "test: prove pattern map foundation"
```

---

## Exit Gate

Pattern Map Foundation is complete only when:

1. every valid map has exactly five canonical musical-role layers;
2. malformed temporal/reference data is refused;
3. explicit track time deterministically resolves tempo, meter, beat and section;
4. layer events and cross-layer alignments can be queried without an audio engine;
5. a human can inspect a map from the CLI;
6. the reference Grunge fixture passes validation;
7. the existing Polly combat suite remains unchanged and green;
8. `npm run build` passes.

**This phase does not change gameplay.**

That is deliberate.

The next plan begins the Pattern Map Authoring / Analysis Tool.
