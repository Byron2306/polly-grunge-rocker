# Riff Morphology and Physical Gesture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add deterministic riff-family morphology and genre-specific structural grammar to Music DNA, then refactor Chainsaw Diplomacy around five audibly distinct thrash riff families without weakening existing production or genre truth gates.

**Architecture:** Introduce a focused `riff_morphology.py` analyzer that turns bar/phrase cells into transposition-invariant signatures, groups them deterministically into riff families, and emits explainable song-level structure metrics plus physical-gesture metadata. Extend genre profiles and validation additively with an optional `riff_structure` component, then rewrite Chainsaw's rhythm/accompaniment generation around explicit A/B/C/D/E riff families whose gestures drive drums and bass.

**Tech Stack:** Python 3.14-compatible stdlib, dataclasses/enums, existing `fusion_lab` model/profile/validator stack, `unittest`, existing SFZ/MIDI production pipeline.

**Spec:** `docs/superpowers/specs/2026-10-02-riff-morphology-design.md`

## Global Constraints

- No new runtime dependency.
- Existing genre JSON without `riff_structure` must continue to load unchanged.
- Existing Music DNA payload keys remain stable; morphology output is additive.
- Existing symbolic gates for gallop rate, downpick ratio, harmony, drums, bass fills, and production truth remain active.
- Transposition alone must not create a new riff family.
- Rhythm/cadence/articulation differences must outweigh absolute pitch when deciding family identity.
- `THRASH_CLASSIC` must reward several riff identities, limited same-family runs, meaningful transitions, and gesture diversity without prescribing exact song form.
- `BLACK_METAL` must permit long same-family/TRANCE repetition and must not require conventional hooks, solos, or chorus form.
- Chainsaw must contain explicit A_HOOK, B_SPRINT, C_STOMP, D_PANIC, and E_TRANSITION families.
- Existing CAPS tone, articulation routing, audibility calibration, and human-review gates remain intact.
- Human vocals remain external; this phase may only expose delivery metadata if required by an existing Chainsaw path.

## Review Focus

- Empty/sparse rhythm tracks: morphology should return deterministic zero/empty structure without crashing or inventing families.
- Pickup notes or bars with events crossing boundaries: signatures must use onset membership deterministically and never double-count an onset across bars.
- Transposed copies with different MIDI register: family identity must remain stable while pedal pitch class may differ only as normalized anchor metadata.
- Profiles without `riff_structure`: validation must behave exactly as before and must not add mutation/rejection reasons.
- Explicit gesture metadata missing on legacy songs: analyzer must report `UNKNOWN` rather than fail or infer a genre judgment.

---

### Task 1: Riff signature and deterministic family clustering

**Files:**
- Create: `fusion_lab/music_dna/riff_morphology.py`
- Create: `fusion_lab/tests/test_music_dna_riff_morphology.py`

**Interfaces:**
- Consumes: `HostComposition`, `NoteEvent`, `Section` from `fusion_lab.model`.
- Produces: `Gesture`, `RiffSignature`, `RiffFamily`, `RiffMorphologyReport`, `signature_for_bar(events, bar_start, bar_ticks) -> RiffSignature`, `analyze_riff_morphology(host, explicit_gestures=None) -> RiffMorphologyReport`.

- [ ] **Step 1: Write failing tests for transposition invariance and distinct rhythm/cadence**

Add tests named:
- `test_transposed_copy_has_same_morphology_signature`
- `test_same_pedal_with_different_rhythm_and_cadence_is_distinct`

Assert that two cells with identical relative interval/onset/rest/accent/articulation/cadence patterns but transposed roots cluster together, while a cell sharing the pedal note but changing onset and cadence pattern does not.

- [ ] **Step 2: Run the focused tests and verify RED**

Run:
```bash
python -m unittest fusion_lab.tests.test_music_dna_riff_morphology -v
```
Expected: FAIL because `riff_morphology` and its public types/functions do not yet exist.

- [ ] **Step 3: Implement the signature model and normalization**

Create:
```python
class Gesture(str, Enum): ...
@dataclass(frozen=True, slots=True)
class RiffSignature: ...
@dataclass(frozen=True, slots=True)
class RiffFamily: ...
@dataclass(frozen=True, slots=True)
class RiffMorphologyReport: ...
def signature_for_bar(events: Sequence[NoteEvent], bar_start: int, bar_ticks: int) -> RiffSignature: ...
```

