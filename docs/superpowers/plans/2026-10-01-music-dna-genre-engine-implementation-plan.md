# Music DNA Genre Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic whole-band Music DNA subsystem that extracts genre features from existing Polly compositions, validates them against seeded genre distributions, enforces cross-instrument and production-truth rules, and integrates the first end-to-end thrash acceptance path into Chainsaw Diplomacy.

**Architecture:** Add a focused `fusion_lab/music_dna/` package around the existing `HostComposition` / `NoteEvent` model. The first milestone works on existing symbolic compositions without changing the renderer; later tasks add performance-event adapters, production-truth enforcement, and Chainsaw-specific staged rendering. Genre identity is represented by distributions and relational features, not fixed recipes or copied reference riffs.

**Tech Stack:** Python 3, `dataclasses`, `enum`, `json`, existing `unittest` suite, existing Fusion Lab `HostComposition` / `NoteEvent` / production pipeline, existing `sfizz_render` + ffmpeg production path.

**Spec:** `docs/superpowers/specs/2026-10-01-music-dna-genre-engine-design.md`

## Global Constraints

- Do not persist or emit complete copyrighted third-party scores, tabs, melodies, or lyrics.
- Keep the existing deterministic composition and rendering pipeline; Music DNA wraps and validates it rather than replacing it.
- No cloud inference is required.
- Genre definitions are distributions / ranges / relationships, not one band's style and not a single hardcoded recipe.
- Initial genre families: thrash metal, black metal, death metal, doom metal, punk, glam metal, progressive metal.
- Thrash is the first end-to-end validation target via `host-003-chainsaw-diplomacy`.
- `ALLOW`, `MUTATE`, and `REJECT` decisions must be explainable with deterministic reason codes.
- Input volume must never be treated as evidence of amplifier gain.
- Generic tanh soft clipping alone must never satisfy `amp_distortion_required`.
- A metal profile that requires conventional amplified-guitar tone must fail production truth if cabinet / IR evidence is absent.
- Palm-muted and sustained rhythm-guitar paths must be measurably distinct or rendering must be refused.
- L/R rhythm tracks must represent distinct performance variants while preserving riff identity.
- Every accepted/generated host writes deterministic `music-dna-report.json` data alongside the production manifest.
- Full-mix Chainsaw rendering is gated behind isolated rhythm-guitar acceptance.

## Review Focus

1. **Malformed or incomplete profile data:** loading must fail with a precise error rather than silently applying defaults that change genre meaning. Covered in Task 1 and Task 3 tests.
2. **Dense but unrelated instruments falsely appearing coupled:** coincidence calculations must use event timing, not raw event counts. Covered in Task 5 tests.
3. **Short-loop repetition gaming the hook score:** exact cycles repeated across long sections must be penalized even when recurrence is high. Covered in Task 6 tests.
4. **Production metadata claiming authenticity without signal-path evidence:** cabinet/amp/palm-mute/double-track requirements must be independently verified. Covered in Task 9 tests.
5. **Genre blends producing impossible or contradictory hard requirements:** incompatible hard constraints must be reported explicitly instead of numerically averaged. Covered in Task 8 tests.

---

## File Structure

### New package

- `fusion_lab/music_dna/model.py` — immutable DNA models, decision/report types, bounded feature primitives.
- `fusion_lab/music_dna/distributions.py` — deterministic scalar/range/categorical distributions and weighted blending primitives.
- `fusion_lab/music_dna/feature_extractors.py` — per-role and whole-host symbolic feature extraction from `HostComposition`.
- `fusion_lab/music_dna/genre_profiles.py` — JSON loading + typed profile assembly.
- `fusion_lab/music_dna/corpus.py` — curated aggregate observation/provenance loader.
- `fusion_lab/music_dna/coupling.py` — timing-based cross-instrument relationship metrics.
- `fusion_lab/music_dna/hook_score.py` — motif recurrence/mutation and anti-loop scoring.
- `fusion_lab/music_dna/validator.py` — deterministic distance checks and `ALLOW|MUTATE|REJECT` reason generation.
- `fusion_lab/music_dna/blend.py` — weighted profile blending with hard-constraint conflict handling.
- `fusion_lab/music_dna/production_truth.py` — truthful signal-path evidence and refusal logic.
- `fusion_lab/music_dna/performance.py` — richer guitar/bass/drum/vocal/keys events plus adapters back to `NoteEvent`.
- `fusion_lab/music_dna/__init__.py` — stable public exports only.

