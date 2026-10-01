# Music DNA Genre Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic whole-band Music DNA subsystem that extracts genre features, ingests legal symbolic sources, validates compositions against seven genre distributions, enforces cross-instrument and production-truth rules, and gates Chainsaw Diplomacy behind an isolated-guitar acceptance path.

**Architecture:** Add a focused `fusion_lab/music_dna/` package around the existing `HostComposition` / `NoteEvent` model. The first milestone classifies existing compositions before renderer changes; later tasks add legal symbolic ingestion, richer performance semantics, truthful configurable amp/cab stage execution, and staged Chainsaw V5 rendering.

**Tech Stack:** Python 3, standard library dataclasses/enums/json/xml, existing `mido`, existing `unittest`, existing Fusion Lab production pipeline, `sfizz_render`, ffmpeg, existing configurable tone-stage execution.

**Spec:** `docs/superpowers/specs/2026-10-01-music-dna-genre-engine-design.md`

## Global Constraints

- Never persist or emit complete copyrighted third-party tabs, scores, melodies, or lyrics.
- No cloud inference requirement.
- Genre identities are distributions and relationships, not fixed recipes.
- Seed genres: thrash, black, death, doom, punk, glam, progressive metal.
- Decisions are deterministic `ALLOW|MUTATE|REJECT` with stable reason codes.
- Input volume is not amplifier gain; generic tanh soft clipping alone cannot satisfy `amp_distortion_required`.
- Cabinet/IR evidence is mandatory when the selected profile requires conventional amplified-guitar tone.
- Palm-mute and sustain routes must be measurably distinct.
- L/R rhythm tracks must be distinct performances preserving riff identity.
- Every analyzed host can emit deterministic `music-dna-report.json`.
- Full Chainsaw rendering is blocked until isolated rhythm guitar passes symbolic + production truth + human review gates.

## Review Focus

1. Malformed/incomplete profile data must fail loudly, not silently default.
2. Dense-but-unrelated instruments must not fake coupling through event counts.
3. Short exact loops must not game hook recurrence.
4. Metadata must not claim amp/cab authenticity without executed-stage evidence.
5. Genre blends with contradictory hard requirements must report conflicts rather than average them.

---

### Task 1: Core DNA models

**Files:** Create `fusion_lab/music_dna/model.py`, `fusion_lab/music_dna/__init__.py`; test `fusion_lab/tests/test_music_dna_model.py`.

**Produces:** `RangeBand`, `FeatureVector`, `HardConstraint`, `DecisionState`, `GenreDecision`, `MusicDNAReport`, `HarmonyDNA`, `GuitarDNA`, `BassDNA`, `DrumDNA`, `VocalDNA`, `KeysDNA`, `ArrangementDNA`, `ProductionDNA`, `GenreDNA`.

- [ ] Write failing tests for bounded probabilities/ranges, immutable reason tuples, exact decision enum values, deterministic `MusicDNAReport.to_dict()`.
- [ ] Run `python -m unittest fusion_lab.tests.test_music_dna_model -v`; expect RED because package/types are missing.
- [ ] Implement immutable models. Required: `RangeBand.normalized_distance(value: float) -> float` and `MusicDNAReport.to_dict() -> dict`.
- [ ] Re-run focused tests; expect PASS.
- [ ] Commit `feat: add music dna core models`.

### Task 2: Deterministic distributions

**Files:** Create `fusion_lab/music_dna/distributions.py`; extend `test_music_dna_model.py`.

**Produces:** `ScalarDistribution`, `CategoricalDistribution`, `blend_range_bands`, `blend_categorical`.

- [ ] Write failing tests for empty/non-finite scalar samples, negative categorical weights, deterministic normalization, weighted range blending.
- [ ] Run focused test; verify RED.
- [ ] Implement the four exported APIs using deterministic ordering only.
- [ ] Verify GREEN.
- [ ] Commit `feat: add deterministic music dna distributions`.

### Task 3: Corpus, provenance, and seven seed genre profiles

**Files:** Create `fusion_lab/music_dna/corpus.py`, `genre_profiles.py`, `fusion_lab/data/music_dna/corpus.json`, seven `genres/*.json`; test `test_music_dna_profiles.py`.

**Produces:** `CorpusObservation`, `load_corpus(path)`, `load_genre_profile(path)`, `load_seed_genre_profiles(root)`.

- [ ] Write failing tests proving all seven profile IDs load, malformed profiles fail, provenance is retained, no raw-score/tab payload keys are stored, thrash tempo envelope includes 175–225 BPM, black palm-mute band is lower than thrash, doom attack density is lower than thrash, classic thrash blast prior is lower than black/death.
- [ ] Run focused tests; verify RED.
- [ ] Seed only aggregate/range observations from the approved research/spec.
- [ ] Verify GREEN.
- [ ] Commit `feat: seed music dna corpus and genre profiles`.

### Task 4: Legal symbolic-source ingestion

**Files:** Create `fusion_lab/music_dna/ingest.py`; test `fusion_lab/tests/test_music_dna_ingest.py`.

**Consumes:** User-owned/permissively licensed MIDI or MusicXML, or existing Polly hosts.