Normalize pitch contour relative to onset roots, normalize onset/rest positions by `bar_ticks`, bucket accents into deterministic low/medium/high classes, map articulation strings into stable semantic classes, and classify final-quarter cadence as `release`, `chromatic`, `held`, or `empty`.

- [ ] **Step 4: Implement deterministic family similarity and assignment**

Add internal similarity helpers weighting onset/rhythm and cadence above pitch contour, then assign families in chronological first-seen order using fixed thresholds. No random state and no dependency on dictionary insertion outside sorted/chronological inputs.

- [ ] **Step 5: Add edge-case tests from Review Focus**

Add:
- `test_empty_rhythm_track_reports_zero_families`
- `test_bar_boundary_onsets_are_counted_once`
- `test_register_shift_does_not_create_fake_family`

- [ ] **Step 6: Run focused morphology tests**

Run:
```bash
python -m unittest fusion_lab.tests.test_music_dna_riff_morphology -v
```
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add fusion_lab/music_dna/riff_morphology.py fusion_lab/tests/test_music_dna_riff_morphology.py
git commit -m "music-dna: add deterministic riff morphology"
```

### Task 2: Song-level morphology metrics and additive report payload

**Files:**
- Modify: `fusion_lab/music_dna/riff_morphology.py`
- Modify: `fusion_lab/music_dna/model.py`
- Modify: `fusion_lab/music_dna/analysis.py`
- Test: `fusion_lab/tests/test_music_dna_riff_morphology.py`
- Test: `fusion_lab/tests/test_chainsaw_music_dna.py`

**Interfaces:**
- Consumes: `analyze_riff_morphology(host, explicit_gestures=None)` from Task 1.
- Produces: report metrics `riff_family_count`, `riff_family_recurrence`, `longest_same_family_run_bars`, `section_riff_contrast`, `transition_density`, `gesture_diversity`; `MusicDNAReport.riff_structure` mapping; `to_dict()['riff_structure']`.

- [ ] **Step 1: Write failing song-level metric tests**

Add:
- `test_repetitive_song_reports_long_run_and_low_section_contrast`
- `test_multi_riff_song_reports_family_and_gesture_diversity`

Use minimal deterministic fixtures and assert metric direction, not opaque scores.

- [ ] **Step 2: Run tests and verify RED**

Run:
```bash
python -m unittest fusion_lab.tests.test_music_dna_riff_morphology -v
```
Expected: FAIL because song-level fields/report wiring are absent.

- [ ] **Step 3: Implement song-level calculations**

In `riff_morphology.py`, calculate family counts, most-common-family recurrence, chronological longest run, section-to-section family-set contrast, proportion of bars/cells marked `TRANSITION`, and diversity of non-UNKNOWN gestures.

- [ ] **Step 4: Extend `MusicDNAReport` additively**

Add:
```python
riff_structure: Mapping[str, object]
```
with sorted/frozen-compatible serialization in `to_dict()`. Preserve all existing keys unchanged.

- [ ] **Step 5: Wire morphology into `analyze_host()`**

Call the analyzer once and pass its serialized payload into `build_music_dna_report` without changing existing feature/coupling/hook extraction.

- [ ] **Step 6: Add compatibility assertion**

Update an existing report test to assert legacy keys still exist and the new `riff_structure` key is additive.

- [ ] **Step 7: Run report/morphology tests**

Run:
```bash
python -m unittest \
  fusion_lab.tests.test_music_dna_riff_morphology \
  fusion_lab.tests.test_chainsaw_music_dna -v
```
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add fusion_lab/music_dna/riff_morphology.py fusion_lab/music_dna/model.py fusion_lab/music_dna/analysis.py fusion_lab/tests/test_music_dna_riff_morphology.py fusion_lab/tests/test_chainsaw_music_dna.py
git commit -m "music-dna: expose riff structure report"
```

### Task 3: Optional genre structural priors and validation