### New data

- `fusion_lab/data/music_dna/corpus.json`
- `fusion_lab/data/music_dna/genres/thrash.json`
- `fusion_lab/data/music_dna/genres/black_metal.json`
- `fusion_lab/data/music_dna/genres/death_metal.json`
- `fusion_lab/data/music_dna/genres/doom_metal.json`
- `fusion_lab/data/music_dna/genres/punk.json`
- `fusion_lab/data/music_dna/genres/glam_metal.json`
- `fusion_lab/data/music_dna/genres/progressive_metal.json`

### Integration changes

- `fusion_lab/chainsaw_diplomacy.py` — consume thrash profile during candidate validation / transformation only after core engine exists.
- `fusion_lab/production_model.py` — add production-path evidence fields only where required by Task 9.
- `fusion_lab/production_render.py` — emit production topology evidence and refuse false amp/cab claims.
- `fusion_lab/production_pipeline.py` — stage Chainsaw rendering behind Music DNA / isolated-guitar gates and write `music-dna-report.json`.
- `fusion_lab/cli.py` — expose report/validation command(s) only after internal APIs are stable.
- `scripts/render_chainsaw_pit_v5.sh` — render through the staged acceptance path after Task 11.

### New tests

- `fusion_lab/tests/test_music_dna_model.py`
- `fusion_lab/tests/test_music_dna_features.py`
- `fusion_lab/tests/test_music_dna_profiles.py`
- `fusion_lab/tests/test_music_dna_coupling.py`
- `fusion_lab/tests/test_music_dna_hook_score.py`
- `fusion_lab/tests/test_music_dna_validator.py`
- `fusion_lab/tests/test_music_dna_blend.py`
- `fusion_lab/tests/test_music_dna_production_truth.py`
- `fusion_lab/tests/test_music_dna_performance.py`
- `fusion_lab/tests/test_chainsaw_music_dna.py`
- `fusion_lab/tests/test_chainsaw_isolated_guitar_gate.py`

---

### Task 1: Core bounded models and decision types

**Files:**
- Create: `fusion_lab/music_dna/model.py`
- Create: `fusion_lab/music_dna/__init__.py`
- Test: `fusion_lab/tests/test_music_dna_model.py`

**Interfaces:**
- Consumes: standard library only.
- Produces: `RangeBand`, `FeatureVector`, `HardConstraint`, `GenreDecision`, `DecisionState`, `MusicDNAReport`, and DNA dataclasses used by all later tasks.

- [ ] **Step 1: Write failing tests for bounded values and immutable decision/report models**

Tests must prove:
- probabilities outside `[0.0, 1.0]` raise `ValueError`;
- `RangeBand(minimum, preferred_minimum, preferred_maximum, maximum)` rejects inverted bounds;
- `DecisionState` exposes exactly `ALLOW`, `MUTATE`, `REJECT`;
- `GenreDecision.reasons` is immutable / tuple-backed;
- `MusicDNAReport` can serialize deterministically through a `to_dict()` method.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m unittest fusion_lab.tests.test_music_dna_model -v`
Expected: FAIL because the package/types do not yet exist.

- [ ] **Step 3: Implement the minimal immutable core models**

Required signatures:

```python
class DecisionState(str, Enum): ...

@dataclass(frozen=True, slots=True)
class RangeBand:
    minimum: float
    preferred_minimum: float
    preferred_maximum: float
    maximum: float
    def normalized_distance(self, value: float) -> float: ...

@dataclass(frozen=True, slots=True)
class FeatureVector:
    values: Mapping[str, float]

