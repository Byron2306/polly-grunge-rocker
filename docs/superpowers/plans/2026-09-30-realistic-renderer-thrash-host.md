# Realistic Renderer + CHAINSAW DIPLOMACY Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic, fail-closed, headless production-rendering path for realistic guitar/bass/drums and compose/render `HOST-003: CHAINSAW DIPLOMACY`, a 64-bar, 192 BPM, E-standard stereotypical late-1980s Thrash host suitable for later Byron vocal ablation.

**Architecture:** Preserve the existing composition/event model and FluidSynth GM path as structural/debug authority. Add a separate production renderer that maps deterministic role MIDI plus articulation metadata to pinned SFZ instruments, bounded humanization, role-specific tone chains, stem rendering and a final instrumental mix; no missing production dependency may silently fall back to GM. `CHAINSAW DIPLOMACY` is authored as deterministic event truth and then rendered through data-driven production profiles.

**Tech Stack:** Python 3.11+, `mido`, `sfizz_render` 1.2.3-compatible offline SFZ renderer, FFmpeg/SoX, optional headless amp/cab/IR processing, Python `unittest`, Debian Proot on Termux.

**Spec:** `docs/superpowers/specs/2026-09-30-realistic-renderer-thrash-host-design.md`

## Global Constraints

- `STYLE ≠ FUNCTION` remains non-negotiable.
- `TRAIT ≠ TECHNIQUE ≠ FUNCTION ≠ ROLE` remains non-negotiable.
- `PERFORMANCE TRUTH ≠ TONE` is non-negotiable.
- Existing GM/FluidSynth rendering remains available and backward-compatible as a structural debugger only.
- Production rendering must be deterministic from the same composition, profiles and humanization seed.
- Production rendering must fail closed when sampler/SFZ/sample/tone dependencies are missing.
- Production rendering must never silently fall back to General MIDI.
- Canonical milestone target is Termux + Debian Proot, headless/offline; no X11, DAW GUI, cloud, proprietary license manager or realtime JACK requirement.
- `CHAINSAW DIPLOMACY`: E standard, 192 BPM, 4/4, 64 bars, E-minor/chromatic Thrash language.
- Canonical host excludes drop tuning, djent displacement, slam vocabulary, blast beats and default modern surgical gating.
- Lyrics and canonical human vocals are out of scope until the instrumental master passes Byron's authenticity review.
- No Pattern Map schema changes.

## Review Focus

1. **Silent fallback:** missing SFZ/sampler/tone dependency must refuse production rendering rather than emit GM output.
2. **Humanization leakage:** renderer microtiming/velocity variation must stay within declared bounds and never move sections, tempo, meter, chord roots, riff ordering or phrase length.
3. **Double-track collapse:** left/right rhythm guitars must remain structurally equivalent but independently humanized/rendered, not duplicated byte-identical stems.
4. **Unsupported articulation:** profile/library mismatch such as requested palm mute or lead bend without an available articulation must fail with an actionable diagnostic.
5. **Reproducibility:** same seed and profiles must reproduce the same production manifest and stem hashes; different humanization seeds may change approved renderer-owned details but not structural signatures.

---

## File Structure

### Create

- `fusion_lab/production_model.py` — production instrument, tone, humanization, render and review contracts.
- `fusion_lab/production_render.py` — dependency checks, `sfizz_render` invocation, tone-chain processing, stems, mix and production manifest.
- `fusion_lab/chainsaw_diplomacy.py` — deterministic HOST-003 composition plus articulation metadata and vocal opportunity windows.
- `fusion_lab/data/production/instruments.example.json` — non-secret portable instrument-profile example with user-local path placeholders.
- `fusion_lab/data/production/tone-profiles.json` — initial `THRASH_1988` processing profile.
- `fusion_lab/data/production/chainsaw-diplomacy.json` — host/render metadata and authenticity-review rubric.
- `fusion_lab/tests/test_production_model.py`
- `fusion_lab/tests/test_production_render.py`
- `fusion_lab/tests/test_chainsaw_diplomacy.py`
- `fusion_lab/tests/test_production_cli.py`
- `scripts/setup_fusion_production_proot.sh` — pinned Debian Proot prerequisites and pinned sfizz source-build path.