**Produces:** `ingest_midi(path) -> HostComposition`, `ingest_musicxml(path) -> HostComposition`, `summarize_symbolic_source(host, provenance) -> CorpusObservation`.

- [ ] Write failing tests using tiny synthetic MIDI and MusicXML fixtures created inside the tests.
- [ ] Tests must prove tempo, meter, pitch/timing events, and provenance survive ingestion; unsupported/ambiguous constructs return explicit errors; output corpus summaries contain aggregate features only, not a serialized complete score.
- [ ] Run `python -m unittest fusion_lab.tests.test_music_dna_ingest -v`; verify RED.
- [ ] Implement MIDI via existing `mido`; implement the minimal MusicXML subset needed for notes/rests/durations/tempo/meter using standard XML parsing. Reject unsupported constructs rather than guessing.
- [ ] Verify GREEN and commit `feat: ingest legal symbolic music sources`.

### Task 5: Symbolic feature extraction

**Files:** Create `fusion_lab/music_dna/feature_extractors.py`; test `test_music_dna_features.py`.

**Produces:** `extract_role_features`, `extract_harmony_features`, `extract_arrangement_features`, `extract_host_features(host) -> FeatureVector`.

- [ ] Write synthetic thrash/black/doom/prog fixtures proving pedal/palm-mute/downpick proxy, tremolo/low-mute, low-density/high-sustain, and odd-meter evidence respectively.
- [ ] Verify RED.
- [ ] Implement extraction from current `HostComposition`/`NoteEvent`; do not invent string/fret/pick semantics yet.
- [ ] Verify GREEN and deterministic repeated extraction.
- [ ] Commit `feat: extract symbolic music dna features`.

### Task 6: Cross-instrument coupling

**Files:** Create `fusion_lab/music_dna/coupling.py`; test `test_music_dna_coupling.py`.

**Produces:** `extract_coupling_features(host, tolerance_ticks=30) -> Mapping[str,float]`.

- [ ] Write failing tests separating true guitar/kick onset lock from equally dense phase-shifted drums; independently test bass/guitar and bass/kick lock; test section density contrast.
- [ ] Verify RED.
- [ ] Implement normalized onset coincidence metrics, never raw event-count similarity.
- [ ] Verify GREEN.
- [ ] Commit `feat: measure whole-band music dna coupling`.

### Task 7: Hook and motif scoring

**Files:** Create `fusion_lab/music_dna/hook_score.py`; test `test_music_dna_hook_score.py`.

**Produces:** `HookScore`, `score_hook(events, ticks_per_beat, beats_per_bar)`.

- [ ] Write failing fixtures showing 4-bar motif + phrase-end mutation scores above random bars; exact 1-bar loop across 8+ bars incurs a penalty; recurrence and mutation remain separate outputs.
- [ ] Verify RED.
- [ ] Implement recurrence, rhythmic fingerprint, contour recurrence, rest recurrence, mutation, exact-cycle penalty, and total.
- [ ] Verify GREEN.
- [ ] Commit `feat: score riff hooks and phrase mutation`.

### Task 8: Explainable genre validator and report

**Files:** Create `fusion_lab/music_dna/validator.py`; test `test_music_dna_validator.py`.

**Produces:** `validate_genre(profile, features, coupling, hook, production_truth=None) -> GenreDecision`; `build_music_dna_report(...) -> MusicDNAReport`.

- [ ] Write failing tests: in-band synthetic thrash => `ALLOW`; low hook + low kick coupling => `MUTATE` with both stable reasons; hard contradiction => `REJECT`; reason ordering deterministic.
- [ ] Verify RED.
- [ ] Implement weighted normalized distance plus hard constraints.
- [ ] Run the entire Music DNA symbolic milestone suite (Tasks 1–8); expect PASS.
- [ ] Commit `feat: validate compositions against genre dna`.

### Task 9: Genre blending

**Files:** Create `fusion_lab/music_dna/blend.py`; test `test_music_dna_blend.py`.

**Produces:** `BlendConflict`, `BlendResult`, `blend_genres(weighted_profiles)`.

- [ ] Write failing test for 60% thrash + 25% black + 15% prog; test deterministic normalized weights; compatible soft ranges interpolate; incompatible hard requirements produce conflict IDs.
- [ ] Verify RED.
- [ ] Implement blending using Task 2 primitives, never blind averaging of hard constraints.
- [ ] Verify GREEN.
- [ ] Commit `feat: blend music dna genre distributions`.

### Task 10: Rich whole-band performance events

**Files:** Create `fusion_lab/music_dna/performance.py`; test `test_music_dna_performance.py`.

**Produces:** `GuitarPerformanceEvent`, `BassPerformanceEvent`, `DrumPerformanceEvent`, `VocalPerformanceEvent`, `KeyPerformanceEvent` plus deterministic adapters back to `NoteEvent`.

- [ ] Write failing tests for guitar string/fret/pick direction/palm-mute amount/accent/technique/chord shape/phrase role and the approved bass/drum/vocal/keys fields.
- [ ] Test invalid string/fret combinations and prove adapters never invent unknown performance semantics.
- [ ] Verify RED.
- [ ] Implement immutable event types and adapters.
- [ ] Verify GREEN.
- [ ] Commit `feat: add whole-band performance semantics`.

