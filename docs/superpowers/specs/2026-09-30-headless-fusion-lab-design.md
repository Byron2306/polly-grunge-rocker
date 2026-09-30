# Polly Grunge Rocker — Headless Fusion Lab Design

**Date:** 2026-09-30  
**Status:** DESIGN LOCK — REVIEW REQUIRED BEFORE IMPLEMENTATION PLAN  
**Branch:** `agent/headless-fusion-lab`

## 1. Governing Law

> **STYLE ≠ FUNCTION**

A stylistic trademark is not bound to one convergent musical function.

A tremolo texture may carry melody, harmony, tension, sustain or counterline. A D-beat may drive a whole section or act as a short release from blast density. A doom sustain may anchor, resolve, threaten, color or simply occupy time. A pinch harmonic may punctuate, climax, interrupt or become melodic material.

The implementation must therefore keep these concepts separate:

```text
STYLE TRAIT
+ PLACEMENT
+ FUNCTION
+ CONTEXT
= EXPRESSION
```

The host composition says **where**. The musician says **how**. The local musical situation says **why**.

This law is non-negotiable and every experiment must be capable of testing it directly.

---

## 2. Purpose

Build a local, deterministic, headless music-composition laboratory that can create a deliberately stereotypical Glam Metal host song and then generate controlled A/B/C/D musical variants where exactly one compositional or performance dimension is changed at a time.

The lab exists to discover reusable fusion rules from controlled evidence rather than genre stereotypes or generative-model behavior.

It must run from Termux/Proot without requiring a graphical DAW, cloud service or generative model.

---

## 3. Core Toolchain

Initial headless stack:

- Python for deterministic composition scripts;
- `mido` for MIDI authoring and manipulation;
- FluidSynth for offline MIDI → WAV rendering;
- SoundFonts for replaceable instrument realization;
- FFmpeg/SoX only where useful for deterministic conversion, normalization or stem assembly;
- existing Pattern Map authoring/analysis tooling for inspection and later export.

GUI DAWs may be used later for artistic polish, but they are not part of the core dependency chain.

The MIDI/event representation is canonical for laboratory truth. Rendered WAV is an audible realization of that truth, not the primary structural authority.

---

## 4. Host 001 — GLAMASAURUS REX

The first host is intentionally exaggerated, catchy and structurally obvious.

### Global structure

- Tempo: `138 BPM`
- Meter: `4/4`
- Tonal center: `E`
- Character: shameless late-80s sleaze/glam metal caricature
- Length target: approximately two minutes

### Form

```text
4 bars   INTRO RIFF
8 bars   VERSE 1
4 bars   PRE-CHORUS
8 bars   CHORUS
4 bars   TURNAROUND
8 bars   VERSE 2
4 bars   PRE-CHORUS
8 bars   CHORUS
8 bars   LEAD BREAK / SOLO
4 bars   BUILD
8 bars   FINAL CHORUS
4 bars   OUTRO
```

### Harmonic skeleton

Verse:

```text
| E5 | D5 | A5 | E5 |
| E5 | D5 | A5 | B5 |
```

Pre-chorus:

```text
| A | B | C#m | B |
```

Chorus:

```text
| E | B | C#m | A |
| E | B | A   | B |
```

The host must remain simple enough that later changes are audible and attributable.

---

## 5. Canonical Musical Roles

The lab must author separate canonical tracks for:

1. `DRUMS`
2. `BASS`
3. `RHYTHM_GUITAR`
4. `LEAD_KEYS`
5. `VOCALS`

For Host 001, `VOCALS` may initially be represented by an instrumental melody guide rather than sung audio. The semantic role remains canonical.

Each role is exported as an independent MIDI file and rendered as an independent WAV stem.

---

## 6. Host Arrangement Language

### Drums

Intentionally legible rock pulse:

- straight eighth-note hats;
- snare on 2 and 4;
- simple kick pattern;
- fills at authored transitions;
- chorus crashes;
- no D-beat, blast beat, polymeter or extreme-metal vocabulary in the frozen host.

### Bass

Intentionally conservative:

- eighth-note root motion;
- occasional fifth;
- simple approach tones into changes;
- no syncopated Prog/Djent counter-groove in the frozen host.

### Rhythm Guitar

- low-E hard-rock chug vocabulary in verses;
- open power-chord punches;
- larger sustained power chords in choruses;
- no Black Metal tremolo saturation, Doom sustain experiment or Djent displacement in the frozen host.

### Lead / Keys

- shameless major-pentatonic/chord-tone hook;
- bend into major third;
- large vibrato;
- repeated high note;
- descending melodic sequence;
- deliberately excessive lead-break language;
- simple glossy pad during choruses.

### Vocal role

- simple memorable melody guide;
- clearly separated phrase starts/ends for later call-response experiments.

---

## 7. Frozen Host Principle

Once Host 001 is verified, it becomes immutable laboratory control data.

Experiments never edit the canonical host in place.

Each experiment records:

```text
FROZEN DIMENSIONS
MUTATED DIMENSION(S)
HYPOTHESIS
VARIANTS
EXPECTED OBSERVABLE DIFFERENCE
```

A valid experiment must preserve all dimensions not explicitly named as mutated.

This is the core protection against fake conclusions.

---

## 8. Experiment 001 — STYLE ≠ FUNCTION

The first experiment tests whether stylistic identity can change while musical function stays constant.

Target: chorus rhythm-guitar role.

### A — Host Control

- original Glam rhythm-guitar notes;
- original harmony;
- original timing;
- original structural function;
- original articulation.

### B1 — Articulation Only

Preserve:

- exact pitches;
- exact harmony;
- exact rhythm grid;
- exact phrase boundaries;
- exact structural function.

Mutate only articulation/density toward continuous tremolo texture.

Question:

> Can a recognizably foreign stylistic identity emerge without changing the compositional job?

### B2 — Voicing Treatment

Preserve:

- host harmony;
- section timing;
- role function;
- phrase placement.

Allow:

- tremolo articulation;
- pedal/drone voicing;
- upper-voice repetition;
- register treatment.

Question:

> Does voicing strengthen guest identity while host function remains intact?

### C — Saturation Failure

Apply the same guest vocabulary across too much of the section/song.

Question:

> At what density/duration does guest identity stop enriching the host and begin replacing it?

---

## 9. Planned Experiment Families

After Experiment 001, the lab should support controlled mutations for:

### Rhythm / time treatment

- D-beat drive;
- blast-beat density;
- slam spacing;
- Djent/Prog displacement;
- polymeter / local cycle disagreement.

### Articulation

- tremolo texture;
- palm-muted chug;
- pinch-harmonic punctuation;
- thumb/slap attack;
- ghost-note/percussive attack.

### Duration / temporal occupancy

- Doom sustain;
- drone anchor;
- long decay;
- deliberate silence / gap expansion.

### Harmonic coloration

- tritone color;
- minor-second friction;
- modal coloration;
- chromatic approach;
- major-harmony preservation under extreme articulation.

### Timbre / orchestration

- Mellotron/choir-like layer;
- organ;
- analog synth;
- noise bed;
- alternate guitar tone;
- prepared/percussive instrument treatment.

The lab must not encode any one of these as a fixed genre-function relationship.

---

## 10. Experiment Data Model

Every experiment needs machine-readable metadata describing:

- experiment ID;
- host ID;
- role under test;
- frozen dimensions;
- mutated dimensions;
- hypothesis;
- variant IDs;
- exact source MIDI files;
- exact rendered stems;
- human listening notes;
- later Pattern Map observations;
- conclusion status: `UNRESOLVED | SUPPORTED | REFUTED | MIXED`.

No conclusion may be inferred solely from a genre label.

---

## 11. Reproducibility

Given the same source files, configuration and SoundFont set, the lab must reproduce:

- identical MIDI event timing;
- identical experiment metadata;
- deterministic file naming;
- deterministic stem assignment;
- stable Pattern Map timing references.

Rendered audio byte identity is desirable but not required across different synthesizer versions. Structural event identity is required.

---

## 12. Proot / Headless Boundary

The first implementation must be usable inside a Debian/Ubuntu Proot environment launched from Termux.

Required workflow:

```text
compose host
    ↓
write canonical MIDI stems
    ↓
render stems headlessly
    ↓
render full mix
    ↓
generate experiment variants
    ↓
render A/B/C/D outputs
    ↓
inspect/listen
    ↓
record human conclusion
```

No graphical X11/VNC dependency is required for the core workflow.

---

## 13. Relationship to Pattern Map

The Fusion Lab and Pattern Map have different authority boundaries.

Fusion Lab owns:

- authored composition source;
- controlled mutation definitions;
- experimental evidence.

Pattern Map owns:

- deterministic runtime musical structure and timing.

The same authored event truth should eventually be convertible into Pattern Map events so the game does not have to re-detect structure that the lab already knows exactly.

This conversion is a later implementation stage and must preserve the existing Pattern Map validation boundary.

---

## 14. Success Criteria

The first Headless Fusion Lab milestone is complete when:

1. Host 001 can be generated deterministically from source code/data;
2. all five semantic roles exist as isolated MIDI stems;
3. the host can be rendered headlessly to individual WAV stems and a combined mix;
4. Host 001 is frozen and checksummed;
5. Experiment 001 can generate A, B1, B2 and C without silently mutating frozen dimensions;
6. experiment metadata records exactly what changed;
7. the output is usable from Termux/Proot without a GUI;
8. existing game/Pattern Map tests remain unaffected;
9. the implementation does not collapse style traits into fixed musical functions.

---

## 15. Canon

Three lines govern the system:

> **MAP THE PATTERNS.**

> **STRUCTURE IS SHARED. STYLE IS PERSONAL.**

> **STYLE ≠ FUNCTION.**

And the operational expression is:

> **The song tells you where. The musician tells you how. The situation tells you why.**
