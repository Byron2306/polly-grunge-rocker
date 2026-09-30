# Pattern Map Authoring / Analysis Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic local authoring tool that turns stems, rendered WAV audio, MIDI/event hints, and human corrections into validated `polly.pattern-map.v1` files without making automatic analysis authoritative.

**Architecture:** The tool is a local CLI/library layer above the verified Pattern Map foundation. Automatic detectors only emit confidence-scored candidates. A separate authoring session records human accept/reject/adjust decisions, and only accepted/corrected material may be exported through the existing Pattern Map validator. The first implementation supports dependency-free PCM WAV analysis plus structured MIDI/event hints; richer DSP can replace candidate generators later without changing the correction/export contract.

**Tech Stack:** TypeScript 5.9.x, Node test runner, existing Pattern Map modules, Node CLI, dependency-free PCM WAV parsing for v1.

**Spec:** `docs/superpowers/specs/2026-09-30-pattern-map-combat-architecture.md`

## Global Constraints

- Automatic analysis is advisory only; human correction is final authority.
- Final export must pass the existing `validatePatternMap()` / `assertValidPatternMap()` boundary.
- The tool must support all five semantic roles: `DRUMS`, `BASS`, `RHYTHM_GUITAR`, `LEAD_KEYS`, `VOCALS`.
- The tool must be useful without requiring the operator to know advanced theory vocabulary.
- No Phaser or gameplay dependency.
- No cloud or model dependency is required for core authoring.
- V1 audio analysis supports PCM WAV only and must reject unsupported formats explicitly rather than guessing.
- V1 may propose BPM, onset, repeated-cell and cross-layer alignment candidates; phrase, section and meter candidates can also be supplied by human or structured hint input.
- Candidate confidence never turns a suggestion into authoritative Pattern Map data automatically.

## Review Focus

1. **Unsupported/odd WAV inputs:** non-PCM, truncated RIFF chunks, unsupported bit depth or impossible sample metadata must fail with actionable errors rather than emit nonsense candidates.
2. **Silence/noise:** empty or near-silent stems must return no false high-confidence onsets/tempo rather than invent structure.
3. **Tempo ambiguity:** half-time/double-time candidates must remain separate scored suggestions; the tool must not silently choose one as truth.
4. **Human edits outside track bounds:** corrected times must be validated and rejected before export.
5. **Cross-layer candidate explosion:** alignment candidate generation must be deterministic and bounded by explicit tolerance/min-role settings.

---

## File Structure

### Create

- `src/music/authoring/types.ts` — candidate/session/correction contracts.
- `src/music/authoring/wav.ts` — dependency-free PCM WAV metadata/sample reader.
- `src/music/authoring/onsets.ts` — deterministic onset-energy candidate detector.
- `src/music/authoring/tempo.ts` — tempo-candidate scoring from onset intervals.
- `src/music/authoring/align.ts` — cross-layer alignment candidate generator.
- `src/music/authoring/session.ts` — apply human accept/reject/adjust decisions.
- `src/music/authoring/export.ts` — convert approved authoring state to validated Pattern Map.
- `src/music/authoring/inspect.ts` — human-readable candidate/session report.
- `scripts/analyze-pattern-map.mjs` — local CLI wrapper.
- `data/authoring/reference-grunge-authoring.json` — deterministic reference authoring session.
- `tests/pattern-authoring-types.test.ts`
- `tests/pattern-authoring-wav.test.ts`
- `tests/pattern-authoring-analysis.test.ts`
- `tests/pattern-authoring-session.test.ts`
- `tests/pattern-authoring-export.test.ts`
- `tests/pattern-authoring-gauntlet.test.ts`
- `docs/PATTERN_MAP_AUTHORING_TOOL.md`

### Do Not Modify

- combat simulation
- Phaser scenes/rendering
- player/enemy timings
- Pattern Map schema fields unless a separately reviewed schema migration is required

---

### Task 1: Candidate and Authoring Session Contracts