### Modify

- `fusion_lab/midi_io.py` — deterministic production-role/layer MIDI writing if needed; preserve old interfaces.
- `fusion_lab/cli.py` — production setup-check, compose/render/verify/review commands.
- `fusion_lab/tests/test_gauntlet.py` — production-path regression without requiring external sample libraries.
- `docs/FUSION_LAB.md` — production-render workflow and operator commands.
- `.gitignore` — ignore local instrument packs, generated production outputs and review scratch while preserving committed metadata/templates.

### Generated, Never Hand-Edited

- `fusion_lab/out/host-003/**`
- `fusion_lab/out/production/host-003/**`

### Do Not Commit

- third-party SFZ/sample packs;
- cabinet IR binaries unless licensing explicitly permits repository redistribution;
- user-local absolute instrument paths;
- generated WAV stems/mixes.

---

### Task 1: Production Renderer Domain Contracts

**Files:**
- Create: `fusion_lab/production_model.py`
- Create: `fusion_lab/tests/test_production_model.py`

**Interfaces:**
- Produces:
  - `InstrumentProfile(id:str, role:str, sfz_path:Path, articulations:Mapping[str,ArticulationMap], source_id:str, source_version:str|None=None)`
  - `ArticulationMap(name:str, keyswitch:int|None=None, midi_channel:int|None=None, velocity_min:int=1, velocity_max:int=127)`
  - `HumanizationProfile(seed:int, timing_ms:int, velocity_delta:int, double_track_timing_ms:int, double_track_velocity_delta:int)`
  - `ToneProfile(id:str, stages:tuple[ToneStage,...], pan:float=0.0, width:float=1.0)`
  - `ToneStage(kind:str, executable:str|None, args:tuple[str,...], asset_path:Path|None=None)`
  - `ProductionRoleProfile(role_layer:str, instrument_id:str, tone_profile_id:str, humanization_id:str)`
  - `AuthenticityReview(state:Literal['PASS','ADJUST','REFUSE'], notes:tuple[str,...], rubric:Mapping[str,str])`

- [ ] **Step 1: Write failing production-contract tests**

Assert:
- humanization tolerances are non-negative and bounded;
- pan is `-1..1`, width is positive;
- instrument profile requires a non-empty source ID and articulation mapping;
- review state only accepts `PASS|ADJUST|REFUSE`;
- tone stages never imply musical function or mutate composition metadata.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_production_model -v`
Expected: FAIL because module does not exist.

- [ ] **Step 3: Implement frozen contracts and validation**

Use immutable dataclasses/tuples/mapping proxies. Paths remain external references; no binary assets are bundled.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_production_model -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/production_model.py fusion_lab/tests/test_production_model.py
git commit -m "feat: define production renderer contracts"
```

---

### Task 2: Fail-Closed Offline Production Renderer

**Files:**
- Create: `fusion_lab/production_render.py`
- Create: `fusion_lab/tests/test_production_render.py`

**Interfaces:**
- Consumes Task 1 contracts plus existing role/layer MIDI paths.
- Produces:
  - `check_production_dependencies(config:ProductionConfig) -> None`
  - `render_sfz(midi:Path, sfz:Path, wav:Path, *, sample_rate:int, executable:str='sfizz_render') -> None`
  - `apply_tone_chain(source:Path, destination:Path, profile:ToneProfile) -> None`
  - `render_production_role(...) -> ProductionStem`
  - `mix_production_stems(stems:Mapping[str,Path], mix_path:Path) -> None`
  - `production_manifest(...) -> dict`

- [ ] **Step 1: Write failing renderer-boundary tests**

