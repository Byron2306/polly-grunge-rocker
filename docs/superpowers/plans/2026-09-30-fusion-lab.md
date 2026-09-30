# Cross-Genre Fusion Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a repeatable evidence pipeline for testing whether guest-genre techniques can enrich a host song without replacing its structure, and export the results as deterministic compatibility data for later runtime systems.

**Architecture:** Fusion Lab is pre-production evidence, not live generative gameplay. Human-authored or Suno-assisted audio experiments are reviewed by ear, annotated against structural context, and converted into a small machine-readable compatibility corpus. Later technique and automatic-opportunity systems consume that corpus; they do not call Suno at runtime.

**Tech Stack:** TypeScript 5.9.x for schema/validation, JSON evidence records, Node test runner, external rendered audio for listening tests.

**Spec:** `docs/superpowers/specs/2026-09-30-pattern-map-combat-architecture.md`

## Global Constraints

- Host genre owns grammar; guest musician owns accent.
- Guest treatment must fill valid structural space rather than dominate the host track.
- Suno may be used as an experimental composition tool but is not a runtime dependency.
- Audio judgments are human-reviewed; generated music is evidence, not authority.
- Compatibility is authored against technique + structural context, not merely genre-name pairs.
- Core compatibility classes are `NATIVE`, `FUSION`, `CLASH`.
- Any experiment used in production must have clear rights/provenance appropriate to its intended use.

## Review Focus

1. **False genre shortcuts:** a genre label alone must never imply every technique from that genre is compatible with every host phrase.
2. **Host hijack:** experiments that sound compelling only because the guest style replaces the host identity must be rejected as fusion evidence.
3. **Density overload:** a compatible technique may become incompatible when used too frequently or for too long.
4. **Tempo/context sensitivity:** the same technique may classify differently across tempo, subdivision and phrase contexts.
5. **Generated-audio provenance:** experimental audio can inform rules without silently becoming a shippable production asset.

---

## File Structure

### Create

- `src/music/fusionLab/types.ts`
- `src/music/fusionLab/validate.ts`
- `tests/fusion-lab-types.test.ts`
- `tests/fusion-lab-validation.test.ts`
- `data/fusion-lab/experiments.json`
- `data/fusion-lab/compatibility.json`
- `docs/music/FUSION_LAB_PROTOCOL.md`
- `docs/music/FUSION_LAB_LISTENING_LOG.md`

### Explicitly Out of Scope

- runtime audio switching;
- live Suno API calls;
- automatic composition;
- final recruit AI;
- final damage tuning;
- final production stems.

---

### Task 1: Define the Experiment Record

**Files:**
- Create: `src/music/fusionLab/types.ts`
- Create: `tests/fusion-lab-types.test.ts`

**Interfaces:**
- Produces:
  - `type FusionCompatibility = 'NATIVE'|'FUSION'|'CLASH'`
  - `type TechniqueId = string`
  - `interface StructuralContext`
  - `interface FusionExperiment`
  - `interface TechniqueCompatibilityRule`

Required `StructuralContext` fields:

```ts
interface StructuralContext {
  hostGenre:string;
  role:'DRUMS'|'BASS'|'RHYTHM_GUITAR'|'LEAD_KEYS'|'VOCALS';
  eventKind:string;
  tempoBpm:number;
  meter:string;
  subdivision:string;
  sectionFunction:string;
}
```

Required experiment fields:

```ts
interface FusionExperiment {
  id:string;
  hostTrackLabel:string;
  guestGenre:string;
  techniqueId:TechniqueId;
  context:StructuralContext;
  sourceKind:'HUMAN'|'SUNO'|'HYBRID';
  audioReference:string;
  compatibility:FusionCompatibility;
  maxDensityPerPhrase:number;
  maxDurationMs:number;
  hostIdentityPreserved:boolean;
  notes:string;
}
```

- [ ] **Step 1: Write a failing construction test**

Create records for:

- Glam host + Black Metal tremolo lead;
- Punk host + Death Metal blast fill;
- Thrash host + Doom bass sustain.

Assert the exact compatibility enum and structural-context fields compile.

- [ ] **Step 2: Run test and confirm failure**

Expected: types do not exist.

- [ ] **Step 3: Implement the types**

No runtime behavior.

- [ ] **Step 4: Run test and confirm PASS**

- [ ] **Step 5: Commit**

```bash
git add src/music/fusionLab/types.ts tests/fusion-lab-types.test.ts
git commit -m "feat: define Fusion Lab evidence types"
```

---

### Task 2: Validate Evidence Records

**Files:**
- Create: `src/music/fusionLab/validate.ts`
- Create: `tests/fusion-lab-validation.test.ts`

**Interfaces:**
- Consumes: `FusionExperiment`.
- Produces:
  - `validateFusionExperiment(experiment:FusionExperiment): string[]`
  - `assertValidFusionExperiment(experiment:FusionExperiment): void`

- [ ] **Step 1: Write failing validation tests**

Reject:

- non-positive tempo;
- negative density;
- non-positive max duration;
- missing technique ID;
- `hostIdentityPreserved === false` when compatibility is `NATIVE` or `FUSION`;
- missing audio reference;
- empty review notes.