**Files:**
- Create: `src/music/authoring/types.ts`
- Create: `tests/pattern-authoring-types.test.ts`

**Interfaces:**
- Consumes: `MusicalRole`, `PatternEventKind`, `PatternMap` from the foundation.
- Produces:
  - `type AnalysisCandidateKind = 'BPM'|'DOWNBEAT'|'METER'|'ONSET'|'REPEATED_CELL'|'PHRASE'|'SECTION_BOUNDARY'|'ALIGNMENT'`
  - `interface AnalysisCandidate`
  - `interface AuthoringInput`
  - `type CorrectionDecision = 'ACCEPT'|'REJECT'|'ADJUST'`
  - `interface CandidateCorrection`
  - `interface AuthoringSession`

- [ ] **Step 1: Write the failing contract test**

Assert a session can represent:
- one DRUMS WAV input;
- a 120 BPM candidate with confidence `0.8`;
- one ONSET candidate at `2000ms`;
- an ADJUST correction moving that onset to `1985ms`;
- a rejected BPM candidate.

- [ ] **Step 2: Run the focused test**

Run: `npm test -- tests/pattern-authoring-types.test.ts`
Expected: FAIL because `src/music/authoring/types.ts` does not exist.

- [ ] **Step 3: Implement the minimal contracts**

Required candidate fields:
- `id:string`
- `kind:AnalysisCandidateKind`
- `confidence:number` in `0..1`
- `sourceId:string`
- optional `role:MusicalRole`
- optional `startMs:number`, `endMs:number`, `bpm:number`, `meterNumerator:number`, `meterDenominator:number`, `eventKind:PatternEventKind`, `relatedCandidateIds:string[]`, `label:string`

Required correction fields:
- `candidateId:string`
- `decision:CorrectionDecision`
- optional adjusted time/tempo/meter/event fields matching the candidate shape
- optional `note:string`

- [ ] **Step 4: Run focused test**
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/music/authoring/types.ts tests/pattern-authoring-types.test.ts
git commit -m "feat: define pattern authoring session contracts"
```

---

### Task 2: Deterministic PCM WAV Reader

**Files:**
- Create: `src/music/authoring/wav.ts`
- Create: `tests/pattern-authoring-wav.test.ts`

**Interfaces:**
- Produces:
  - `interface PcmWav { sampleRate:number; channels:number; bitsPerSample:16|24|32; frames:number; durationMs:number; mono:Float32Array }`
  - `parsePcmWav(bytes:Uint8Array):PcmWav`

- [ ] **Step 1: Write failing WAV tests**

Generate tiny RIFF/WAVE byte fixtures in-memory. Cover:
- valid mono 16-bit PCM;
- valid stereo downmix to mono;
- truncated RIFF chunk refused;
- non-PCM format refused;
- unsupported bit depth refused;
- zero sample rate/channel count refused.

- [ ] **Step 2: Run focused test**
Expected: FAIL.

- [ ] **Step 3: Implement RIFF chunk walking and PCM normalization**

Do not assume `fmt ` and `data` chunk ordering beyond RIFF rules. Ignore unknown chunks safely, including odd-byte padding.

- [ ] **Step 4: Run focused test**
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/music/authoring/wav.ts tests/pattern-authoring-wav.test.ts
git commit -m "feat: read deterministic pcm wav stems"
```

---

### Task 3: Advisory Onset and Tempo Candidates

**Files:**
- Create: `src/music/authoring/onsets.ts`
- Create: `src/music/authoring/tempo.ts`
- Create: `tests/pattern-authoring-analysis.test.ts`

**Interfaces:**
- `detectOnsetCandidates(wav:PcmWav, sourceId:string, role:MusicalRole, config?:OnsetConfig):AnalysisCandidate[]`
- `inferTempoCandidates(onsets:readonly AnalysisCandidate[], sourceId:string, config?:TempoConfig):AnalysisCandidate[]`

- [ ] **Step 1: Write failing synthetic-analysis tests**

