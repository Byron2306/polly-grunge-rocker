# Generic Fusion Expression Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the Headless Fusion Lab with a deterministic generic expression engine and implement THRASH CHIMERA as the first compound multi-recruit experiment, preserving the laws `STYLE ≠ FUNCTION`, `TRAIT ≠ TECHNIQUE ≠ FUNCTION ≠ ROLE`, and `SHARED CLOCK ≠ SHARED RHYTHMIC IDENTITY`.

**Architecture:** Keep host composition immutable and treat performer identity, style traits, techniques, functions, opportunities, local context and realized expressions as separate data contracts. A generic experiment compiler resolves declared expressions into new immutable compositions, enforces frozen-dimension authority, and reuses the existing MIDI/render pipeline. THRASH CHIMERA is authored entirely through this generic machinery, not through experiment-specific branching in the engine.

**Tech Stack:** Python 3.11+, existing `fusion_lab` dataclasses, `mido`, Python `unittest`, FluidSynth CLI, existing headless renderer.

**Spec:** `docs/superpowers/specs/2026-09-30-generic-fusion-expression-engine-design.md`

## Global Constraints

- **STYLE ≠ FUNCTION** is non-negotiable.
- **TRAIT ≠ TECHNIQUE ≠ FUNCTION ≠ ROLE** is non-negotiable.
- **SHARED CLOCK ≠ SHARED RHYTHMIC IDENTITY** is non-negotiable.
- Host tempo, meter, section boundaries, phrase boundaries, host harmonic progression and host riff identity remain host authority unless an experiment explicitly declares otherwise.
- Performer slots do not equal semantic functions; multiple performers may overlap a role family.
- Experiments must declare frozen dimensions and mutated dimensions before generation.
- Undeclared mutation leakage must be refused.
- Single-recruit and compound experiments must use the same generic engine.
- THRASH CHIMERA control host is approximately `190 BPM`, `4/4`, E-centered aggressive minor/chromatic Thrash.
- Core workflow remains deterministic, headless, Termux/Proot-compatible, and cloud-free.
- Existing Headless Fusion Lab interfaces and Pattern Map schema remain backward-compatible.

## Review Focus

1. **Identity collapse:** tests must prove the same technique can serve multiple functions and the same function can be realized by multiple techniques.
2. **Mutation leakage in compound variants:** F/G must not silently alter host tempo, meter, section boundaries, phrase boundaries or riff identity.
3. **Role-local cycle drift:** Djent bass local cycles must preserve the global tick clock and hit authored convergence targets.
4. **Overlapping performer ownership:** Doom guitar and Prog synth must coexist without one evicting the other solely because both map to a broad lead/keys family.
5. **Bad-placement validity:** G must differ from F by placement/density policy, not by host song substitution or undeclared pitch/tempo changes.

---

## File Structure

### Create

- `fusion_lab/expression_model.py` — performer, trait, technique, function, opportunity, context and expression contracts.
- `fusion_lab/expression_engine.py` — generic expression validation, placement and transformation engine.
- `fusion_lab/thrash_chimera.py` — deterministic Thrash control host plus THRASH CHIMERA performer/opportunity/variant definitions.
- `fusion_lab/tests/test_expression_model.py`
- `fusion_lab/tests/test_expression_engine.py`
- `fusion_lab/tests/test_thrash_chimera.py`
- `fusion_lab/data/experiments/exp-002-thrash-chimera.json`

### Modify

- `fusion_lab/model.py` — only if minimal shared metadata hooks are needed; preserve existing constructor compatibility.
- `fusion_lab/midi_io.py` — support additional overlay/percussion tracks if required without changing deterministic signatures for existing experiments.
- `fusion_lab/cli.py` — add generic experiment and THRASH CHIMERA commands.
- `fusion_lab/render.py` — only if compound variants need additional role-layer stem naming; preserve current commands.
- `fusion_lab/tests/test_gauntlet.py` — extend full lab gauntlet.
- `docs/FUSION_LAB.md` — document generic engine and THRASH CHIMERA workflow.

### Generated, Never Hand-Edited

