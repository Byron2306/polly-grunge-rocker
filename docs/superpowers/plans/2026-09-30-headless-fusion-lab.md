# Headless Fusion Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic Termux/Proot-compatible composition laboratory that generates and renders the frozen five-role `GLAMASAURUS REX` host and controlled Experiment 001 variants proving `STYLE ≠ FUNCTION`.

**Architecture:** Canonical laboratory truth lives in Python-authored MIDI/event data. Mido writes isolated role MIDI stems, FluidSynth renders them headlessly, and machine-readable experiment manifests declare frozen and mutated dimensions before variants are generated. Rendered WAV is evidence for listening; MIDI events and manifests remain structural authority.

**Tech Stack:** Python 3.11+, `mido`, Python `unittest`, FluidSynth CLI, General MIDI/SF2 SoundFont supplied by operator, optional FFmpeg/SoX for deterministic mix assembly.

**Spec:** `docs/superpowers/specs/2026-09-30-headless-fusion-lab-design.md`

## Global Constraints

- **STYLE ≠ FUNCTION** is non-negotiable.
- Host 001 is `GLAMASAURUS REX`: `138 BPM`, `4/4`, tonal center `E`.
- Five canonical roles must exist independently: `DRUMS`, `BASS`, `RHYTHM_GUITAR`, `LEAD_KEYS`, `VOCALS`.
- MIDI/event data is canonical structural truth; rendered WAV is not.
- Once the host passes its freeze gate, experiments must never edit canonical host files in place.
- Experiment metadata must explicitly name frozen dimensions and mutated dimensions.
- Core workflow must run without X11/VNC, cloud services, or generative models.
- V1 renderer targets FluidSynth and an operator-provided SoundFont path; no SoundFont binary is committed.
- Existing game/Pattern Map code and tests must remain unchanged and green.

## Review Focus

1. **Host mutation leakage:** B1/B2/C must be rejected if dimensions declared frozen differ from the host beyond the experiment contract.
2. **MIDI determinism:** repeated generation must produce identical normalized event signatures and stable filenames.
3. **Missing headless dependencies:** absent `mido`, `fluidsynth`, or SoundFont path must fail with short actionable diagnostics rather than partial output.
4. **Role isolation:** every role stem must contain only its own channel/events and preserve the shared tempo/meter clock.
5. **Render portability:** byte-identical WAV is not required across FluidSynth versions, but expected stem count, duration tolerance, and source-event identity must remain stable.

---

## File Structure

### Create

- `fusion_lab/requirements.txt` — Python dependency floor (`mido`).
- `fusion_lab/model.py` — canonical note/event, role, section, host, and experiment metadata contracts.
- `fusion_lab/glamasaurus_rex.py` — Host 001 deterministic composition source.
- `fusion_lab/midi_io.py` — deterministic Mido serialization and normalized event signatures.
- `fusion_lab/experiment.py` — frozen-dimension comparison and Experiment 001 mutations.
- `fusion_lab/render.py` — FluidSynth/FFmpeg-or-SoX headless rendering orchestration.
- `fusion_lab/cli.py` — compose, freeze, experiment, render, verify commands.
- `fusion_lab/__main__.py` — `python -m fusion_lab` entrypoint.
- `fusion_lab/tests/test_model.py`
- `fusion_lab/tests/test_host.py`
- `fusion_lab/tests/test_midi_io.py`
- `fusion_lab/tests/test_experiment_001.py`
- `fusion_lab/tests/test_render_contract.py`
- `fusion_lab/tests/test_gauntlet.py`
- `fusion_lab/data/host-001/manifest.json` — generated/frozen host metadata after verification.
- `fusion_lab/data/experiments/exp-001-style-not-function.json` — experiment definition/result shell.
- `docs/FUSION_LAB.md`

### Generated, Never Hand-Edited

- `fusion_lab/out/host-001/*.mid`
- `fusion_lab/out/host-001/*.wav`
- `fusion_lab/out/exp-001/{A,B1,B2,C}/*.mid`
- `fusion_lab/out/exp-001/{A,B1,B2,C}/*.wav`
- `fusion_lab/out/**/mix.wav`

### Do Not Modify

- combat simulation
- Phaser scenes/rendering
- existing Pattern Map schema
- existing Pattern Map authoring contracts

---

### Task 1: Laboratory Domain Model and Deterministic Clock

**Files:**
- Create: `fusion_lab/model.py`
- Create: `fusion_lab/tests/test_model.py`