@dataclass(frozen=True, slots=True)
class HardConstraint:
    id: str
    required: bool

@dataclass(frozen=True, slots=True)
class GenreDecision:
    state: DecisionState
    genre: str
    reasons: tuple[str, ...]
    distance: float

@dataclass(frozen=True, slots=True)
class MusicDNAReport:
    genre_profile: str
    feature_vector: Mapping[str, float]
    coupling: Mapping[str, float]
    hook_score: Mapping[str, float]
    production_truth: Mapping[str, object]
    decision: GenreDecision
    def to_dict(self) -> dict: ...
```

Define the DNA component dataclasses named in the spec (`HarmonyDNA`, `GuitarDNA`, `BassDNA`, `DrumDNA`, `VocalDNA`, `KeysDNA`, `ArrangementDNA`, `ProductionDNA`, `GenreDNA`) with mappings of feature name to `RangeBand` plus hard constraints where applicable. Keep v1 generic rather than creating one field per possible feature.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `python -m unittest fusion_lab.tests.test_music_dna_model -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/music_dna fusion_lab/tests/test_music_dna_model.py
git commit -m "feat: add music dna core models"
```

---

### Task 2: Deterministic distribution primitives

**Files:**
- Create: `fusion_lab/music_dna/distributions.py`
- Test: `fusion_lab/tests/test_music_dna_model.py`

**Interfaces:**
- Consumes: `RangeBand` from Task 1.
- Produces: `ScalarDistribution`, `CategoricalDistribution`, `blend_range_bands(...)`, `blend_categorical(...)`.

- [ ] **Step 1: Add failing distribution tests**

Tests must prove:
- scalar distribution rejects empty samples and non-finite values;
- categorical weights reject negative values and normalize deterministically;
- identical inputs always return identical summaries;
- `blend_range_bands` preserves outer min/max and weighted preferred center deterministically.

- [ ] **Step 2: Run focused test and verify RED**

Run: `python -m unittest fusion_lab.tests.test_music_dna_model -v`
Expected: FAIL on missing distribution APIs.

- [ ] **Step 3: Implement minimal deterministic distributions**

Required signatures:

```python
@dataclass(frozen=True, slots=True)
class ScalarDistribution:
    samples: tuple[float, ...]
    def median(self) -> float: ...
    def to_range_band(self) -> RangeBand: ...

@dataclass(frozen=True, slots=True)
class CategoricalDistribution:
    weights: Mapping[str, float]
    def normalized(self) -> Mapping[str, float]: ...

def blend_range_bands(weighted: Sequence[tuple[float, RangeBand]]) -> RangeBand: ...
def blend_categorical(weighted: Sequence[tuple[float, Mapping[str, float]]]) -> Mapping[str, float]: ...
```

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest fusion_lab.tests.test_music_dna_model -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/music_dna/distributions.py fusion_lab/tests/test_music_dna_model.py
git commit -m "feat: add deterministic music dna distributions"
```

---

### Task 3: Seed corpus and seven genre profiles

**Files:**
- Create: `fusion_lab/music_dna/corpus.py`
- Create: `fusion_lab/music_dna/genre_profiles.py`
- Create: `fusion_lab/data/music_dna/corpus.json`
- Create: all seven `fusion_lab/data/music_dna/genres/*.json`
- Test: `fusion_lab/tests/test_music_dna_profiles.py`

**Interfaces:**
- Consumes: Task 1 DNA models and Task 2 range/distribution primitives.
- Produces: `CorpusObservation`, `load_corpus(path)`, `load_genre_profile(path)`, `load_seed_genre_profiles(root)`.

- [ ] **Step 1: Write failing tests for corpus/profile loading**

