# Polly Grunge Rocker — Generic Fusion Expression Engine Design

**Date:** 2026-09-30  
**Status:** DESIGN LOCK — REVIEW REQUIRED BEFORE IMPLEMENTATION PLAN  
**Branch:** `agent/headless-fusion-lab`

## 1. Governing Laws

The engine is built around these non-negotiable separations:

> **STYLE ≠ FUNCTION**

> **TRAIT ≠ TECHNIQUE ≠ FUNCTION ≠ ROLE**

Correlations are allowed. Identity collapse is not.

A stylistic trademark is a way of sounding or behaving. A technique is a concrete musical mechanism. A function is the compositional job being performed at one moment. A role is the broad semantic lane in the arrangement. These may converge historically, but the engine must never define one as the other.

Operationally:

```text
HOST STRUCTURE
+ OPPORTUNITY
+ PERFORMER
+ STYLE TRAIT
+ TECHNIQUE
+ FUNCTION
+ LOCAL CONTEXT
= EXPRESSION
```

The host says **where**. The musician says **how**. The situation says **why**.

---

## 2. Purpose

Extend the existing Headless Fusion Lab from hand-authored one-off experiments into a generic combinatorial experiment engine that can:

- define host songs independently from recruit identity;
- define stylistic traits independently from techniques;
- define techniques independently from compositional functions;
- place multiple performers into the same host section without forcing one performer per semantic role;
- generate controlled variants where declared dimensions change and undeclared dimensions remain frozen;
- produce good-placement and bad-placement controls;
- support both single-variable and compound multi-recruit experiments;
- remain deterministic and headless in Termux/Proot.

The engine is for discovery. It must make it possible to ask whether a technique/function/context relationship works without smuggling in unrelated changes.

---

## 3. Core Domain Model

### Host

Owns canonical song structure:

- tempo regions;
- meter;
- sections;
- phrase boundaries;
- harmonic motion;
- role events;
- transition windows;
- convergence points.

The host does not own recruit style.

### Performer

Represents a recruit identity.

A performer may expose:

- native stylistic traits;
- available techniques;
- timbral preferences;
- role affinities;
- familiarity metadata;
- optional local rhythmic cycle behavior.

A performer is not restricted to one host role forever.

### Style Trait

A stable identity dimension such as:

- tremolo texture;
- long sustain;
- loose slam weight;
- percussive thumb attack;
- raw D-beat propulsion;
- spectral/timbral experimentation;
- high overtone punctuation;
- harmonic drone preference.

Traits describe identity, not job.

### Technique

A concrete musical mechanism such as:

- tremolo picking;
- sustained note or chord;
- pedal drone;
- D-beat;
- blast beat;
- double-kick lock;
- pinch harmonic;
- thumb/slap/pop;
- ghost-note attack;
- metric displacement;
- synth swell;
- choir pad;
- filter movement;
- tritone coloration.

### Function

A compositional job such as:

- primary groove;
- propulsion;
- escalation;
- release;
- transition drive;
- harmonic bed;
- melodic lead;
- counter-melody;
- punctuation;
- phrase answer;
- tension;
- resolution;
- section illumination;
- textural atmosphere;
- convergence setup;
- rhythmic destabilization.

No technique has one fixed function.

### Opportunity

A host-authored structural opening where an expression may occur.

Opportunity constrains:

- section;
- time range;
- eligible functions;
- eligible roles or performers;
- rhythmic tolerance;
- harmonic tolerance;
- density budget;
- convergence target if any.

### Local Context

Context binds an expression to the active musical situation:

- current host harmony;
- tempo;
- meter;
- section;
- phrase position;
- active performers;
- density;
- register occupancy;
- rhythmic cycles;
- timbral/spectral density.

### Expression

An expression is the concrete realized event created from performer + trait + technique + function + opportunity + local context.

It must record provenance so every audible change can be traced to the declared experiment definition.

---

## 4. Performer Slot Is Not Semantic Function

The old one-role-one-performer assumption is insufficient.

The engine must support:

```text
HOST ROLE
    ↓
FUNCTIONAL OPPORTUNITIES
    ↓
0..N PERFORMER EXPRESSIONS
```

Two performers may overlap the broad `LEAD_KEYS` family while serving different functions.

Example:

```text
DOOM GUITARIST
function: COUNTER_MELODY
trait: LONG_SUSTAIN
technique: SUSTAINED_MELODIC_LINE
```

while simultaneously:

```text
PROG SYNTH
function: TEXTURAL_ATMOSPHERE
trait: TIMBRAL_EXPERIMENTATION
technique: SYNTH_SWELL / CHOIR_PAD
```

Neither displaces the other by definition.

---

## 5. Generic Experiment Definition

Every experiment is data-driven and records:

```text
experiment_id
host_id
control_variant
performers
expressions
frozen_dimensions
mutated_dimensions
hypothesis
variant_graph
bad_placement_control
expected_observables
conclusion_status
human_listening_notes
```

Each expression declares at minimum:

```text
performer_id
style_trait
technique
function
opportunity_id
role_family
placement
rhythmic_policy
harmonic_policy
timbral_policy
density_policy
```

The engine rejects variants that alter a frozen dimension without declaring it.

---

## 6. Generic Variant Strategy

The engine must be able to generate progressive variants rather than only A/B/C.

Typical pattern:

```text
A = pure host
B = host + recruit 1
C = host + recruit 2
D = host + recruit 3
E = host + recruit 4
F = host + all recruits correctly placed
G = host + all recruits badly placed / over-saturated
```

This separates:

- whether one recruit treatment works;
- whether several treatments coexist;
- whether placement rather than genre label explains success;
- whether density causes collapse.

---

## 7. Experiment 002 — THRASH CHIMERA

This is the first compound multi-recruit experiment implemented on the generic engine.

### Host Identity

A deliberately stereotypical Thrash host.

Baseline:

- Tempo: approximately `190 BPM`;
- Meter: `4/4`;
- tonal language: aggressive minor/chromatic E-centered riff vocabulary;
- tight palm-muted gallops;
- rapid downpicked power-chord movement;
- conventional Thrash bass following host riff in the control;
- conventional Thrash drum arrangement in the control;
- short aggressive lead phrases;
- clear, repeatable section structure.

Suggested form:

```text
INTRO
VERSE 1
PRE-CHORUS
CHORUS
VERSE 2
CHORUS
SOLO
BREAK
FINAL CHORUS
OUTRO
```

Host authority remains unchanged in all valid variants:

- global tempo;
- global meter;
- section boundaries;
- phrase boundaries;
- host harmonic progression;
- host riff identity.

---

## 8. THRASH CHIMERA Recruit 1 — Doom Melodic Guitarist

### Identity

Style traits:

- long sustain;
- harmonic gravity;
- slow melodic movement;
- wide note duration;
- heavy vibrato;
- optional drone behavior.

### Primary technique family

- `SUSTAINED_MELODIC_LINE`;
- `DRONE_ANCHOR`;
- optional `SLOW_RESOLUTION`.

### Functions under test

- counter-melody;
- emotional bed;
- long-form tension;
- resolution;
- section gravity.

### Critical law tested

> Slow temporal identity may survive inside a fast host without changing the host tempo.

The Doom recruit must not slow the Thrash host. The host continues at ~190 BPM while the recruit occupies longer temporal spans.

---

## 9. THRASH CHIMERA Recruit 2 — Djent Thumb/Slap Bassist

This recruit is inspired by modern progressive extended-range thumb/slap language rather than copying any specific artist recording.

### Identity

Style traits:

- percussive thumb attack;
- slap/pop punctuation;
- muted ghost attacks;
- asymmetric accent logic;
- displaced groove;
- local-cycle independence.

### Primary techniques

- `THUMB_ATTACK`;
- `SLAP_POP`;
- `GHOST_NOTE`;
- `METRIC_DISPLACEMENT`;
- `ROLE_LOCAL_CYCLE`.

### Functions under test

- groove destabilization;
- counter-rhythm;
- subdivision definition;
- convergence setup;
- phrase tension.

### Role-local time law

The bassist may operate a local accent cycle while remaining on the same global clock.

Example candidate grouping:

```text
3 + 3 + 2 + 3 + 5
```

This is an accent/cycle policy, not a second tempo.

### Critical law tested

> **SHARED CLOCK ≠ SHARED RHYTHMIC IDENTITY**

The bassist may appear to argue with the bar while still converging at authored targets.

---

## 10. THRASH CHIMERA Recruit 3 — Prog Synth

### Identity

Style trait:

- timbral experimentation;
- spectral transformation;
- re-orchestration;
- unexpected register and texture.

### Primary techniques

- `SYNTH_SWELL`;
- `CHOIR_PAD`;
- `FILTER_MOVEMENT`;
- `NOISE_BED`;
- optional `TIMBRE_MORPH`.

### Functions under test

- section illumination;
- transition atmosphere;
- harmonic atmosphere;
- textural bed;
- dramatic reveal.

### Critical law tested

> Style may change through timbre while harmony and structural function remain unchanged.

The first Prog synth treatment should preserve host harmony and timing while changing spectral identity.

---

## 11. THRASH CHIMERA Recruit 4 — Death Metal Drummer

### Identity

Style traits:

- high-density extreme-metal percussion;
- double-kick pressure;
- blast vocabulary;
- violent transition fills;
- half-time death groove contrast.

### Primary techniques

- `DOUBLE_KICK_LOCK`;
- `BLAST_BEAT`;
- `DEATH_HALF_TIME`;
- `TOM_FILL`;
- optional `SKANK_TRANSITION`.

### Functions under test

The same performer must use different techniques for different functions:

- verse: double-kick propulsion;
- pre-chorus: blast escalation;
- chorus: dense support beneath readable host phrase structure;
- break: half-time gravity;
- transition: tom-fill punctuation/drive.

### Critical law tested

> One stylistic identity can perform multiple compositional functions without becoming multiple genres or performers.

