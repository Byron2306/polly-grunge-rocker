# Polly Grunge Rocker — Realistic Renderer + Thrash Host Design

**Date:** 2026-09-30  
**Status:** DESIGN LOCK — USER REVIEW REQUIRED BEFORE IMPLEMENTATION PLAN  
**Branch:** `agent/headless-fusion-lab`

## 1. Purpose

Replace the current General-MIDI listening path with a realistic, free/open, headless Linux rendering stack while preserving the proven deterministic composition and experiment machinery.

The existing GM/FluidSynth path remains available as a fast structural debugger. It is not the production listening target.

The first realistic host will be a deliberately stereotypical late-1980s Thrash song designed to pass two independent gates:

1. machine-verifiable structural truth; and
2. human expert authenticity review for guitar/bass/drum tone, articulation, idiom and mix behavior.

The instrumental master will then become the fixed host for human vocal ablation experiments using Byron as the vocalist.

---

## 2. Non-Negotiable Separation

The production renderer must preserve the programme's existing laws:

> **STYLE ≠ FUNCTION**

> **TRAIT ≠ TECHNIQUE ≠ FUNCTION ≠ ROLE**

and add:

> **PERFORMANCE TRUTH ≠ TONE**

The composition engine owns notes, timings, articulations, sections, opportunities and structural identity.

The renderer owns sample choice, round-robin choice, humanization within declared tolerances, amp/cab tone, stereo placement, EQ, compression, room/reverb and stem summing.

A tone profile may change without silently rewriting the musical performance.

---

## 3. Rendering Architecture

```text
COMPOSITION / EXPRESSION ENGINE
        ↓
role MIDI + articulation metadata
        ↓
REALISTIC INSTRUMENT SAMPLER
        ↓
clean / DI-like role stems
        ↓
ROLE-SPECIFIC TONE CHAINS
        ↓
processed stems
        ↓
MIX BUS
        ↓
production mix.wav
```

### Structural debugger

The existing FluidSynth renderer stays available for:

- fast smoke tests;
- deterministic MIDI verification;
- CI-like local checks;
- experiment geometry.

### Production renderer

Initial preferred route:

- SFZ multisampled instruments;
- `sfizz_render` or equivalent pinned offline SFZ renderer;
- FFmpeg/SoX for deterministic audio post-processing and mixing;
- Guitarix-compatible or other free Linux amp/cab processing when it can run headlessly/reliably in Proot;
- cabinet IR convolution as a first-class tone stage;
- no cloud dependency;
- no GUI requirement for the canonical render path.

The renderer must be version-pinned and fail closed rather than silently falling back to General MIDI.

---

## 4. Platform Constraint

Target environment:

- Termux on Android;
- Debian Proot with shared home;
- offline rendering is acceptable;
- real-time low-latency performance is not required;
- native Linux/headless tools are preferred over Wine/plugin-bridge complexity;
- large commercial sample stacks are explicitly out of scope for the first milestone.

A renderer that requires X11, a desktop DAW, real-time JACK performance, cloud authentication, or proprietary license managers is not canonical for milestone one.

---

## 5. Instrument Sources

### Guitar

Guitar is the highest-risk realism role.

Requirements for the first accepted sample source:

- standard six-string range sufficient for E-standard Thrash;
- distinct palm-muted and open/sustain articulations;
- repeated-note round robins or equivalent anti-machine-gun behavior;
- velocity sensitivity;
- usable power-chord or interval rendering, or note-level mapping that can convincingly construct them;
- stable SFZ or similarly automatable mapping;
- DI-like output preferred so tone can be applied separately.

Optional later articulations:

- pinch harmonic;
- natural harmonic;
- slide;
- pick scrape;
- tremolo picking;
- dead note;
- bend / vibrato;
- alternate pick direction.

No guitar library is accepted solely because it is labeled 'metal'. Byron's listening review determines whether the source survives the authenticity gate.

### Bass

Preferred first source may include aggressive standard-tuned sampled bass such as Growlybass or another free SFZ instrument.

Requirements:

- E-standard usable range;
- picked articulation preferred for canonical Thrash host;
- sufficient round-robin/velocity variation;
- DI or minimally processed source;
- room for phrase-end fills and octave/fifth approaches.

### Drums

Requirements:

- velocity layers;
- round robins;
- multiple cymbal articulations if practical;
- kick/snare/tom separation sufficient for realistic Thrash programming;
- deterministic headless render.

Drum realism must come from both the samples and the generated performance: identical repeated velocities/timings are forbidden in the production profile unless explicitly authored.

### Keys

Keys are not central to the first Thrash host. They may remain absent or be reserved for later hosts. The renderer architecture must nevertheless permit sampled/synth role layers in future experiments.