Tests must prove:
- the seven required IDs load: `THRASH_CLASSIC`, `BLACK_METAL_CLASSIC`, `DEATH_METAL_CLASSIC`, `DOOM_METAL_CLASSIC`, `PUNK_CLASSIC`, `GLAM_METAL_CLASSIC`, `PROGRESSIVE_METAL_CLASSIC`;
- thrash tempo outer range includes `175..225` from the approved spec;
- classic thrash blast prior remains near-zero relative to death/black profiles;
- black metal palm-mute preferred range is lower than thrash;
- doom attack-density preferred range is lower than thrash;
- malformed profile with a missing required component fails loudly;
- corpus observations retain provenance fields but do not contain full tab/score payload keys.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `python -m unittest fusion_lab.tests.test_music_dna_profiles -v`
Expected: FAIL because loaders/data do not yet exist.

- [ ] **Step 3: Implement loaders and curated aggregate seed data**

Required signatures:

```python
@dataclass(frozen=True, slots=True)
class CorpusObservation:
    genre: str
    artist: str
    track: str
    features: Mapping[str, float]
    provenance: tuple[str, ...]

def load_corpus(path: Path) -> tuple[CorpusObservation, ...]: ...
def load_genre_profile(path: Path) -> GenreDNA: ...
def load_seed_genre_profiles(root: Path) -> Mapping[str, GenreDNA]: ...
```

Seed only aggregate/range data approved in the spec/research. Do not add copyrighted note sequences.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest fusion_lab.tests.test_music_dna_profiles -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/music_dna/corpus.py fusion_lab/music_dna/genre_profiles.py fusion_lab/data/music_dna fusion_lab/tests/test_music_dna_profiles.py
git commit -m "feat: seed seven music dna genre profiles"
```

---

### Task 4: Symbolic feature extraction from existing hosts

**Files:**
- Create: `fusion_lab/music_dna/feature_extractors.py`
- Test: `fusion_lab/tests/test_music_dna_features.py`

**Interfaces:**
- Consumes: `HostComposition`, `NoteEvent`, `FeatureVector`.
- Produces: `extract_host_features(host) -> FeatureVector` and role helpers.

- [ ] **Step 1: Write failing synthetic-fixture tests**

Create small legal synthetic hosts in the test module and prove:
- synthetic thrash yields high pedal-note ratio, palm-mute ratio, and downpick-articulation proxy;
- synthetic black fixture yields high tremolo ratio and low palm-mute ratio;
- synthetic doom yields low attack density and high sustain ratio;
- synthetic prog fixture reports meter/odd-grouping evidence when section metadata/fixture representation supplies it;
- extraction is deterministic for a fixed host.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `python -m unittest fusion_lab.tests.test_music_dna_features -v`
Expected: FAIL on missing extractor.

- [ ] **Step 3: Implement feature extraction**

Required signatures:

```python
def extract_role_features(host: HostComposition, role: str) -> Mapping[str, float]: ...
def extract_harmony_features(host: HostComposition) -> Mapping[str, float]: ...
def extract_arrangement_features(host: HostComposition) -> Mapping[str, float]: ...
def extract_host_features(host: HostComposition) -> FeatureVector: ...
```

Use timing/pitch/articulation/function data already present. Do not infer string/fret/pick direction yet; those arrive in Task 10.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest fusion_lab.tests.test_music_dna_features -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/music_dna/feature_extractors.py fusion_lab/tests/test_music_dna_features.py
git commit -m "feat: extract symbolic music dna features"
```

---

### Task 5: Cross-instrument coupling metrics

**Files:**
- Create: `fusion_lab/music_dna/coupling.py`
- Test: `fusion_lab/tests/test_music_dna_coupling.py`

**Interfaces:**
- Consumes: `HostComposition`.
- Produces: `extract_coupling_features(host, tolerance_ticks=...) -> Mapping[str, float]`.

- [ ] **Step 1: Write failing timing-based coupling tests**

Tests must distinguish:
- high guitar/kick onset lock;
- equally dense but phase-shifted drums yielding low guitar/kick lock;
- bass/guitar lock separately from bass/kick lock;
- snare-to-guitar-accent and section-density contrast metrics are deterministic.

- [ ] **Step 2: Run focused test and verify RED**

Run: `python -m unittest fusion_lab.tests.test_music_dna_coupling -v`
Expected: FAIL on missing coupling API.