- `fusion_lab/out/exp-002/{A,B,C,D,E,F,G}/**`

### Do Not Modify

- existing Pattern Map schema;
- combat simulation;
- Phaser runtime;
- Host 001 canonical files/manifests.

---

### Task 1: Independent Expression Domain Contracts

**Files:**
- Create: `fusion_lab/expression_model.py`
- Create: `fusion_lab/tests/test_expression_model.py`

**Interfaces:**
- Produces:
  - `StyleTrait(id:str, description:str)`
  - `Technique(id:str, description:str)`
  - `Function(id:str, description:str)`
  - `Performer(id:str, name:str, role_affinities:tuple[str,...], trait_ids:tuple[str,...], technique_ids:tuple[str,...], timbral_preferences:tuple[str,...]=(), local_cycle:tuple[int,...]|None=None)`
  - `Opportunity(id:str, section_id:str, start_tick:int, end_tick:int, eligible_functions:tuple[str,...], eligible_role_families:tuple[str,...], density_budget:float, convergence_tick:int|None=None)`
  - `LocalContext(section_id:str, harmony:str, bpm:int, meter:str, phrase_position:str, active_performers:tuple[str,...], density:float, register_occupancy:tuple[int,int]|None=None)`
  - `ExpressionRequest(performer_id:str, trait_id:str, technique_id:str, function_id:str, opportunity_id:str, role_family:str, rhythmic_policy:str, harmonic_policy:str, timbral_policy:str, density_policy:str)`
  - `ResolvedExpression(...provenance fields..., events:tuple[NoteEvent,...])`

- [ ] **Step 1: Write failing separation tests**

Assert:
- one technique object can be referenced by two different functions;
- one function can be realized by two different techniques;
- performer role affinity does not constrain function identity;
- opportunity ranges require `start_tick < end_tick` and density budget in `0..1`;
- performer local cycle values are positive integers and do not encode a second tempo.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_expression_model -v`
Expected: FAIL because the module does not exist.

- [ ] **Step 3: Implement immutable contracts and validation**

Use frozen dataclasses and tuples. Do not encode genre labels as function rules.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_expression_model -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/expression_model.py fusion_lab/tests/test_expression_model.py
git commit -m "feat: define generic fusion expression model"
```

---

### Task 2: Generic Expression Engine and Frozen-Dimension Authority

**Files:**
- Create: `fusion_lab/expression_engine.py`
- Create: `fusion_lab/tests/test_expression_engine.py`
- Modify: `fusion_lab/model.py` only if required for non-breaking metadata access.

**Interfaces:**
- Consumes Task 1 contracts plus existing `HostComposition`.
- Produces:
  - `resolve_expression(host:HostComposition, request:ExpressionRequest, performer:Performer, opportunity:Opportunity, registries:ExpressionRegistries) -> ResolvedExpression`
  - `apply_expressions(host:HostComposition, expressions:tuple[ResolvedExpression,...]) -> HostComposition`
  - `compare_host_dimensions(host:HostComposition, variant:HostComposition) -> dict[str,bool]`
  - `assert_frozen_dimensions(host:HostComposition, variant:HostComposition, frozen:tuple[str,...], mutated:tuple[str,...]) -> None`
  - `expression_density(expressions:tuple[ResolvedExpression,...], opportunity:Opportunity) -> float`

- [ ] **Step 1: Write failing generic-engine tests**

Assert:
- invalid performer/trait/technique/function references refuse deterministically;
- request function must be allowed by the opportunity;
- request role family must be allowed by the opportunity;
- multiple expressions may overlap the same role family;
- applying expressions never mutates the input host object;
- changing a frozen tempo, meter, section boundary or host-riff signature is refused;
- density budget overflow is refused unless the experiment variant explicitly declares a saturation control.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_expression_engine -v`
Expected: FAIL.

- [ ] **Step 3: Implement registry validation and pure application pipeline**

Keep transformation policy generic. Dispatch by technique ID through a registry of small deterministic handlers rather than experiment IDs.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_expression_engine -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/expression_engine.py fusion_lab/tests/test_expression_engine.py fusion_lab/model.py
git commit -m "feat: add generic fusion expression engine"
```