Pin:
- missing `sfizz_render` -> `PRODUCTION_MISSING_SFIZZ_RENDER`;
- missing `.sfz` -> `PRODUCTION_MISSING_SFZ`;
- missing sample referenced by source profile -> actionable refusal before mix;
- missing tone-stage executable/IR -> refusal;
- no code path invokes FluidSynth/GM when production mode is requested;
- generated command is headless/offline and pins sample rate/output path;
- same manifest inputs produce stable JSON/hash ordering.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_production_render -v`
Expected: FAIL.

- [ ] **Step 3: Implement minimal renderer, post chain and manifest**

Use subprocess invocation only; external executable paths are explicit and validated. FFmpeg/SoX mix is deterministic and separate from composition truth.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_production_render -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/production_render.py fusion_lab/tests/test_production_render.py
git commit -m "feat: add fail-closed production renderer"
```

---

### Task 3: Pinned Debian Proot Toolchain and Local Instrument Profiles

**Files:**
- Create: `scripts/setup_fusion_production_proot.sh`
- Create: `fusion_lab/data/production/instruments.example.json`
- Modify: `.gitignore`
- Modify: `docs/FUSION_LAB.md`

**Interfaces:**
- Produces a reproducible install/check path for:
  - build essentials;
  - FFmpeg/SoX;
  - pinned `sfizz` source version `1.2.3` with `SFIZZ_RENDER=ON` when no compatible binary exists;
  - local `sfizz_render` discovery;
  - operator-owned instrument library root via environment/config.

- [ ] **Step 1: Write shell-contract tests or static assertions in `test_production_render.py`**

Assert setup script:
- pins sfizz version;
- builds only the offline renderer path when source build is needed;
- never downloads or bundles third-party sample libraries automatically;
- prints the exact location of `sfizz_render`;
- refuses success if renderer cannot be found after setup.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_production_render -v`
Expected: new setup-contract tests FAIL.

- [ ] **Step 3: Implement setup script and example profile**

Document that sfizz 1.2.3 is pinned because upstream is archived/read-only; sample-library acquisition remains manual/operator-controlled for licensing reasons. Example profile uses placeholders such as `${FUSION_INSTRUMENT_ROOT}/guitar/...`.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_production_render -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/setup_fusion_production_proot.sh fusion_lab/data/production/instruments.example.json docs/FUSION_LAB.md .gitignore fusion_lab/tests/test_production_render.py
git commit -m "build: add pinned proot production setup"
```

---

### Task 4: Compose HOST-003 `CHAINSAW DIPLOMACY`

**Files:**
- Create: `fusion_lab/chainsaw_diplomacy.py`
- Create: `fusion_lab/tests/test_chainsaw_diplomacy.py`
- Create: `fusion_lab/data/production/chainsaw-diplomacy.json`

**Interfaces:**
- Produces:
  - `build_chainsaw_diplomacy() -> HostComposition`
  - `chainsaw_articulation_map(host:HostComposition) -> Mapping[str,tuple[ArticulationEvent,...]]`
  - `chainsaw_vocal_windows(host:HostComposition) -> tuple[VocalWindow,...]`
  - `chainsaw_review_rubric() -> Mapping[str,str]`

- [ ] **Step 1: Write failing host tests**

Pin:
- ID `host-003-chainsaw-diplomacy`;
- 192 BPM, 4/4, E tonal center, 64 bars;
- exact section form `4,8,4,8,8,8,8,4,8,4`;
- E-standard pitch floor with no drop-tuned extension below E2 guitar fundamental;
- rhythm vocabulary contains downpicked eighths, gallops, palm-muted E pedal, chromatic power-chord movement and open releases;
- pitch vocabulary exercises E/F/F#/G/Bb/B and tritone/diminished pressure;
- bass primarily follows riff with authored fills;
- drums include Thrash/skank, chorus backbeat, double-kick escalation, tom fills and half-time bridge, and contain no blast-beat articulation;
- lead section includes sustained notes, fast run, high-register peak and phrase gaps;
- host contains explicit long, bark, syncopated, cross-bar, call-response and harmony vocal windows.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_chainsaw_diplomacy -v`
Expected: FAIL.

- [ ] **Step 3: Implement deterministic host, articulation metadata and vocal windows**

Keep instrument/sample/tone knowledge out of the composition module.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_chainsaw_diplomacy -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/chainsaw_diplomacy.py fusion_lab/tests/test_chainsaw_diplomacy.py fusion_lab/data/production/chainsaw-diplomacy.json
git commit -m "feat: compose chainsaw diplomacy thrash host"
```