- [ ] **Step 3: Implement timing coincidence helpers**

Required signature:

```python
def extract_coupling_features(host: HostComposition, *, tolerance_ticks: int = 30) -> Mapping[str, float]: ...
```

Coincidence ratios must operate on normalized onset sets; do not use raw event-count similarity.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest fusion_lab.tests.test_music_dna_coupling -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/music_dna/coupling.py fusion_lab/tests/test_music_dna_coupling.py
git commit -m "feat: measure whole-band music dna coupling"
```

---

### Task 6: Hook / motif scoring with anti-loop penalties

**Files:**
- Create: `fusion_lab/music_dna/hook_score.py`
- Test: `fusion_lab/tests/test_music_dna_hook_score.py`

**Interfaces:**
- Consumes: rhythm-guitar `NoteEvent` sequences + ticks-per-beat / meter.
- Produces: `HookScore`, `score_hook(...)`.

- [ ] **Step 1: Write failing motif tests**

Fixtures must prove:
- a 4-bar motif with controlled phrase-end mutation scores higher than unrelated random bars;
- a repeated 1-bar cycle copied unchanged through 8+ bars receives an exact-cycle penalty;
- recurrence and mutation are separate reported values;
- uniform attack density is penalized relative to a stable motif with a turnaround.

- [ ] **Step 2: Run focused test and verify RED**

Run: `python -m unittest fusion_lab.tests.test_music_dna_hook_score -v`
Expected: FAIL on missing scorer.

- [ ] **Step 3: Implement deterministic hook score**

Required signatures:

```python
@dataclass(frozen=True, slots=True)
class HookScore:
    recurrence: float
    mutation: float
    rhythmic_identity: float
    contour_recurrence: float
    rest_recurrence: float
    exact_cycle_penalty: float
    total: float

def score_hook(events: Sequence[NoteEvent], *, ticks_per_beat: int, beats_per_bar: int) -> HookScore: ...
```

Keep the score heuristic and explainable; no ML model.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest fusion_lab.tests.test_music_dna_hook_score -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/music_dna/hook_score.py fusion_lab/tests/test_music_dna_hook_score.py
git commit -m "feat: add deterministic riff hook scoring"
```

---

### Task 7: Explainable genre validator and report generation

**Files:**
- Create: `fusion_lab/music_dna/validator.py`
- Test: `fusion_lab/tests/test_music_dna_validator.py`

**Interfaces:**
- Consumes: `GenreDNA`, `FeatureVector`, coupling mapping, `HookScore`, optional production-truth evidence.
- Produces: `validate_genre(...) -> GenreDecision`, `build_music_dna_report(...) -> MusicDNAReport`.

- [ ] **Step 1: Write failing decision tests**

Tests must prove:
- in-band synthetic thrash returns `ALLOW`;
- low hook recurrence + low kick coupling returns `MUTATE` with both explicit reason codes;
- hard production contradiction returns `REJECT`;
- decisions are deterministic and reason ordering is stable.

- [ ] **Step 2: Run focused test and verify RED**

Run: `python -m unittest fusion_lab.tests.test_music_dna_validator -v`
Expected: FAIL on missing validator.

- [ ] **Step 3: Implement weighted normalized distance + hard constraints**

Required signatures:

```python
def validate_genre(
    profile: GenreDNA,
    features: FeatureVector,
    coupling: Mapping[str, float],
    hook: HookScore,
    *,
    production_truth: Mapping[str, object] | None = None,
) -> GenreDecision: ...

def build_music_dna_report(...) -> MusicDNAReport: ...
```

Reason IDs must be machine-stable strings, e.g. `riff_hook_recurrence_below_range`, `guitar_kick_coupling_below_range`, `palm_mute_ratio_below_range`.

- [ ] **Step 4: Verify milestone suite**