**Files:**
- Modify: `fusion_lab/music_dna/model.py`
- Modify: `fusion_lab/music_dna/genre_profiles.py`
- Modify: `fusion_lab/music_dna/validator.py`
- Modify: `fusion_lab/data/music_dna/genres/thrash.json`
- Modify: `fusion_lab/data/music_dna/genres/black_metal.json`
- Create or modify: `fusion_lab/tests/test_music_dna_genre_profiles.py`
- Test: `fusion_lab/tests/test_music_dna_riff_morphology.py`

**Interfaces:**
- Consumes: numeric morphology metrics from Task 2.
- Produces: optional `RiffStructureDNA`; `GenreDNA.riff_structure: RiffStructureDNA | None`; validator keys prefixed `riff_structure.`.

- [ ] **Step 1: Write failing backward-compatibility and opt-in profile tests**

Add tests:
- `test_profile_without_riff_structure_loads_unchanged`
- `test_thrash_profile_loads_riff_structure_ranges`
- `test_black_metal_profile_allows_long_trance_runs`

The first test must load a temporary legacy-shaped v1 profile and assert `riff_structure is None`.

- [ ] **Step 2: Run tests and verify RED**

Run the profile and morphology test modules; expected failure because the optional component is unsupported.

- [ ] **Step 3: Add optional `RiffStructureDNA` model and loader support**

Add a DNA component class and optional field to `GenreDNA`. Do not add `riff_structure` to the required component set. Parse it only when present.

- [ ] **Step 4: Merge morphology metrics into validation inputs**

Extend `build_music_dna_report()` / `validate_genre()` signatures with optional `riff_structure` mapping and flatten profile ranges under `riff_structure.<metric>`. If profile or report structure data is absent, produce no new reason.

- [ ] **Step 5: Seed `THRASH_CLASSIC` structural ranges**

Add ranges for:
- `riff_family_count`
- `riff_family_recurrence`
- `longest_same_family_run_bars`
- `section_riff_contrast`
- `transition_density`
- `gesture_diversity`

Choose initial ranges from the approved spec intent and existing fixtures, then lock them with tests rather than weakening existing guitar/drum thresholds.

- [ ] **Step 6: Seed contrasting `BLACK_METAL` ranges**

Permit materially longer same-family runs and lower transition density than thrash. Do not add a hook/solo/chorus requirement. Add a test fixture explicitly tagged `TRANCE` whose long repetition validates under black metal but would fall outside thrash structural preference.

- [ ] **Step 7: Run profile/validator regression suite**

Run:
```bash
python -m unittest \
  fusion_lab.tests.test_music_dna_genre_profiles \
  fusion_lab.tests.test_music_dna_riff_morphology \
  fusion_lab.tests.test_chainsaw_music_dna -v
```
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add fusion_lab/music_dna/model.py fusion_lab/music_dna/genre_profiles.py fusion_lab/music_dna/validator.py fusion_lab/data/music_dna/genres/thrash.json fusion_lab/data/music_dna/genres/black_metal.json fusion_lab/tests/test_music_dna_genre_profiles.py fusion_lab/tests/test_music_dna_riff_morphology.py
git commit -m "music-dna: add genre-specific riff structure priors"
```

### Task 4: Replace Chainsaw variant cycling with explicit A/B/C/D/E riff families

**Files:**
- Modify: `fusion_lab/chainsaw_diplomacy.py`
- Modify: `fusion_lab/tests/test_chainsaw_music_dna.py`
- Test: `fusion_lab/tests/test_articulation_sfz_routing.py`

**Interfaces:**
- Consumes: `Gesture` from Task 1 and existing `NoteEvent`/articulation semantics.
- Produces: explicit family composers `_riff_a_hook`, `_riff_b_sprint`, `_riff_c_stomp`, `_riff_d_panic`, `_riff_e_transition`; deterministic section-family schedule; family/gesture metadata consumable by morphology analysis.

- [ ] **Step 1: Write failing Chainsaw family-coverage tests**

Add tests asserting:
- all A/B/C/D/E families appear in the song schedule
- at least five family identities are reported
- `longest_same_family_run_bars` is within the thrash profile's configured preferred/hard range
- at least four distinct section opening signatures remain
- gallop/downpick/harmony gates remain at current thresholds

- [ ] **Step 2: Run Chainsaw test and verify RED**

Run:
```bash
python -m unittest fusion_lab.tests.test_chainsaw_music_dna -v
```
Expected: FAIL because the current `_riff_for_bar`/variant table architecture cannot satisfy explicit family coverage.

- [ ] **Step 3: Implement A_HOOK**

Create an original E-pedal hook with memorable upper movement and a strong cadence. Preserve the existing successful palm-mute/downpick and chromatic vocabulary, but do not copy reference-track notes.

- [ ] **Step 4: Implement B_SPRINT**

Create a denser continuous downpick/gallop family with fewer chord-stab resets and explicit hybrid gallop/downpick semantics compatible with the articulation alias layer.

- [ ] **Step 5: Implement C_STOMP**

Create spacious syncopated/half-time material with large landing accents and more rests; avoid simply slowing A_HOOK.

- [ ] **Step 6: Implement D_PANIC**

Create a reduced-pedal chromatic/tritone family with unstable forward pressure and clearly different contour/onset signature from A/B/C.

- [ ] **Step 7: Implement E_TRANSITION**

Create one- or two-bar connective cells that terminate into the next family and are never scheduled as a long main-riff run.

- [ ] **Step 8: Replace `_SECTION_VARIANTS` with explicit family schedule**

Encode the approved flow:
- intro A
- verse1 A -> B
- pre D -> B
- chorus1 A' -> C
- verse2 B -> D
- chorus2 A' -> C'
- solo B / D
- bridge C -> E
- final A' -> B -> C
- outro D -> E

Use deliberate A'/C' mutations that remain in the same family rather than creating fake novelty.

- [ ] **Step 9: Run Chainsaw and articulation tests**

Run:
```bash
python -m unittest \
  fusion_lab.tests.test_chainsaw_music_dna \
  fusion_lab.tests.test_articulation_sfz_routing -v
