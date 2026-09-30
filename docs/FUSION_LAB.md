# Headless Fusion Lab

The Fusion Lab is a deterministic, headless composition laboratory for Polly Grunge Rocker.

Its governing law is:

> **STYLE ≠ FUNCTION**

A stylistic trademark is a performance vocabulary, not a fixed compositional job. Experiments therefore declare what is frozen and what is mutated before any variant is generated.

## Host 001: GLAMASAURUS REX

The frozen control is generated from code at **138 BPM**, **4/4**, tonal center **E**, with five isolated semantic roles:

- DRUMS
- BASS
- RHYTHM_GUITAR
- LEAD_KEYS
- VOCALS

The MIDI/event source is structural truth. Rendered WAV files are listening evidence.

## Debian / Ubuntu Proot setup

From the repository root inside Proot:

```bash
apt update
apt install -y python3 python3-pip fluidsynth ffmpeg
python3 -m pip install --user -r fusion_lab/requirements.txt
```

If your distro enforces an externally-managed Python environment, create a venv instead:

```bash
python3 -m venv .venv-fusion
. .venv-fusion/bin/activate
pip install -r fusion_lab/requirements.txt
```

A local General MIDI `.sf2` SoundFont is required for rendering. The lab never downloads or chooses one automatically. Set its path explicitly:

```bash
export SOUNDFONT=/absolute/path/to/your.sf2
```

FFmpeg is used to sum stems when available. `sox` may be installed and used as the fallback mixer:

```bash
apt install -y sox
```

No X11, VNC, desktop audio server, cloud service, or generative model is required.

## Generate and verify the frozen host

```bash
python -m fusion_lab compose --out fusion_lab/out/host-001
python -m fusion_lab verify-host --dir fusion_lab/out/host-001
```

Expected host outputs:

```text
bass.mid
drums.mid
lead_keys.mid
manifest.json
rhythm_guitar.mid
vocals.mid
```

`verify-host` recomputes structural and MIDI signatures. It refuses drift from the generated manifest.

## Generate Experiment 001

```bash
python -m fusion_lab experiment-001 --out fusion_lab/out/exp-001
```

The four variants are:

- **A**: untouched host control.
- **B1**: chorus rhythm-guitar tremolo texture. Global clock, sections, other roles, harmonic roots, phrase bounds, chord-change grid, and compositional function remain frozen.
- **B2**: chorus tremolo plus register/voicing treatment and pedal drone. Host function and harmonic-root schedule remain frozen.
- **C**: deliberate saturation candidate using the guest tremolo vocabulary broadly across the song.

The experiment begins with conclusion status `UNRESOLVED`. Listening notes belong in the experiment evidence and must not rewrite structural truth.

## Render the host

```bash
python -m fusion_lab render \
  --midi-dir fusion_lab/out/host-001 \
  --out fusion_lab/out/host-001 \
  --soundfont "$SOUNDFONT"
```

This produces five WAV stems and `mix.wav`.

## Render Experiment 001

```bash
python -m fusion_lab render-exp001 \
  --root fusion_lab/out/exp-001 \
  --soundfont "$SOUNDFONT"
```

Each `A`, `B1`, `B2`, and `C` directory receives five WAV stems and a mix.

## Generic Fusion Expression Engine

The generic engine keeps these axes independent:

- performer;
- style trait;
- technique;
- compositional function;
- opportunity;
- role family;
- local context.

The governing laws are:

> **STYLE != FUNCTION**

> **TRAIT != TECHNIQUE != FUNCTION != ROLE**

> **SHARED CLOCK != SHARED RHYTHMIC IDENTITY**

A technique may serve multiple functions, a function may be realized by several techniques, and multiple performers may overlap the same broad role family without becoming the same musical job.

## Experiment 002: THRASH CHIMERA

The control is a deterministic **190 BPM**, **4/4**, E-centered Thrash host. The host clock, meter, section structure and Thrash rhythm-guitar identity remain frozen while recruit expressions are added through the generic engine.

Variants:

- **A**: pure Thrash control.
- **B**: Doom melodic guitarist with sparse multi-note sustains and drone behavior.
- **C**: Djent thumb/slap bassist with a `3+3+2+3+5` local accent cycle on the shared global clock.
- **D**: Prog synth using swells, choir-pad texture and filter movement.
- **E**: Death drummer using double-kick propulsion, blast escalation, dense support, half-time gravity and tom transitions.
- **F**: all four recruits correctly placed at once.
- **G**: the same vocabulary under explicit saturation/bad-placement policy.

Generate all seven variants:

```bash
python -m fusion_lab experiment-002 \
  --out fusion_lab/out/exp-002
```

Each variant receives adjusted host-role MIDI layers plus separate performer-owned MIDI layers. The Doom guitarist and Prog synth therefore may both occupy the broad `LEAD_KEYS` family while retaining different instruments and functions.

Render all seven variants:

```bash
python -m fusion_lab render-exp002 \
  --root fusion_lab/out/exp-002 \
  --soundfont "$SOUNDFONT"
```

Each `A` through `G` directory receives named WAV layers and `mix.wav`.

Experiment 002 remains `UNRESOLVED` until human listening evidence is recorded. The engine proves what changed. It does not decide whether the result is musically successful.

## Tests

Fusion Lab only:

```bash
python -m unittest discover -s fusion_lab/tests -v
```

Then preserve the game:

```bash
npm test
npm run build
```

## Authority boundary

The lab does not decide whether a fusion idea is musically successful. It proves exactly what changed, renders the controlled variants, and leaves the listening conclusion to the human operator.

The Pattern Map remains a separate runtime truth layer. No Pattern Map schema change is part of this milestone.