Run:
```bash
python -m unittest \
  fusion_lab.tests.test_music_dna_model \
  fusion_lab.tests.test_music_dna_profiles \
  fusion_lab.tests.test_music_dna_features \
  fusion_lab.tests.test_music_dna_coupling \
  fusion_lab.tests.test_music_dna_hook_score \
  fusion_lab.tests.test_music_dna_validator -v
```
Expected: PASS. This is the first useful milestone from the spec: existing hosts can now be classified before renderer changes.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/music_dna/validator.py fusion_lab/tests/test_music_dna_validator.py
git commit -m "feat: validate compositions against genre dna"
```

---

### Task 8: Genre blending with explicit conflict handling

**Files:**
- Create: `fusion_lab/music_dna/blend.py`
- Test: `fusion_lab/tests/test_music_dna_blend.py`

**Interfaces:**
- Consumes: weighted `GenreDNA` profiles and Task 2 blend primitives.
- Produces: `BlendConflict`, `blend_genres(...)`.

- [ ] **Step 1: Write failing blend tests**

Tests must prove:
- `60% THRASH + 25% BLACK + 15% PROG` returns deterministic weighted ranges;
- weights must be positive and normalize to 1.0;
- compatible soft ranges interpolate;
- incompatible hard requirements return conflict IDs rather than averaging them away.

- [ ] **Step 2: Run focused test and verify RED**

Run: `python -m unittest fusion_lab.tests.test_music_dna_blend -v`
Expected: FAIL on missing blend API.

- [ ] **Step 3: Implement explicit blending**

Required signatures:

```python
@dataclass(frozen=True, slots=True)
class BlendConflict:
    id: str
    profiles: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class BlendResult:
    profile: GenreDNA | None
    conflicts: tuple[BlendConflict, ...]

def blend_genres(weighted_profiles: Sequence[tuple[float, GenreDNA]]) -> BlendResult: ...
```

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest fusion_lab.tests.test_music_dna_blend -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/music_dna/blend.py fusion_lab/tests/test_music_dna_blend.py
git commit -m "feat: blend music dna genre distributions"
```

---

### Task 9: Production-truth evidence and refusal gates

**Files:**
- Create: `fusion_lab/music_dna/production_truth.py`
- Modify: `fusion_lab/production_model.py`
- Modify: `fusion_lab/production_render.py`
- Test: `fusion_lab/tests/test_music_dna_production_truth.py`

**Interfaces:**
- Consumes: `ProductionDNA`, tone profile/instrument profile/render topology evidence.
- Produces: `ProductionEvidence`, `validate_production_truth(...)`.

- [ ] **Step 1: Write failing production-truth tests**

Tests must prove:
- `cabinet_ir=None` rejects a profile declaring cabinet mandatory;
- gain + EQ + generic `asoftclip` without explicit amp-stage evidence cannot satisfy `amp_distortion_required`;
- a topology containing source -> boost -> amp/preamp -> cabinet/IR -> post-EQ passes the structural requirement;
- palm-mute and sustain routes with identical source/topology/envelope evidence are rejected as non-distinct;
- L/R tracks with identical performance identity are rejected even if panned differently;
- manifests expose the actual topology evidence, not only knob values.

- [ ] **Step 2: Run focused test and verify RED**

Run: `python -m unittest fusion_lab.tests.test_music_dna_production_truth -v`
Expected: FAIL because evidence types / checks do not exist.

- [ ] **Step 3: Add production evidence model**

Required signatures:

```python
@dataclass(frozen=True, slots=True)
class ProductionEvidence:
    stages: tuple[str, ...]
    cabinet_ir: str | None
    amp_stage: str | None
    distortion_stage: str | None
    palm_mute_identity: str | None
    sustain_identity: str | None
    left_performance_id: str | None
    right_performance_id: str | None

def validate_production_truth(profile: ProductionDNA, evidence: ProductionEvidence) -> tuple[str, ...]: ...
```

Extend existing production model/render manifest structures only enough to carry truthful evidence. Do not invent fake amp evidence for the current soft-clip path.

- [ ] **Step 4: Verify focused tests and existing tone tests**