---

### Task 5: Production MIDI/Layers and Bounded Humanization

**Files:**
- Modify: `fusion_lab/midi_io.py`
- Modify: `fusion_lab/tests/test_midi_layers.py`
- Modify: `fusion_lab/tests/test_production_render.py`

**Interfaces:**
- Produces:
  - `write_production_midis(host, articulation_map, out_dir, humanization_profiles) -> Mapping[str,Path]`
  - independent layers `rhythm_guitar_L`, `rhythm_guitar_R`, `bass`, `drums`, `lead_guitar`;
  - stable structural signatures from the unhumanized canonical host;
  - deterministic rendered-performance signatures from `(host, profile, seed)`.

- [ ] **Step 1: Add failing layer/humanization tests**

Assert:
- L/R rhythm layers share canonical note order/roots but are not byte-identical when humanized;
- timing deltas never exceed profile limits;
- velocity deltas never exceed profile limits;
- same seed reproduces same MIDI signatures;
- different seeds may vary renderer-owned timing/velocity while preserving canonical host signature;
- unsupported articulation mapping refuses rather than substituting generic sustain.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_midi_layers fusion_lab.tests.test_production_render -v`
Expected: FAIL.

- [ ] **Step 3: Implement deterministic articulation routing and bounded humanization**

Humanization occurs during production-MIDI export; it must not mutate `HostComposition`.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_midi_layers fusion_lab.tests.test_production_render -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/midi_io.py fusion_lab/tests/test_midi_layers.py fusion_lab/tests/test_production_render.py
git commit -m "feat: add deterministic production layers"
```

---

### Task 6: `THRASH_1988` Tone Profile and Production Mix Contract

**Files:**
- Create: `fusion_lab/data/production/tone-profiles.json`
- Modify: `fusion_lab/production_render.py`
- Modify: `fusion_lab/tests/test_production_render.py`

**Interfaces:**
- Produces initial tone-profile contracts for:
  - rhythm guitar L/R;
  - bass;
  - drums;
  - lead guitar;
- records processing provenance but does not hard-code genre logic into composition.

- [ ] **Step 1: Write failing tone-profile tests**

Pin:
- rhythm guitars hard-ish L/R and use independently addressable processing chains;
- bass centered;
- kick/snare/drums remain centered as permitted by rendered source while stereo drums are preserved if source supplies them;
- lead center/slightly offset with optional ambience;
- tone profile has headroom target and no loudness-maximization stage;
- profile can be swapped without changing host structural signature;
- missing tone asset refuses production render.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_production_render -v`
Expected: FAIL.

- [ ] **Step 3: Implement profile loading and processing/mix contract**

First milestone may use FFmpeg/SoX EQ, convolution/IR and gain/pan stages if a dedicated amp processor is unavailable; profile provenance must explicitly record the chosen path.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_production_render -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/data/production/tone-profiles.json fusion_lab/production_render.py fusion_lab/tests/test_production_render.py
git commit -m "feat: add thrash 1988 production profile"
```

---

### Task 7: Production CLI and Verification Workflow

**Files:**
- Modify: `fusion_lab/cli.py`
- Create: `fusion_lab/tests/test_production_cli.py`
- Modify: `docs/FUSION_LAB.md`

**Interfaces:**
- Adds commands:
  - `production-check --instrument-config <json> --tone-profiles <json>`
  - `compose-host003 --out <dir>`
  - `render-host003-production --midi-dir <dir> --out <dir> --instrument-config <json> --tone-profiles <json> --seed <int>`
  - `verify-host003-production --dir <dir>`
  - `review-host003 --dir <dir> --state PASS|ADJUST|REFUSE --note <text>...`