---

### Task 3: Technique Handler Registry

**Files:**
- Modify: `fusion_lab/expression_engine.py`
- Modify: `fusion_lab/tests/test_expression_engine.py`

**Interfaces:**
- Produces handler registrations for:
  - `SUSTAINED_MELODIC_LINE`
  - `DRONE_ANCHOR`
  - `THUMB_ATTACK`
  - `SLAP_POP`
  - `GHOST_NOTE`
  - `METRIC_DISPLACEMENT`
  - `ROLE_LOCAL_CYCLE`
  - `SYNTH_SWELL`
  - `CHOIR_PAD`
  - `FILTER_MOVEMENT`
  - `NOISE_BED`
  - `DOUBLE_KICK_LOCK`
  - `BLAST_BEAT`
  - `DEATH_HALF_TIME`
  - `TOM_FILL`

- [ ] **Step 1: Add failing handler tests**

Pin at least one behavior per family:
- Doom sustain spans multiple host beats without changing global BPM;
- local-cycle handler changes accent placement but retains absolute tick clock;
- synth treatments may change program/register/velocity/timbre metadata while preserving declared host harmony;
- Death drum handlers use percussion channel and section-specific subdivision/density patterns;
- the same `SUSTAINED_MELODIC_LINE` technique can resolve under both `COUNTER_MELODY` and `RESOLUTION` functions.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_expression_engine -v`
Expected: new handler tests FAIL.

- [ ] **Step 3: Implement minimal deterministic handlers**

Handlers receive host/opportunity/context and return events only. They do not know experiment IDs.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_expression_engine -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/expression_engine.py fusion_lab/tests/test_expression_engine.py
git commit -m "feat: add reusable fusion technique handlers"
```

---

### Task 4: Compose the THRASH CHIMERA Control Host

**Files:**
- Create: `fusion_lab/thrash_chimera.py`
- Create: `fusion_lab/tests/test_thrash_chimera.py`

**Interfaces:**
- Produces:
  - `build_thrash_host() -> HostComposition`
  - `build_thrash_chimera_registries() -> ExpressionRegistries`
  - `build_thrash_chimera_opportunities(host:HostComposition) -> tuple[Opportunity,...]`

- [ ] **Step 1: Write failing Thrash host tests**

Pin:
- `190 BPM`, `4/4`, E-centered aggressive minor/chromatic language;
- clear deterministic form: INTRO, VERSE_1, PRE_CHORUS, CHORUS_1, VERSE_2, CHORUS_2, SOLO, BREAK, FINAL_CHORUS, OUTRO;
- palm-muted gallop/downpick rhythm-guitar identity;
- control bass follows host riff;
- control drums are conventional Thrash, not blast/death-half-time in A;
- five existing semantic roles remain representable and no generic recruit trait is present in A.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_thrash_chimera -v`
Expected: FAIL.

- [ ] **Step 3: Implement deterministic host and registries**

Keep recruit definitions declarative in this module; generic engine remains experiment-agnostic.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_thrash_chimera -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/thrash_chimera.py fusion_lab/tests/test_thrash_chimera.py
git commit -m "feat: compose thrash chimera control host"
```

---

### Task 5: THRASH CHIMERA Single-Recruit Variants B/C/D/E

**Files:**
- Modify: `fusion_lab/thrash_chimera.py`
- Modify: `fusion_lab/tests/test_thrash_chimera.py`

**Interfaces:**
- Produces:
  - `build_thrash_chimera_variants() -> dict[str,HostComposition]`
  - `build_thrash_chimera_expression_sets() -> dict[str,tuple[ExpressionRequest,...]]`

- [ ] **Step 1: Write failing B/C/D/E tests**