---

## 12. THRASH CHIMERA Variant Graph

The first implementation should generate:

### A — Pure Thrash Control

No recruit expressions.

### B — Doom Recruit Only

Add Doom sustained melodic counterline while all other host dimensions remain frozen.

### C — Djent Bass Recruit Only

Replace or overlay the control bass contribution only according to the declared local-cycle policy.

### D — Prog Synth Recruit Only

Add timbral/textural layer while preserving host harmony/structure.

### E — Death Drummer Only

Replace the control drum treatment with declared Death Metal techniques while keeping host clock and section structure.

### F — Full Chimera

All four recruits correctly placed at once.

The purpose is to test coexistence, not maximal density. Each recruit receives authored opportunity windows and density budgets.

### G — Bad Placement / Saturation Control

All four recruit vocabularies are overused or placed outside their strongest authored opportunities while preserving the same host song.

G exists to distinguish:

> `genre fusion works`

from the stronger conclusion:

> `specific trait × technique × function × context relationships work`.

---

## 13. Frozen Dimensions and Mutation Authority

Every variant declares its authority before generation.

Examples:

### Doom-only variant

Frozen:

- host tempo;
- meter;
- section boundaries;
- rhythm-guitar riff;
- drum pattern;
- host harmony;
- host phrase identity.

Mutated/added:

- performer expression layer;
- sustained melodic duration;
- melodic counterline register;
- vibrato/articulation metadata.

### Death-drummer variant

Frozen:

- tempo;
- meter;
- guitar riff;
- bass host line;
- synth absence;
- harmonic motion;
- section timing.

Mutated:

- drum technique;
- drum density;
- drum subdivision pattern;
- fill placement.

The engine must refuse undeclared mutation leakage.

---

## 14. Placement Quality

The generic engine must distinguish technique availability from placement quality.

Placement quality may consider:

- section compatibility;
- phrase position;
- harmonic compatibility;
- rhythmic space;
- density budget;
- register collision;
- convergence timing;
- active recruit count;
- local-cycle resolution.

This is not a simple genre compatibility score.

A technique may work brilliantly in one function/context and badly in another.

---

## 15. Density and Saturation

Every expression may specify:

- event density;
- duration budget;
- spectral/register occupancy;
- overlap budget;
- repetition limit.

The system must support saturation controls because a valid technique can become destructive when overused.

This is especially important for:

- tremolo;
- blast beats;
- drones;
- synth pads;
- pinch harmonics;
- displaced accents.

---

## 16. Evidence Model

Each generated variant must retain machine-readable provenance sufficient to answer:

- what changed;
- what remained frozen;
- who changed it;
- which trait was expressed;
- which technique realized it;
- what function it served;
- where it occurred;
- what context was active;
- what density policy applied.

Human listening evidence remains separate from structural truth.

Conclusion status remains:

```text
UNRESOLVED | SUPPORTED | REFUTED | MIXED
```

No conclusion is inferred from a genre label.

---

## 17. Relationship to Pattern Map

The generic engine is not the runtime Pattern Map.

Fusion Engine owns:

- performer/trait/technique/function definitions;
- experiment definitions;
- controlled mutation;
- generated musical evidence.

Pattern Map owns:

- runtime structural truth;
- opportunities;
- deterministic timing;
- section/phrase/role events;
- convergence points.

Later integration should allow Pattern Map opportunities to instantiate the same generic expression relationships proven in the lab.

The lab therefore becomes an evidence source for future game rules, not a parallel gameplay engine.

---

## 18. Success Criteria

The generic engine milestone is successful when:

1. traits, techniques, functions, roles and performers are represented independently;
2. a technique can legally be assigned to more than one function;
3. a function can be realized by multiple techniques;
4. multiple performers may coexist inside overlapping semantic role families;
5. every experiment declares frozen and mutated dimensions before generation;
6. undeclared mutation leakage is refused;
7. single-recruit and compound experiments use the same generic machinery;
8. THRASH CHIMERA A/B/C/D/E/F/G can be generated deterministically;
9. the Doom recruit can sustain over a ~190 BPM host without changing global tempo;
10. the Djent bassist can use role-local rhythmic identity while preserving the shared clock;
11. the Prog synth can change timbre while preserving host harmony and timing;
12. the Death drummer can perform several different functions using one coherent performer identity;
13. F and G differ primarily by placement/density policy rather than by host song;
14. all variants render headlessly in Termux/Proot using the existing lab renderer;
15. no rule collapses style into function.

---

## 19. Canon

The engine is governed by:

> **MAP THE PATTERNS.**

> **STRUCTURE IS SHARED. STYLE IS PERSONAL.**

> **STYLE ≠ FUNCTION.**

> **TRAIT ≠ TECHNIQUE ≠ FUNCTION ≠ ROLE.**

> **SHARED CLOCK ≠ SHARED RHYTHMIC IDENTITY.**

And the operational rule remains:

> **The song tells you where. The musician tells you how. The situation tells you why.**