- [ ] **Step 1: Write failing CLI tests**

Assert:
- `compose-host003` works without production dependencies;
- production commands fail closed when config/assets are absent;
- production render never calls the existing GM renderer;
- verification checks structural signature, production manifest and expected stems;
- review command records state/notes without altering audio/structural evidence;
- only `PASS` marks a production master as `promotion_eligible=true`.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_production_cli -v`
Expected: FAIL.

- [ ] **Step 3: Implement CLI commands and docs**

Keep operator-local instrument paths outside committed configuration.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_production_cli -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/cli.py fusion_lab/tests/test_production_cli.py docs/FUSION_LAB.md
git commit -m "feat: add production render operator workflow"
```

---

### Task 8: Full Regression and Real Proot Production Gate

**Files:**
- Modify: `fusion_lab/tests/test_gauntlet.py`
- Modify: `docs/FUSION_LAB.md`

**Interfaces:**
- Proves old GM experiments and new production architecture coexist.

- [ ] **Step 1: Extend gauntlet tests**

Assert:
- existing Host 001/EXP-001 and THRASH CHIMERA tests remain green;
- production modules contain no cloud/OpenAI/Suno/network runtime dependency;
- production mode has no GM fallback path;
- HOST-003 remains 192 BPM/4/4/64 bars/E standard;
- structural signature is independent of tone profile;
- authenticity review begins unresolved/not promoted.

- [ ] **Step 2: Run repository Fusion Lab regression**

Run: `python -m unittest discover -s fusion_lab/tests -v`
Expected: all tests PASS.

- [ ] **Step 3: Run game regression**

Run:
```bash
npm test
npm run build
```
Expected: PASS.

- [ ] **Step 4: Run real Debian Proot production checks**

Inside Debian Proot:
```bash
scripts/setup_fusion_production_proot.sh
python -m fusion_lab production-check --instrument-config "$FUSION_INSTRUMENT_CONFIG" --tone-profiles fusion_lab/data/production/tone-profiles.json
python -m fusion_lab compose-host003 --out fusion_lab/out/host-003
python -m fusion_lab render-host003-production --midi-dir fusion_lab/out/host-003 --out fusion_lab/out/production/host-003 --instrument-config "$FUSION_INSTRUMENT_CONFIG" --tone-profiles fusion_lab/data/production/tone-profiles.json --seed 1988
python -m fusion_lab verify-host003-production --dir fusion_lab/out/production/host-003
```
Expected: guitar L/R, bass, drums, lead, instrumental mix and production manifest exist; no GM fallback occurred.

- [ ] **Step 5: Byron authenticity review**

Listen to the production instrumental and record `PASS`, `ADJUST`, or `REFUSE` against at least:
- palm-mute punch;
- pick attack realism;
- gallop/downpick plausibility;
- gain/cab character;
- bass attack/body;
- drum naturalism;
- double-track plausibility;
- lead-guitar believability;
- overall Thrash production feel.

Only `PASS` freezes HOST-003 as the vocal-ablation basis.

- [ ] **Step 6: Commit regression/docs updates after machine verification**

```bash
git add fusion_lab/tests/test_gauntlet.py docs/FUSION_LAB.md
git commit -m "test: verify realistic thrash production path"
```

Human authenticity evidence remains an operator artifact until explicitly promoted.

---

## Completion Contract

The milestone is complete only when:

1. legacy Fusion Lab regression is green;
2. HOST-003 is deterministic at 192 BPM, 4/4, 64 bars, E standard;
3. production sampler and tone dependencies are explicit and fail closed;
4. guitar, bass and drums render from realistic non-GM sources;
5. left/right rhythm guitars render independently;
6. palm-muted/open articulation routing is structurally proven and audibly distinguishable;
7. production stems and instrumental mix export headlessly in Debian Proot;
8. production provenance is reproducible from profile + seed;
9. no production dependency silently falls back to GM;
10. Byron records `PASS` before the instrumental master is frozen for lyrics/vocal ablation.