Pin:
- `B`: Doom sustained melodic counterline overlays the 190 BPM host without changing tempo/meter/riff identity;
- `C`: Djent bass uses `3+3+2+3+5` local accent grouping and converges at authored target ticks while the host remains 190 BPM;
- `D`: Prog synth adds timbral/textural treatment while preserving host harmony/section timing;
- `E`: Death drummer uses double-kick propulsion, blast escalation, dense chorus support, half-time break and tom-fill transition under one performer identity;
- every variant passes its declared frozen-dimension contract.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_thrash_chimera -v`
Expected: new variant tests FAIL.

- [ ] **Step 3: Implement single-recruit variants through generic engine only**

No `if experiment == 'thrash-chimera'` logic is allowed inside `expression_engine.py`.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_thrash_chimera -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/thrash_chimera.py fusion_lab/tests/test_thrash_chimera.py
git commit -m "feat: add thrash chimera recruit variants"
```

---

### Task 6: Full Chimera F and Bad-Placement Control G

**Files:**
- Modify: `fusion_lab/thrash_chimera.py`
- Modify: `fusion_lab/tests/test_thrash_chimera.py`
- Create: `fusion_lab/data/experiments/exp-002-thrash-chimera.json`

**Interfaces:**
- Extends `build_thrash_chimera_variants()` with `A..G`.

- [ ] **Step 1: Write failing F/G tests**

Assert:
- F contains all four performers concurrently;
- Doom guitar and Prog synth can overlap the same broad role family while serving different functions;
- F respects all authored density budgets and convergence targets;
- G uses the same host and performer vocabulary but deliberately worsens placement/density policy;
- F and G have identical host tempo, meter, section boundaries, phrase boundaries and host-riff signature;
- G has greater aggregate density/overlap and more out-of-opportunity placements than F;
- experiment metadata conclusion remains `UNRESOLVED` until human listening evidence is supplied.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_thrash_chimera -v`
Expected: FAIL.

- [ ] **Step 3: Implement F/G and experiment metadata**

Bad placement is an explicit experiment policy, not silent validator bypass. Record each exception/provenance entry.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_thrash_chimera -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/thrash_chimera.py fusion_lab/tests/test_thrash_chimera.py fusion_lab/data/experiments/exp-002-thrash-chimera.json
git commit -m "feat: generate full thrash chimera experiment"
```

---

### Task 7: MIDI/Render Support for Overlapping Performer Layers

**Files:**
- Modify: `fusion_lab/midi_io.py`
- Modify: `fusion_lab/render.py` only if needed
- Modify: `fusion_lab/tests/test_midi_io.py`
- Modify: `fusion_lab/tests/test_render_contract.py`

**Interfaces:**
- Existing Host 001 and Experiment 001 serialization signatures must remain unchanged.
- New output may include additional deterministic performer-layer stem names when compound experiments require them.

- [ ] **Step 1: Write failing overlap serialization tests**

Assert:
- overlapping performer expressions serialize without dropping either layer;
- drum recruit events stay on percussion channel;
- non-drum performer layers use deterministic non-conflicting channels/programs;
- repeated A..G generation yields stable normalized signatures;
- existing Host 001/EXP-001 normalized signatures remain stable.

- [ ] **Step 2: Run RED**

Run:
```bash
python -m unittest fusion_lab.tests.test_midi_io fusion_lab.tests.test_render_contract -v
```
Expected: new overlap tests FAIL.

- [ ] **Step 3: Implement minimal serialization/render extension**

Do not alter existing filenames unless a collision exists. New performer stems use stable names derived from performer ID.

- [ ] **Step 4: Run GREEN**

Run:
```bash
python -m unittest fusion_lab.tests.test_midi_io fusion_lab.tests.test_render_contract -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/midi_io.py fusion_lab/render.py fusion_lab/tests/test_midi_io.py fusion_lab/tests/test_render_contract.py
git commit -m "feat: render overlapping fusion performers"
```

---

### Task 8: Generic and THRASH CHIMERA CLI

**Files:**
- Modify: `fusion_lab/cli.py`
- Modify: `fusion_lab/tests/test_gauntlet.py`
- Modify: `docs/FUSION_LAB.md`

**Interfaces:**
- Add:
  - `python -m fusion_lab thrash-chimera --out <dir>`
  - `python -m fusion_lab verify-thrash-chimera --dir <dir>`
  - `python -m fusion_lab render-thrash-chimera --root <dir> --soundfont <path>`