### Task 11: Production-truth evidence

**Files:** Create `fusion_lab/music_dna/production_truth.py`; modify `production_model.py`, `production_render.py`; test `test_music_dna_production_truth.py`.

**Produces:** `ProductionEvidence`, `validate_production_truth(profile, evidence) -> tuple[str,...]`.

- [ ] Write failing tests: missing cabinet rejects cabinet-required profile; input gain + EQ + generic softclip cannot satisfy amp truth; identical palm-mute/sustain identities reject; identical L/R performance IDs reject; manifest exposes executed topology evidence.
- [ ] Verify RED.
- [ ] Add evidence fields without falsely blessing the existing softclip-only path.
- [ ] Run production-truth + existing tone/mix/articulation tests; expect PASS.
- [ ] Commit `feat: enforce truthful production evidence`.

### Task 12: Configurable real amp/cab stage execution

**Files:** Modify `fusion_lab/production_model.py`, `production_render.py`; create/update `fusion_lab/data/production/tone-profiles.json`; test `fusion_lab/tests/test_real_amp_cab_chain.py`.

**Consumes:** Existing `ToneStage(executable,args,asset_path)` mechanism plus installed local executables/assets.

**Produces:** Executed stage evidence for `boost`, `preamp_or_amp`, `cabinet_ir`, `post_eq`; explicit refusal if required local executable/IR is unavailable.

- [ ] Write failing tests with a harmless fake executable/fixture chain proving stage order is executed and recorded; missing required amp or cabinet asset must refuse before render.
- [ ] Verify RED.
- [ ] Implement stage classification/evidence around the existing external-stage runner instead of faking an amp with volume + tanh.
- [ ] Configure thrash tone profile to reference a real local amp/preamp stage and cabinet IR **only when verified installed**; otherwise leave the profile refusing with an actionable reason rather than inventing an asset.
- [ ] Verify GREEN plus existing tone tests.
- [ ] Commit `feat: execute truthful amp and cabinet stages`.

### Task 13: Chainsaw Diplomacy Music DNA integration

**Files:** Modify `fusion_lab/chainsaw_diplomacy.py`, `production_pipeline.py`; test `test_chainsaw_music_dna.py`.

**Produces:** `analyze_chainsaw_music_dna(host) -> MusicDNAReport` and deterministic `music-dna-report.json` writing.

- [ ] Write failing tests proving 192 BPM + `PALM_MUTE` labels alone cannot pass; 3-bar short-cycle repetition cannot pass a long section; hook mutation and guitar/kick coupling are independently required; report contains `genre_profile`, `feature_vector`, `coupling`, `hook_score`, `production_truth`, `decision`, `reasons`.
- [ ] Verify RED.
- [ ] Implement analysis/report path against `THRASH_CLASSIC`.
- [ ] Verify GREEN with existing Chainsaw tests.
- [ ] Commit `feat: validate Chainsaw against thrash music dna`.

### Task 14: Isolated rhythm-guitar gate and Chainsaw V5

**Files:** Modify `production_pipeline.py`, `cli.py`; create `scripts/render_chainsaw_pit_v5.sh`; test `test_chainsaw_isolated_guitar_gate.py`.

**Produces:** `IsolatedGuitarGate`, `evaluate_isolated_guitar_gate(report,evidence)`, staged V5 CLI/script.

- [ ] Write failing tests: symbolic `MUTATE/REJECT` blocks promotion; missing real amp/cab evidence blocks acceptance; non-distinct mute/sustain blocks acceptance; identical L/R performance IDs block acceptance; failed isolated gate prevents bass/drums/full mix; accepted gate permits downstream rendering but leaves final `PENDING_HUMAN_REVIEW`.
- [ ] Verify RED.
- [ ] Implement the staged gate and V5 script. Script must fail fast and never print a success banner on refusal.
- [ ] Run focused integration tests; expect PASS.
- [ ] Run `python -m unittest discover -s fusion_lab/tests -v`; record all failures by exact name.
- [ ] Run `git diff --check`.
- [ ] Run `bash scripts/render_chainsaw_pit_v5.sh`. Correct outcomes are either a truthful isolated-guitar/full render or an explicit refusal because verified local amp/cab assets are missing.
- [ ] Commit `feat: gate Chainsaw V5 behind isolated guitar truth`.

## Final Verification

- [ ] Full unittest discovery reports zero unreported failures.
- [ ] `git diff --check` is clean.
- [ ] All seven genre profiles deserialize deterministically.
- [ ] Synthetic MIDI and MusicXML ingestion is deterministic and stores only aggregate corpus observations.
- [ ] Two analyses of the same host produce identical `music-dna-report.json` content.
- [ ] Current softclip-only topology is rejected when thrash requires real amp/cab evidence.
- [ ] Executed amp/cab stage evidence is present when a truthful render succeeds.
- [ ] Full Chainsaw render is impossible before isolated rhythm guitar passes symbolic, production, and human-review gates.