Construct synthetic pulses at 500ms spacing and assert:
- onset candidates appear near the pulse locations within a pinned tolerance;
- silence returns no onsets;
- tempo inference returns a high-ranked ~120 BPM candidate;
- half-time/double-time remain separate candidates when supported by the interval evidence;
- candidate arrays are deterministic across repeated calls.

- [ ] **Step 2: Run focused test**
Expected: FAIL.

- [ ] **Step 3: Implement onset energy-flux scoring**

Use fixed-size analysis windows and local adaptive thresholding. Candidate confidence is normalized and advisory only.

- [ ] **Step 4: Implement tempo histogram scoring from onset intervals**

Clamp candidate BPM search to a documented range, default `40..240`. Preserve multiple plausible candidates rather than silently selecting one.

- [ ] **Step 5: Run focused test**
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/music/authoring/onsets.ts src/music/authoring/tempo.ts tests/pattern-authoring-analysis.test.ts
git commit -m "feat: propose onset and tempo candidates"
```

---

### Task 4: Cross-Layer Alignment Candidates

**Files:**
- Create: `src/music/authoring/align.ts`
- Modify: `tests/pattern-authoring-analysis.test.ts`

**Interfaces:**
- `findAlignmentCandidates(candidates:readonly AnalysisCandidate[], toleranceMs:number, minRoles:number):AnalysisCandidate[]`

- [ ] **Step 1: Add failing alignment tests**

Cover:
- DRUMS/BASS/RHYTHM candidates inside ±40ms form one ALIGNMENT candidate;
- duplicate candidates from the same role do not inflate `minRoles`;
- candidates outside tolerance do not align;
- results remain deterministically ordered;
- large candidate lists remain bounded to unique local clusters rather than pairwise explosion.

- [ ] **Step 2: Run focused test**
Expected: FAIL.

- [ ] **Step 3: Implement deterministic sliding-window clustering**

Alignment confidence is derived from role count, timing spread and member confidence. It remains advisory.

- [ ] **Step 4: Run focused test**
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/music/authoring/align.ts tests/pattern-authoring-analysis.test.ts
git commit -m "feat: propose cross-layer alignment candidates"
```

---

### Task 5: Human Correction Is Authority

**Files:**
- Create: `src/music/authoring/session.ts`
- Create: `tests/pattern-authoring-session.test.ts`

**Interfaces:**
- `resolveCandidate(session:AuthoringSession, candidateId:string):ResolvedCandidate|null`
- `resolvedCandidates(session:AuthoringSession):ResolvedCandidate[]`

- [ ] **Step 1: Write failing correction tests**

Assert:
- no correction means candidate remains advisory and is not export-authoritative;
- ACCEPT preserves candidate values;
- REJECT removes it from resolved authoritative material;
- ADJUST replaces only explicitly supplied fields;
- duplicate corrections for one candidate are refused;
- correction of unknown candidate ID is refused;
- adjusted confidence does not become authority by itself;
- out-of-range negative time remains representable here but is rejected at export, keeping responsibilities separate.

- [ ] **Step 2: Run focused test**
Expected: FAIL.

- [ ] **Step 3: Implement deterministic resolution**

A candidate is export-authoritative only when it has an explicit ACCEPT or ADJUST correction.

- [ ] **Step 4: Run focused test**
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/music/authoring/session.ts tests/pattern-authoring-session.test.ts
git commit -m "feat: make human correction authoritative"
```

---

### Task 6: Validated Pattern Map Export

**Files:**
- Create: `src/music/authoring/export.ts`
- Create: `tests/pattern-authoring-export.test.ts`

**Interfaces:**
- `exportPatternMap(session:AuthoringSession, skeleton:PatternMap):PatternMap`

- [ ] **Step 1: Write failing export tests**

Cover:
- only accepted/adjusted events enter the exported map;
- rejected/unreviewed candidates do not enter the map;
- accepted BPM candidates can replace matching skeleton tempo regions only when explicitly mapped by correction metadata;
- accepted ONSET/FILL/etc. candidates become events on their declared role;
- accepted ALIGNMENT candidates resolve related candidate IDs into exported event IDs;
- adjusted time outside track bounds causes export refusal via the existing Pattern Map validator;
- duplicate exported IDs are refused;
- output validates as `polly.pattern-map.v1`.

- [ ] **Step 2: Run focused test**
Expected: FAIL.

- [ ] **Step 3: Implement export through existing Pattern Map validation**

Do not add a second competing validation system. Build a candidate Pattern Map, call `assertValidPatternMap()`, then return it.

- [ ] **Step 4: Run focused test**
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/music/authoring/export.ts tests/pattern-authoring-export.test.ts
git commit -m "feat: export corrected authoring sessions"
```