Run:
```bash
python -m unittest \
  fusion_lab.tests.test_music_dna_production_truth \
  fusion_lab.tests.test_tone_truth \
  fusion_lab.tests.test_mix_truth \
  fusion_lab.tests.test_articulation_sfz_routing -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/music_dna/production_truth.py fusion_lab/production_model.py fusion_lab/production_render.py fusion_lab/tests/test_music_dna_production_truth.py
git commit -m "feat: enforce truthful metal production topology"
```

---

### Task 10: Rich performance events and compatibility adapters

**Files:**
- Create: `fusion_lab/music_dna/performance.py`
- Test: `fusion_lab/tests/test_music_dna_performance.py`

**Interfaces:**
- Consumes: current `NoteEvent`.
- Produces: rich performance events + deterministic conversion adapters back to `NoteEvent`.

- [ ] **Step 1: Write failing event/adaptor tests**

Tests must prove:
- guitar event can represent string, fret, pick direction, palm-mute amount, accent, technique, chord shape, phrase role;
- bass/drum/vocal/keys event types match the approved spec fields;
- conversion to `NoteEvent` preserves timing/pitch/velocity/articulation/function deterministically;
- invalid guitar fret/string combinations are rejected when both are supplied;
- conversion does not silently invent unknown performance semantics.

- [ ] **Step 2: Run focused test and verify RED**

Run: `python -m unittest fusion_lab.tests.test_music_dna_performance -v`
Expected: FAIL on missing performance API.

- [ ] **Step 3: Implement immutable event types and adapters**

Required exported names:
`GuitarPerformanceEvent`, `BassPerformanceEvent`, `DrumPerformanceEvent`, `VocalPerformanceEvent`, `KeyPerformanceEvent`, `guitar_to_note_event`, `bass_to_note_event`, `drum_to_note_event`, `keys_to_note_event`.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest fusion_lab.tests.test_music_dna_performance -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/music_dna/performance.py fusion_lab/tests/test_music_dna_performance.py
git commit -m "feat: add instrument performance semantics"
```

---

### Task 11: Chainsaw Diplomacy thrash DNA integration

**Files:**
- Modify: `fusion_lab/chainsaw_diplomacy.py`
- Modify: `fusion_lab/production_pipeline.py`
- Test: `fusion_lab/tests/test_chainsaw_music_dna.py`

**Interfaces:**
- Consumes: `THRASH_CLASSIC`, Tasks 4–7 validators, Task 10 performance semantics where applicable.
- Produces: `analyze_chainsaw_music_dna(host) -> MusicDNAReport`; optional deterministic mutation entry point only for reason codes covered by tests.

- [ ] **Step 1: Write failing Chainsaw acceptance tests**

Tests must prove:
- Chainsaw produces a deterministic DNA report;
- it cannot be accepted solely because BPM is 192 or events contain `PALM_MUTE` labels;
- no fixed 3-bar short cycle can pass the hook gate across a long section;
- hook recurrence and phrase-end mutation are both checked;
- guitar/kick coupling is checked against the thrash profile band;
- report reason codes explain every mutation/rejection;
- report JSON matches the required minimum fields from the spec.

- [ ] **Step 2: Run focused test and verify RED**

Run: `python -m unittest fusion_lab.tests.test_chainsaw_music_dna -v`
Expected: FAIL on missing integration/report path.

- [ ] **Step 3: Implement Chainsaw analysis/report path**

Required signature:

```python
def analyze_chainsaw_music_dna(host: HostComposition) -> MusicDNAReport: ...
```

`production_pipeline.py` must write `music-dna-report.json` next to the production manifest whenever host-003 is rendered or validated.

Do not yet permit full-mix render promotion based only on this symbolic report; Task 12 adds the isolated guitar gate.

- [ ] **Step 4: Verify GREEN**

Run:
```bash
python -m unittest \
  fusion_lab.tests.test_chainsaw_diplomacy \
  fusion_lab.tests.test_chainsaw_music_dna -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/chainsaw_diplomacy.py fusion_lab/production_pipeline.py fusion_lab/tests/test_chainsaw_music_dna.py