- [ ] **Step 2: Run and verify FAIL**

- [ ] **Step 3: Implement deterministic validation**

Collect all issue strings before throwing.

- [ ] **Step 4: Run and verify PASS**

- [ ] **Step 5: Commit**

```bash
git add src/music/fusionLab/validate.ts tests/fusion-lab-validation.test.ts
git commit -m "feat: validate Fusion Lab evidence"
```

---

### Task 3: Write the Listening Protocol

**Files:**
- Create: `docs/music/FUSION_LAB_PROTOCOL.md`

**Interfaces:**
- Consumes: architecture spec.
- Produces: repeatable human review procedure.

- [ ] **Step 1: Define the A/B/C listening protocol**

Every experiment must compare:

- A: host phrase without guest treatment;
- B: guest treatment at a deliberately valid structural opportunity;
- C: same guest treatment deliberately overused or misplaced.

Reviewers answer:

1. Is the host genre still unmistakable?
2. Does the guest technique feel musically intentional?
3. Does the technique improve, decorate or meaningfully contrast the phrase?
4. At what density does it begin to hijack the song?
5. What structural feature made the successful placement work?

- [ ] **Step 2: Define classification rules**

`NATIVE`: broad tolerance inside the tested context.

`FUSION`: effective only with selective placement/density.

`CLASH`: useful only in rare explicitly authored windows or rejected for ordinary runtime use.

- [ ] **Step 3: Document provenance rules**

Generated experiments may inform compatibility metadata without becoming committed/shippable audio automatically.

- [ ] **Step 4: Commit**

```bash
git add docs/music/FUSION_LAB_PROTOCOL.md
git commit -m "docs: define Fusion Lab listening protocol"
```

---

### Task 4: Run the First Six Experiments

**Files:**
- Create: `data/fusion-lab/experiments.json`
- Create: `docs/music/FUSION_LAB_LISTENING_LOG.md`

**Interfaces:**
- Consumes: listening protocol.
- Produces: six reviewed experiment records.

Required first matrix:

1. Glam host + Black Metal tremolo lead.
2. Punk host + Death Metal blast-beat drum fill.
3. Thrash host + Doom bass sustain.
4. Prog host + Punk drum treatment.
5. Grunge host + Black Metal shriek texture.
6. Doom-like host phrase + Glam vocal harmony.

- [ ] **Step 1: Produce A/B/C audio examples for experiment 1**

Use human composition, Suno or a hybrid workflow. Keep the host structure as constant as practical across variants.

- [ ] **Step 2: Review experiment 1 and record evidence**

Record exact structural context, compatibility, maximum useful density, maximum useful duration and notes.

- [ ] **Step 3: Repeat for experiments 2–6**

Each experiment receives its own record and listening-log section.

- [ ] **Step 4: Validate every JSON record**

Expected: all pass `assertValidFusionExperiment()`.

- [ ] **Step 5: Commit metadata and listening notes**

Do not commit externally generated audio unless rights and project policy explicitly permit it.

```bash
git add data/fusion-lab/experiments.json docs/music/FUSION_LAB_LISTENING_LOG.md
git commit -m "research: record first Fusion Lab experiments"
```

---

### Task 5: Distill Runtime Compatibility Rules

**Files:**
- Create: `data/fusion-lab/compatibility.json`
- Extend: `tests/fusion-lab-validation.test.ts`

**Interfaces:**
- Consumes: reviewed experiments.
- Produces: technique compatibility rules for later runtime phases.

Required rule dimensions:

- technique ID;
- compatible role;
- host structural event kind;
- tempo range;
- subdivision affinity;
- section-function affinity;
- compatibility class;
- maximum density;
- maximum duration;
- evidence experiment IDs.

- [ ] **Step 1: Write failing corpus tests**

Assert every compatibility rule:

- cites at least one reviewed experiment;
- has non-empty structural constraints;
- does not infer compatibility from genre pair alone;
- stays within observed density/duration evidence.

- [ ] **Step 2: Run and verify FAIL**

- [ ] **Step 3: Author the smallest rule corpus supported by evidence**

Do not generalize beyond what the six experiments justify.

- [ ] **Step 4: Run Fusion Lab tests**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add data/fusion-lab/compatibility.json tests/fusion-lab-validation.test.ts
git commit -m "research: distill fusion compatibility corpus"
```

---

### Task 6: Fusion Lab Exit Gate

**Files:**
- No new runtime code.

**Interfaces:**
- Produces evidence accepted by later Technique Vocabulary and Fusion Audio Realization phases.

- [ ] **Step 1: Review all six experiments together**

Confirm the experiment set includes at least one convincing `FUSION` result and at least one meaningful rejection or `CLASH` result.

- [ ] **Step 2: Confirm host identity preservation**

A successful experiment must still sound primarily like its host genre.

- [ ] **Step 3: Confirm runtime independence**

No production gameplay code imports Suno, calls a generative service or requires generated audio to construct compatibility rules.

- [ ] **Step 4: Run repository tests and build**

```bash
npm test
npm run build
```

Expected: PASS.

- [ ] **Step 5: Human sign-off**

The phase passes only when the evidence demonstrates that cross-genre contributions can sound intentional rather than merely novel.