```
Expected: PASS.

- [ ] **Step 10: Commit**

```bash
git add fusion_lab/chainsaw_diplomacy.py fusion_lab/tests/test_chainsaw_music_dna.py fusion_lab/tests/test_articulation_sfz_routing.py
git commit -m "chainsaw: compose explicit thrash riff families"
```

### Task 5: Couple drums and bass to riff-family gesture boundaries

**Files:**
- Modify: `fusion_lab/chainsaw_diplomacy.py`
- Modify: `fusion_lab/tests/test_chainsaw_music_dna.py`
- Test: `fusion_lab/tests/test_music_dna_coupling.py`

**Interfaces:**
- Consumes: deterministic family/gesture schedule from Task 4.
- Produces: gesture-aware `_drums(...)` and `_bass(...)` behavior with fills/attacks tied to riff boundaries rather than only fixed section ends.

- [ ] **Step 1: Write failing gesture-coupling tests**

Assert:
- SPRINT bars have higher kick propulsion density than STOMP bars
- STOMP bars have fewer attacks and stronger landing velocities
- PANIC bars include accent displacement or short double-kick escalation
- family boundaries can create bass/drum transition fills even when not at section end

- [ ] **Step 2: Run tests and verify RED**

Run Chainsaw and coupling test modules; expected failure under current section-only accompaniment logic.

- [ ] **Step 3: Refactor bass generation around family boundaries**

Continue following riff roots, preserve audibility velocities, and allow fills at selected family transitions. Do not raise guitar-lock rate above the existing `<= 0.90` gate.

- [ ] **Step 4: Refactor drum generation around gestures**

Map SPRINT/STOMP/PANIC/TRANSITION behaviors from the spec while preserving current aggressive velocity floor and double-kick density. Transition fills should answer or trigger family changes instead of always landing only on section-final bars.

- [ ] **Step 5: Run coupling and Chainsaw tests**

Run:
```bash
python -m unittest \
  fusion_lab.tests.test_chainsaw_music_dna \
  fusion_lab.tests.test_music_dna_coupling -v