**Interfaces:**
- Produces:
  - `Role = Literal['DRUMS','BASS','RHYTHM_GUITAR','LEAD_KEYS','VOCALS']`
  - `NoteEvent(start_tick:int, duration_ticks:int, note:int, velocity:int, channel:int, articulation:str|None=None)`
  - `Section(id:str, start_bar:int, bars:int)`
  - `RoleTrack(role:Role, events:tuple[NoteEvent,...], program:int|None, percussion:bool=False)`
  - `HostComposition(id:str, bpm:int, numerator:int, denominator:int, ticks_per_beat:int, sections:tuple[Section,...], tracks:dict[Role,RoleTrack])`
  - `ExperimentDefinition(id:str, host_id:str, role:Role, frozen_dimensions:tuple[str,...], mutated_dimensions:tuple[str,...], hypothesis:str, variants:tuple[str,...])`

- [ ] **Step 1: Write failing contract tests**

Assert:
- exactly five canonical role names;
- `138 BPM`, `4/4`, and positive `ticks_per_beat` are representable;
- invalid note ranges, negative ticks/durations, and velocity outside `1..127` are refused;
- section bar ranges cannot overlap or move backwards.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_model -v`
Expected: FAIL because `fusion_lab.model` does not exist.

- [ ] **Step 3: Implement minimal frozen dataclasses and validation**

Use immutable dataclasses/tuples so experiments cannot mutate host objects accidentally.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_model -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/model.py fusion_lab/tests/test_model.py
git commit -m "feat: define fusion lab musical model"
```

---

### Task 2: Compose Host 001 — GLAMASAURUS REX

**Files:**
- Create: `fusion_lab/glamasaurus_rex.py`
- Create: `fusion_lab/tests/test_host.py`

**Interfaces:**
- Consumes Task 1 model.
- Produces: `build_glamasaurus_rex() -> HostComposition`.

- [ ] **Step 1: Write failing host tests**

Pin:
- `bpm == 138`, meter `4/4`, tonal-center metadata `E`;
- form bar counts: `4,8,4,8,4,8,4,8,8,4,8,4`;
- five non-empty semantic role tracks;
- verse harmony follows `E5 D5 A5 E5 | E5 D5 A5 B5`;
- pre-chorus follows `A B C#m B`;
- chorus follows `E B C#m A | E B A B`;
- drums use straight eighth hats, snare 2/4, simple kick, transition fills, chorus crashes;
- host contains no experiment-only articulation tags (`TREMOLO_TEXTURE`, `DOOM_SUSTAIN`, `D_BEAT`, `BLAST`, `SLAM`, `DJENT_DISPLACEMENT`).

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_host -v`
Expected: FAIL because builder does not exist.

- [ ] **Step 3: Implement deterministic host composition**

Encode harmony/rhythm as named helpers but return only Task 1 contracts. `VOCALS` is a MIDI melody guide, not sung audio.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_host -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/glamasaurus_rex.py fusion_lab/tests/test_host.py
git commit -m "feat: compose glamasaurus rex host"
```

---

### Task 3: Deterministic MIDI Stem Writer and Host Freeze Manifest

**Files:**
- Create: `fusion_lab/requirements.txt`
- Create: `fusion_lab/midi_io.py`
- Create: `fusion_lab/tests/test_midi_io.py`
- Create: `fusion_lab/data/host-001/manifest.json`

**Interfaces:**
- Consumes Task 1/2 composition.
- Produces:
  - `write_role_midis(host:HostComposition, out_dir:Path) -> dict[Role,Path]`
  - `normalized_event_signature(path:Path) -> str`
  - `host_manifest(host:HostComposition, midi_paths:dict[Role,Path]) -> dict`

- [ ] **Step 1: Write failing MIDI tests**

Assert:
- five `.mid` files with deterministic names;
- every file contains the same 138 BPM tempo and 4/4 signature;
- drum data uses MIDI percussion channel 10 (zero-based channel 9);
- non-drum roles do not leak events between channels/tracks;
- two independent generations have identical normalized signatures;
- manifest contains source-event signature per role and host structural signature.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_midi_io -v`
Expected: FAIL before serializer exists.

- [ ] **Step 3: Implement Mido writer/signature logic**

Sort simultaneous events deterministically before writing. Hash normalized event tuples rather than raw MIDI bytes for structural identity.

- [ ] **Step 4: Generate and freeze manifest**

Run: `python -m fusion_lab compose --out fusion_lab/out/host-001` after Task 6 CLI exists; until then tests may call writer directly. Manifest committed only after all host assertions pass.

- [ ] **Step 5: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_midi_io -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add fusion_lab/requirements.txt fusion_lab/midi_io.py fusion_lab/tests/test_midi_io.py fusion_lab/data/host-001/manifest.json
git commit -m "feat: write and freeze fusion host midi stems"
```