---

## 6. Humanization Policy

Humanization is renderer-owned but bounded.

Allowed dimensions:

- microtiming offsets inside a declared tolerance;
- velocity variation inside declared ranges;
- round-robin sample selection;
- L/R double-track timing and velocity divergence;
- drummer limb/accent variation;
- fill variation when the composition marks a fill opportunity.

Forbidden silent mutations:

- tempo changes;
- section-boundary movement;
- changed chord roots;
- changed riff note order;
- changed meter;
- changed phrase length;
- added/deleted structural events outside declared rendering policy.

The same composition must remain structurally recognizable after rendering.

---

## 7. Tone Profiles

Tone is data-driven rather than hard-coded per song.

A tone profile may define:

```text
instrument_source
input_gain
pre_eq
boost_or_drive
amp_stage
cab_or_ir
post_eq
compression
gate
reverb
delay
stereo_position
stereo_width
saturation
noise_floor
```

Future profiles may include:

- `THRASH_1988`
- `BLACK_2ND_WAVE`
- `SLAM_DEATH`
- `DOOM_MONOLITH`
- `GLAM_1987`
- `DJENT_MODERN`
- `PROG_CLEAN`

Tone-profile identity never defines musical function.

---

## 8. Human Authenticity Authority

Byron is the human knowledgeable-other for this milestone.

Machine tests can prove that the correct files, notes, timings, articulations and processing stages were used. They cannot prove that a Thrash palm mute actually sounds convincing.

The review record therefore separates:

### Structural verification

Machine-verifiable:

- BPM;
- meter;
- sections;
- riff notes;
- articulation assignments;
- sample/tone profile provenance;
- stem existence;
- deterministic output metadata.

### Authenticity review

Human-reviewed:

- palm-mute punch;
- pick attack realism;
- downpick/gallop plausibility;
- gain amount and character;
- cab/mid character;
- bass attack/body;
- drum naturalism;
- double-track plausibility;
- lead-guitar believability;
- genre-specific production feel.

Review states:

```text
PASS | ADJUST | REFUSE
```

A production tone is not promoted on machine checks alone.

---

## 9. Host 003 — CHAINSAW DIPLOMACY

The first realistic host is deliberately stereotypical late-1980s Thrash.

### Canonical identity

- tuning: **E standard**;
- tempo: **192 BPM**;
- meter: **4/4**;
- tonal center: E-minor / chromatic E-centered riff language;
- no drop tuning;
- no djent displacement;
- no slam vocabulary;
- no blast beats in the canonical control;
- no modern surgical-gate aesthetic as a default tone behavior.

### Harmonic/riff vocabulary

Primary pitch resources may include:

- E pedal;
- F natural;
- F#;
- G;
- Bb;
- B;
- chromatic approach tones;
- tritone pressure;
- diminished passing color.

The host should sound stereotypically Thrash because of the total relationship between riffing, articulation, tempo, percussion, bass behavior and tone, not because a genre label is baked into the engine.

### Form

```text
4 bars   INTRO RIFF
8 bars   VERSE 1
4 bars   PRE-CHORUS
8 bars   CHORUS
8 bars   VERSE 2
8 bars   CHORUS
8 bars   SOLO
4 bars   BRIDGE
8 bars   FINAL CHORUS
4 bars   OUTRO
```

Total: 64 bars.

---

## 10. Guitar Performance Grammar

### Rhythm guitars

Two independently rendered rhythm layers.

Core grammar:

- hard downpicked eighth-note drive;
- gallop cells;
- palm-muted low-E pedal;
- chromatic power-chord movement;
- open power-chord releases;
- short transitional scrapes/noise only when explicitly authored;
- realistic phrase breathing rather than mathematically identical attack throughout.

The left and right rhythm layers share musical structure but may differ by bounded humanization, round-robin selection and processing variation.

### Lead guitar

The solo must test whether the realistic stack can render expressive lead guitar rather than only rhythm parts.

Required vocabulary:

- sustained lead notes;
- bends or bend-equivalent articulation if the chosen library supports them;
- vibrato;
- short fast runs;
- high-register phrase peaks;
- deliberate phrase gaps.

The milestone may refuse a free guitar library if it cannot make the solo believable enough. A fallback simplified solo is allowed only as a diagnostic, not as the production acceptance target.

---

## 11. Bass Grammar

Canonical Thrash bass:

- picked attack;
- primarily follows the riff;
- occasional octave/fifth reinforcement;
- short phrase-end fills;
- central placement;
- enough low-mid definition to remain audible without becoming modern click-bass.

Bass tone and bass composition remain separate dimensions.

---

## 12. Drum Grammar

Canonical control:

- fast Thrash/skank behavior where appropriate;
- kick support under riff accents;
- readable snare backbeat in chorus sections;
- double-kick escalation in transition/build contexts;
- ride/hat/crash articulation changes by section;
- tom fills at authored transitions;
- half-time Thrash bridge;
- no blast beats in control host.

Production humanization must include bounded velocity and microtiming variation while preserving the shared global clock.

---

## 13. Mix Grammar

Initial mix target:

- rhythm guitars hard L/R;
- bass center;
- kick/snare center;
- cymbals naturally distributed if sample source permits;
- lead centered or slightly offset with optional delay/reverb;
- enough headroom for later vocal insertion;
- no loudness-maximization requirement in milestone one.

The mix must export stems as well as a full instrumental mix so later vocal ablations do not require re-rendering the entire song.

---

## 14. Byron Vocal Integration

The instrumental host is designed explicitly to receive real human vocals from Byron.

The renderer does not synthesize the canonical vocal performance.

Planned human vocal states include:

- high second-wave black-metal shriek;
- lower growly shriek;
- croak/fry coloration;
- death growl;
- Thrash bark / shout-talk;
- punk shout/sneer if desired;
- high clean / androgynous Glam register.

The host should leave deliberate vocal opportunity windows for:

- long sustained phrase;
- short bark;
- syncopated phrase;
- phrase crossing the barline;
- call/response;
- harmonic double;
- controlled dissonant double.

Vocal recording and ablation are a later milestone. This milestone only guarantees that the instrumental master exposes suitable windows and enough mix headroom.

---

## 15. Lyrics Boundary

Lyrics are authored only after the realistic instrumental host passes authenticity review.

Reason:

The lyric cadence should respond to the final riff accents, section lengths, phrase openings and vocal space rather than force the instrumental master to bend around premature text.

The future lyric set should include phonetic material suitable for both sustained harsh vocals and short percussive barks.

---

## 16. Evidence and Provenance

Every production render records:

- renderer version;
- instrument library IDs/paths;
- sample source hashes where practical;
- tone-profile ID;
- processing stages;
- IR/cab identity;
- humanization seed;
- per-role structural signature;
- output stem hashes;
- mix hash;
- expert-review state and notes.

A render is reproducible from the same inputs and seed.

No missing production dependency may silently fall back to the GM renderer.

---

## 17. Milestone Failure Behavior

The production renderer must refuse with actionable diagnostics when:

- offline sampler is missing;
- SFZ source is missing;
- required samples are missing;
- amp/cab/IR dependency is missing;
- an instrument profile declares unsupported articulations;
- a production role silently resolves to General MIDI;
- expected stems are absent;
- mix step fails.

A diagnostic GM render may be explicitly requested by command, but it is never an implicit production fallback.

---

## 18. First-Milestone Acceptance

The milestone is complete only when:

1. the existing GM renderer still passes its regression suite;
2. the production renderer runs headlessly in Debian Proot;
3. the production renderer can render at least guitar, bass and drums from deterministic event truth;
4. guitar output is not General MIDI;
5. E-standard tuning is preserved in `CHAINSAW DIPLOMACY`;
6. two rhythm-guitar layers render independently;
7. palm-muted and open rhythm articulations are audibly distinguishable;
8. bass is rendered from a realistic sampled source rather than GM;
9. drums use multi-velocity/round-robin-capable source material or equivalent realistic variation;
10. the host renders all 64 bars at 192 BPM / 4/4;
11. structural signatures remain stable before/after renderer swap;
12. production stems and instrumental mix are exported;
13. missing production dependencies fail closed;
14. Byron reviews the instrumental result and records `PASS`, `ADJUST`, or `REFUSE` for the authenticity rubric;
15. only a `PASS` production master becomes the frozen basis for the later vocal-ablation experiment.

---

## 19. Out of Scope for This Milestone

- commercial Kontakt libraries;
- MODO Bass;
- Superior Drummer;
- mandatory Wine/yabridge setup;
- real-time Android performance;
- final mastering;
- AI-generated canonical vocals;
- vocal model training;
- Pattern Map schema changes;
- automatic authenticity scoring.

---

## 20. Canon

The production renderer exists to make the evidence listenable without corrupting the experiment.

> **THE COMPOSITION TELLS US WHAT WAS PLAYED.**

> **THE RENDERER TELLS US WHAT IT SOUNDED LIKE.**

> **THE HUMAN EXPERT TELLS US WHETHER THE IDIOM IS AUTHENTIC.**

And the programme laws remain:

> **STYLE ≠ FUNCTION.**

> **PERFORMANCE TRUTH ≠ TONE.**

> **STRUCTURE IS SHARED. STYLE IS PERSONAL.**