---

### Task 7: Inspector and Local CLI Workflow

**Files:**
- Create: `src/music/authoring/inspect.ts`
- Create: `scripts/analyze-pattern-map.mjs`
- Create: `data/authoring/reference-grunge-authoring.json`
- Create: `tests/pattern-authoring-gauntlet.test.ts`
- Create: `docs/PATTERN_MAP_AUTHORING_TOOL.md`

**Interfaces:**
- `formatAuthoringReport(session:AuthoringSession):string`
- CLI modes:
  - `analyze-wav <role> <wav-file> <session-json-out>`
  - `inspect <session-json>`
  - `export <session-json> <skeleton-pattern-map-json> <pattern-map-out>`

- [ ] **Step 1: Write the failing end-to-end gauntlet**

Single gauntlet must prove:
1. a deterministic synthetic DRUMS WAV yields onset/tempo candidates;
2. candidate report shows confidence and role without theory-heavy jargon requirement;
3. unreviewed candidates cannot export themselves into authoritative Pattern Map events;
4. explicit human corrections allow export;
5. cross-layer alignment survives correction/export;
6. final export loads through `parsePatternMapJson()`;
7. authoring modules contain no Phaser imports and no cloud/network dependency.

- [ ] **Step 2: Implement report formatter and CLI wrapper**

The CLI may use Node `fs` in `.mjs`; TypeScript domain modules remain pure enough for unit tests.

- [ ] **Step 3: Create the reference authoring session**

Include all five roles, at least one accepted event per role, at least one rejected suggestion, one adjusted suggestion, and one accepted 3+ role alignment.

- [ ] **Step 4: Document the workflow**

Document the operator loop:

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

State clearly that candidate analysis is not musical truth.

- [ ] **Step 5: Run the authoring suite**

```bash
npm test -- tests/pattern-authoring-*.test.ts
```
Expected: PASS.

- [ ] **Step 6: Run the full regression suite and build**

```bash
npm test
npm run build
```
Expected: all previous combat/render/Pattern Map tests remain green and build passes.

- [ ] **Step 7: Commit**

```bash
git add \
  src/music/authoring/inspect.ts \
  scripts/analyze-pattern-map.mjs \
  data/authoring/reference-grunge-authoring.json \
  tests/pattern-authoring-gauntlet.test.ts \
  docs/PATTERN_MAP_AUTHORING_TOOL.md

git commit -m "test: prove pattern map authoring workflow"
```

---

## Exit Gate

Pattern Map Authoring / Analysis Tool is complete only when:

1. PCM WAV input can produce deterministic advisory onset and tempo candidates;
2. multiple plausible tempo interpretations remain visible rather than silently collapsed;
3. cross-layer alignments can be proposed deterministically;
4. unreviewed automatic candidates cannot become authoritative Pattern Map data;
5. explicit human accept/reject/adjust decisions control export;
6. exported maps pass the existing Pattern Map validator and loader;
7. unsupported audio inputs fail explicitly;
8. a local CLI supports analyze → inspect → correct externally → export workflow;
9. the existing 99-test gameplay/foundation baseline remains green;
10. `npm run build` passes.

This phase does **not** synchronize gameplay to audio yet. The next programme is the authoritative audio clock/runtime sync layer.