git commit -m "feat: validate Chainsaw against thrash music dna"
```

---

### Task 12: Isolated rhythm-guitar gate and V5 render path

**Files:**
- Modify: `fusion_lab/production_pipeline.py`
- Modify: `fusion_lab/cli.py`
- Create: `scripts/render_chainsaw_pit_v5.sh`
- Test: `fusion_lab/tests/test_chainsaw_isolated_guitar_gate.py`

**Interfaces:**
- Consumes: Chainsaw DNA report, `ProductionEvidence`, production-truth validator.
- Produces: staged render decision and V5 CLI/script path that refuses the full instrumental until isolated rhythm guitar passes both symbolic and production-truth gates.

- [ ] **Step 1: Write failing staged-render tests**

Tests must prove:
- `MUTATE`/`REJECT` Music DNA decisions block isolated render promotion;
- missing amp/cabinet evidence blocks isolated-guitar acceptance;
- non-distinct palm-mute/sustain evidence blocks acceptance;
- identical L/R performance identities block acceptance;
- failed isolated guitar acceptance prevents bass/drum/full mix render call path;
- accepted isolated guitar evidence permits downstream render path;
- a `PENDING_HUMAN_REVIEW` marker remains required before final promotion.

- [ ] **Step 2: Run focused test and verify RED**

Run: `python -m unittest fusion_lab.tests.test_chainsaw_isolated_guitar_gate -v`
Expected: FAIL because staged gate does not yet exist.

- [ ] **Step 3: Implement staged gate API and CLI exposure**

Required signatures:

```python
@dataclass(frozen=True, slots=True)
class IsolatedGuitarGate:
    accepted: bool
    reasons: tuple[str, ...]
    human_review_state: str

def evaluate_isolated_guitar_gate(report: MusicDNAReport, evidence: ProductionEvidence) -> IsolatedGuitarGate: ...
```

Add CLI support for validating/rendering host-003 through the staged gate. `scripts/render_chainsaw_pit_v5.sh` must fail fast if symbolic or production-truth gates fail and must not print a success banner for a refused full render.

- [ ] **Step 4: Verify focused integration**

Run:
```bash
python -m unittest \
  fusion_lab.tests.test_chainsaw_isolated_guitar_gate \
  fusion_lab.tests.test_chainsaw_music_dna \
  fusion_lab.tests.test_music_dna_production_truth -v
```
Expected: PASS.

- [ ] **Step 5: Run the full suite**

Run: `python -m unittest discover -s fusion_lab/tests -v`
Expected: all tests PASS. Any unrelated pre-existing failure must be reported by exact test name before claiming completion.

- [ ] **Step 6: Run a real local V5 acceptance render only if truthful amp/cabinet assets exist**

Run: `bash scripts/render_chainsaw_pit_v5.sh`
Expected one of:
- truthful staged success through isolated guitar and downstream render; or
- explicit refusal reason such as missing cabinet/amp evidence. A refusal is correct behavior when assets are insufficient.

- [ ] **Step 7: Commit**

```bash
git add fusion_lab/production_pipeline.py fusion_lab/cli.py scripts/render_chainsaw_pit_v5.sh fusion_lab/tests/test_chainsaw_isolated_guitar_gate.py
git commit -m "feat: gate Chainsaw V5 behind isolated guitar truth"
```

---

## Final Verification

After all tasks:

- [ ] Run `python -m unittest discover -s fusion_lab/tests -v` and record total passed / failed.
- [ ] Run `git diff --check`.
- [ ] Confirm all seven profile JSON files deserialize.
- [ ] Confirm `music-dna-report.json` is deterministic for two repeated analyses of the same host.
- [ ] Confirm the current fake soft-clip-only guitar topology is **rejected** when the thrash profile requires real amp/cab evidence.
- [ ] Confirm full Chainsaw rendering cannot proceed until isolated rhythm guitar passes symbolic + production truth + human-review gating.
- [ ] Review the branch diff against `docs/superpowers/specs/2026-10-01-music-dna-genre-engine-design.md` and list any intentionally deferred items.