- [ ] **Step 1: Write failing CLI tests**

Assert:
- A..G deterministic directories are created;
- verification checks frozen-dimension contracts and signatures;
- render command delegates to existing headless renderer and does not require DISPLAY/X11;
- short actionable diagnostics are produced for missing dependency/SoundFont paths.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_gauntlet -v`
Expected: new CLI tests FAIL.

- [ ] **Step 3: Implement CLI commands and docs**

Document exact Proot commands and output locations.

- [ ] **Step 4: Run CLI smoke tests**

Run:
```bash
python -m fusion_lab thrash-chimera --out fusion_lab/out/exp-002
python -m fusion_lab verify-thrash-chimera --dir fusion_lab/out/exp-002
```
Expected: deterministic A..G generation and verification PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/cli.py fusion_lab/tests/test_gauntlet.py docs/FUSION_LAB.md
git commit -m "feat: expose thrash chimera headless workflow"
```

---

### Task 9: Full Generic Engine Gauntlet and Real Proot Render

**Files:**
- Modify: `fusion_lab/tests/test_gauntlet.py`
- Modify: `docs/FUSION_LAB.md`
- Modify: `fusion_lab/data/experiments/exp-002-thrash-chimera.json` only after human listening evidence.

**Interfaces:**
- Consumes Tasks 1–8.

- [ ] **Step 1: Extend full gauntlet**

Prove in one flow:
1. trait/technique/function/role independence;
2. same technique → multiple functions;
3. same function → multiple techniques;
4. multiple performers overlap one role family;
5. undeclared host mutation is refused;
6. Doom sustain preserves 190 BPM host clock;
7. Djent local cycle preserves global tick clock and convergence;
8. Prog synth preserves host harmony/timing while changing treatment;
9. Death drummer performs multiple functions under one identity;
10. F and G share host song authority but differ in placement/density policy;
11. A..G normalized event signatures are deterministic;
12. EXP-001 and Host 001 remain green.

- [ ] **Step 2: Run complete Python suite**

Run:
```bash
python -m unittest discover -s fusion_lab/tests -v
```
Expected: PASS.

- [ ] **Step 3: Run existing game regression suite/build**

Run:
```bash
npm test
npm run build
```
Expected: PASS.

- [ ] **Step 4: Perform actual Proot render**

Run:
```bash
python -m fusion_lab render-thrash-chimera \
  --root fusion_lab/out/exp-002 \
  --soundfont "$SOUNDFONT"
```
Expected: audible A/B/C/D/E/F/G output generated headlessly.

- [ ] **Step 5: Record human listening evidence without forcing a conclusion**

Keep `UNRESOLVED` until the operator explicitly marks the experiment `SUPPORTED`, `REFUTED` or `MIXED`.

- [ ] **Step 6: Commit verification/docs after evidence**

```bash
git add fusion_lab/tests/test_gauntlet.py docs/FUSION_LAB.md fusion_lab/data/experiments/exp-002-thrash-chimera.json
git commit -m "test: prove generic fusion engine with thrash chimera"
```

---

## Exit Gate

The Generic Fusion Expression Engine milestone is complete only when:

1. performer, trait, technique, function, opportunity, context and expression are independent contracts;
2. a technique can serve multiple functions;
3. a function can be realized by multiple techniques;
4. multiple performers can overlap a role family;
5. undeclared mutation leakage is refused;
6. single-recruit and compound experiments use one generic path;
7. THRASH CHIMERA A/B/C/D/E/F/G generates deterministically;
8. Doom sustain does not change the ~190 BPM host clock;
9. Djent local-cycle identity does not create a second tempo;
10. Prog synth changes timbral identity without stealing host structural authority;
11. Death drummer uses several functions while retaining one performer identity;
12. F vs G isolates placement/density quality rather than changing the host song;
13. all variants serialize and render headlessly in Proot;
14. Host 001 and Experiment 001 regressions remain green;
15. Polly's existing game tests/build remain green;
16. no engine rule collapses style into function.

**No Pattern Map schema change is part of this milestone.**