---

### Task 4: Experiment 001 Mutations and Frozen-Dimension Guard

**Files:**
- Create: `fusion_lab/experiment.py`
- Create: `fusion_lab/tests/test_experiment_001.py`
- Create: `fusion_lab/data/experiments/exp-001-style-not-function.json`

**Interfaces:**
- Produces:
  - `build_experiment_001(host:HostComposition) -> dict[str,HostComposition]` with `A`, `B1`, `B2`, `C`;
  - `compare_dimensions(host:HostComposition, variant:HostComposition, role:Role) -> dict[str,bool]`;
  - `assert_experiment_contract(definition:ExperimentDefinition, host:HostComposition, variant:HostComposition) -> None`.

- [ ] **Step 1: Write failing mutation tests**

Pin:
- `A` is structurally identical to host;
- `B1` preserves chorus rhythm-guitar pitches, harmony, onset grid, phrase bounds and function, mutating only articulation/density to `TREMOLO_TEXTURE`;
- `B2` preserves host harmony/section timing/function but may change register/voicing, add pedal/drone and repeated upper voice;
- `C` uses the same guest vocabulary at excessive density across broader material;
- every unlisted frozen dimension remains identical;
- deliberately changing B1 harmony or timing makes `assert_experiment_contract()` fail.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_experiment_001 -v`
Expected: FAIL.

- [ ] **Step 3: Implement mutation transforms as pure functions**

Never mutate input host objects. Variants are new immutable compositions.

- [ ] **Step 4: Write experiment metadata**

Machine-readable file must record host ID, target role, frozen dimensions, mutated dimensions, hypothesis, `A/B1/B2/C`, and conclusion status `UNRESOLVED`.

- [ ] **Step 5: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_experiment_001 -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add fusion_lab/experiment.py fusion_lab/tests/test_experiment_001.py fusion_lab/data/experiments/exp-001-style-not-function.json
git commit -m "feat: generate style-not-function experiment"
```

---

### Task 5: Headless FluidSynth Rendering Contract

**Files:**
- Create: `fusion_lab/render.py`
- Create: `fusion_lab/tests/test_render_contract.py`

**Interfaces:**
- Produces:
  - `RenderConfig(soundfont:Path, sample_rate:int=44100, gain:float=0.8)`
  - `check_render_dependencies(config:RenderConfig) -> None`
  - `render_midi(midi:Path, wav:Path, config:RenderConfig) -> None`
  - `render_stems(midi_paths:dict[Role,Path], out_dir:Path, config:RenderConfig) -> dict[Role,Path]`
  - `mix_stems(stems:dict[Role,Path], mix_path:Path) -> None`.

- [ ] **Step 1: Write failing contract tests**

Use fake executable discovery/subprocess adapters where required. Assert:
- missing `fluidsynth` gives `FUSION_RENDER_MISSING_FLUIDSYNTH`;
- nonexistent SoundFont gives `FUSION_RENDER_MISSING_SOUNDFONT`;
- renderer command is non-interactive/headless and pins sample rate/gain;
- five role stems are rendered to stable filenames;
- mix refuses if a canonical stem is missing.

- [ ] **Step 2: Run RED**

Run: `python -m unittest fusion_lab.tests.test_render_contract -v`
Expected: FAIL.

- [ ] **Step 3: Implement rendering orchestration**

Prefer FluidSynth for synthesis. Use FFmpeg or SoX only for summing existing stems; emit an actionable error when neither mixer exists.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest fusion_lab.tests.test_render_contract -v`
Expected: PASS without requiring live audio hardware.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/render.py fusion_lab/tests/test_render_contract.py
git commit -m "feat: render fusion lab stems headlessly"
```

---

### Task 6: Proot-Friendly CLI and Operator Workflow

**Files:**
- Create: `fusion_lab/cli.py`
- Create: `fusion_lab/__main__.py`
- Create: `docs/FUSION_LAB.md`

**Interfaces:**
- CLI:
  - `python -m fusion_lab compose --out <dir>`
  - `python -m fusion_lab verify-host --dir <dir>`
  - `python -m fusion_lab experiment-001 --out <dir>`
  - `python -m fusion_lab render --midi-dir <dir> --out <dir> --soundfont <path>`
  - `python -m fusion_lab render-exp001 --root <dir> --soundfont <path>`