```
Expected: PASS with existing coupling sanity checks retained.

- [ ] **Step 6: Commit**

```bash
git add fusion_lab/chainsaw_diplomacy.py fusion_lab/tests/test_chainsaw_music_dna.py fusion_lab/tests/test_music_dna_coupling.py
git commit -m "chainsaw: couple rhythm section to riff gestures"
```

### Task 6: Preserve lead believability and expose family-aware solo backing

**Files:**
- Modify: `fusion_lab/chainsaw_diplomacy.py`
- Modify: `fusion_lab/tests/test_chainsaw_music_dna.py`
- Test: `fusion_lab/tests/test_chainsaw_aggro_profile.py`

**Interfaces:**
- Consumes: B_SPRINT/D_PANIC solo-backing schedule from Task 4.
- Produces: existing lead track over family-aware backing; no new synthesis dependency.

- [ ] **Step 1: Add failing lead/backing assertions**

Assert the solo section's backing uses B/D families, the lead stays inside the existing guitar-like register bound, includes phrase space, and does not collapse into continuous scalar sixteenth-note output.

- [ ] **Step 2: Run test and verify RED if current solo backing is incompatible**

Run:
```bash
python -m unittest fusion_lab.tests.test_chainsaw_music_dna -v
```

- [ ] **Step 3: Adapt lead phrasing only where family changes require it**

Keep rests, sustained notes, bounded register, and dedicated CAPS lead mode. Align phrase entries/exits with B/D boundaries without reintroducing the high-register digital-ping behavior.

- [ ] **Step 4: Run lead/tone regressions**

Run:
```bash
python -m unittest \
  fusion_lab.tests.test_chainsaw_music_dna \
  fusion_lab.tests.test_chainsaw_aggro_profile -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/chainsaw_diplomacy.py fusion_lab/tests/test_chainsaw_music_dna.py
git commit -m "chainsaw: align lead with riff-family backing"
```

### Task 7: Full Music DNA gauntlet and governed V5 render handoff

**Files:**
- Modify only if tests reveal supported defects; no feature expansion in this task.
- Verify: `fusion_lab/music_dna/chainsaw_v5.py`
- Verify: `scripts/render_chainsaw_pit_v5.sh`
- Verify: existing production/audio truth tests.

**Interfaces:**
- Consumes: Tasks 1-6.
- Produces: a clean `PENDING_HUMAN_REVIEW` V5 analysis and isolated-guitar render ready for Byron's ear gate.

- [ ] **Step 1: Run the focused morphology/genre/Chainsaw suite**

Run:
```bash
python -m unittest \
  fusion_lab.tests.test_music_dna_riff_morphology \
  fusion_lab.tests.test_music_dna_hook_score \
  fusion_lab.tests.test_music_dna_genre_profiles \
  fusion_lab.tests.test_music_dna_coupling \
  fusion_lab.tests.test_chainsaw_music_dna \
  fusion_lab.tests.test_chainsaw_aggro_profile \
  fusion_lab.tests.test_articulation_sfz_routing \
  fusion_lab.tests.test_mix_truth -v
```
Expected: PASS.

- [ ] **Step 2: Run the full Music DNA/project gauntlet**

Run the repository's existing comprehensive unittest command or the V5 gauntlet script used on this branch. Expected: all existing tests green; no legacy profile/report regressions.

- [ ] **Step 3: Run static diff check**

Run:
```bash
git diff --check
```
Expected: no output.

- [ ] **Step 4: Analyze Chainsaw through the governed gate**

Run:
```bash
bash scripts/render_chainsaw_pit_v5.sh analyze
```
Expected:
```text
state: PENDING_HUMAN_REVIEW
reasons: []
```
The generated Music DNA report must include `riff_structure` with A/B/C/D/E coverage, sufficient gesture diversity, acceptable longest-family run, and acceptable transition density.

- [ ] **Step 5: Render isolated guitars for human review**

Run:
```bash
bash scripts/render_chainsaw_pit_v5.sh isolated
```
Expected: isolated-guitar render succeeds and the gate remains `PENDING_HUMAN_REVIEW` until explicit approval.

- [ ] **Step 6: Do not auto-pass the human gate**

Byron must listen for the approved success criterion: audible movement among hook, sprint, stomp, panic, and transition behaviors without losing the established dirty/aggressive guitar tone. Do not run `review-pass` or `full` from automation without that explicit ear approval.

- [ ] **Step 7: Commit any verification-only supported repairs, then record final branch status**

If no repairs were required, leave the branch at the Task 6 commit and report test/render evidence. If supported defects were repaired, commit only those narrowly scoped fixes with a verification-focused message.