- [ ] **Step 1: Add CLI tests to `fusion_lab/tests/test_gauntlet.py`**

Assert command parsing, deterministic output paths, short diagnostics, and no X11/display requirement.

- [ ] **Step 2: Implement CLI**

No command may discover or download a SoundFont automatically. Operator supplies the local path explicitly.

- [ ] **Step 3: Document exact Debian/Ubuntu Proot setup**

Document:

```bash
apt update
apt install -y python3 python3-pip fluidsynth ffmpeg
python3 -m pip install --user -r fusion_lab/requirements.txt
```

Also document how to substitute a local `.sf2` path and how to use `sox` if FFmpeg is unavailable.

- [ ] **Step 4: Run CLI smoke tests**

Run:
```bash
python -m fusion_lab compose --out fusion_lab/out/host-001
python -m fusion_lab verify-host --dir fusion_lab/out/host-001
python -m fusion_lab experiment-001 --out fusion_lab/out/exp-001
```
Expected: deterministic MIDI/metadata output and host verification PASS.

- [ ] **Step 5: Commit**

```bash
git add fusion_lab/cli.py fusion_lab/__main__.py fusion_lab/tests/test_gauntlet.py docs/FUSION_LAB.md
git commit -m "feat: expose proot fusion lab cli"
```

---

### Task 7: Full Laboratory Gauntlet and First Audible Proof

**Files:**
- Modify: `fusion_lab/tests/test_gauntlet.py`
- Modify: `docs/FUSION_LAB.md`

**Interfaces:**
- Consumes Tasks 1–6.
- Produces no new domain API.

- [ ] **Step 1: Write the full gauntlet**

Prove in one test flow:
1. Host 001 builds with exact 138 BPM/4/4 form and five roles;
2. host MIDI signatures are stable across two generations;
3. frozen host manifest matches generated host;
4. A/B1/B2/C are generated without in-place host mutation;
5. B1 changes articulation while preserving declared harmony/timing/function;
6. B2 changes only its declared larger voicing set;
7. C exceeds B1/B2 guest-density metric while retaining experiment provenance;
8. changing a frozen B1 dimension is refused;
9. source tree has no X11/VNC/cloud/generative-model dependency in the lab path;
10. existing game tests remain independent.

- [ ] **Step 2: Run Python laboratory suite**

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
Expected: all existing tests PASS and build PASS.

- [ ] **Step 4: Perform real Proot render**

With an operator-supplied SoundFont:
```bash
python -m fusion_lab render \
  --midi-dir fusion_lab/out/host-001 \
  --out fusion_lab/out/host-001 \
  --soundfont "$SOUNDFONT"

python -m fusion_lab render-exp001 \
  --root fusion_lab/out/exp-001 \
  --soundfont "$SOUNDFONT"
```
Expected: five host WAV stems + host mix, plus audible A/B1/B2/C outputs.

- [ ] **Step 5: Record listening evidence without forcing a conclusion**

Update `exp-001-style-not-function.json` only with human listening notes supplied after hearing A/B1/B2/C. Keep conclusion `UNRESOLVED` until the operator explicitly classifies it as `SUPPORTED`, `REFUTED`, or `MIXED`.

- [ ] **Step 6: Commit verification/doc updates**

```bash
git add fusion_lab/tests/test_gauntlet.py docs/FUSION_LAB.md fusion_lab/data/experiments/exp-001-style-not-function.json
git commit -m "test: prove headless fusion lab foundation"
```

---

## Exit Gate

Headless Fusion Lab milestone 1 is complete only when:

1. `GLAMASAURUS REX` is generated deterministically at 138 BPM in 4/4;
2. all five semantic roles exist as isolated MIDI stems;
3. the host form/harmony and arrangement constraints are pinned by tests;
4. a committed freeze manifest protects the host control;
5. Experiment 001 generates A/B1/B2/C as pure derivatives;
6. B1 proves the implementation can mutate articulation while preserving declared function/harmony/timing;
7. B2 expands only the declared voicing dimensions;
8. C provides an explicit saturation-failure candidate rather than silently redefining the host;
9. FluidSynth can render stems and mixes headlessly inside the user's Proot environment with an operator-supplied SoundFont;
10. the experiment records human listening evidence separately from structural truth;
11. existing Polly tests/build remain green;
12. no implementation rule collapses stylistic trademark into fixed compositional function.

**No Pattern Map schema change is part of this milestone.** Conversion from authored MIDI truth into Pattern Map events remains a later stage.
