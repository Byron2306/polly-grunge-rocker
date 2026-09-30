# Polly Grunge Rocker — Pattern Map Programme Roadmap

**Date:** 2026-09-30  
**Status:** APPROVED ARCHITECTURE → STAGED IMPLEMENTATION PROGRAMME  
**Canonical architecture:** `docs/superpowers/specs/2026-09-30-pattern-map-combat-architecture.md`

## Programme Objective

Build a deterministic music-driven belt-scroller in which:

- Rat Hole teaches the shared musical grammar and assembles Polly's guaranteed Grunge starter band;
- later genre worlds reinterpret that grammar rather than replacing it;
- optional recruits bring persistent stylistic identities and learn where their vocabulary fits;
- learned ally techniques become automatic when current coherence and Pattern Map opportunity support them;
- party composition becomes audible through controlled cross-genre fusion;
- the host song always remains structurally authoritative.

Core rules:

> **MAP THE PATTERNS.**

> **STRUCTURE IS SHARED. STYLE IS PERSONAL.**

> **The song tells you where. The musician tells you how.**

---

## Phase Order

### 0. Proven Combat Baseline — COMPLETE

Preserve the accepted Phase 1 / Phase 2B.1 beat-'em-up feel:

- free X/Y belt movement;
- light chain and heavy guitar attack;
- hitstop, hitstun, knockback and tokenized enemy pressure;
- mobile controls;
- approved Polly and enemy master sprites;
- corrected walk band.

The music programme may extend this baseline but must not replace it.

### 1. Rat Hole Production Art

Replace the flat placeholder environment with the approved painterly pixel-art language.

Production goals:

- Rat Hole reads immediately as Polly's Grunge home turf;
- one continuous physical venue/alley progresses through teaching spaces;
- wet asphalt, practical light, grime, layered masonry, posters, pipes, fences, clutter and meaningful foreground depth;
- combat readability remains stronger than decoration;
- no procedural-flat or early-adventure-game aesthetic.

This phase changes presentation only.

### 2. Pattern Map Foundation

Build pure deterministic TypeScript domain structures for:

- tempo and meter regions;
- sections and phrases;
- the five musical roles;
- per-role pattern events;
- cross-layer alignments;
- deterministic queries by explicit track time;
- validation, import and human inspection.

No Phaser and no WebAudio dependency.

Existing plan: `docs/superpowers/plans/2026-09-30-pattern-map-foundation.md`.

### 3. Pattern Map Authoring / Analysis Tool

Build the human-in-the-loop tool used to create production maps from stems, MIDI and rendered audio.

Assist with:

- BPM and downbeat candidates;
- meter candidates;
- transient/onset extraction;
- repeated-cell detection;
- phrase and riff candidates;
- section boundaries;
- cross-layer alignment candidates;
- confidence visualization;
- manual correction;
- deterministic export.

Automatic analysis remains advisory. Human correction is authoritative.

### 4. Fusion Lab

Before runtime fusion exists, experimentally establish which cross-genre treatments actually work by ear.

Use generated or authored musical experiments, including Suno where useful, to test host/guest combinations such as:

- Glam + Black Metal tremolo;
- Punk + Death Metal blast fills;
- Thrash + Doom bass sustain;
- Prog + Punk drums;
- Grunge + Black Metal vocals;
- Doom + Glam harmonies.

For each experiment record:

- host genre and structural context;
- guest technique;
- where the contribution works;
- where it hijacks or muddies the host;
- suitable duration and density;
- whether compatibility is Native, Fusion or Clash;
- reusable rules that can later become runtime data.

Exit with a small validated technique compatibility corpus rather than theory-only assumptions.

### 5. Authoritative Audio Clock

Create one source of timing truth connecting:

- audio playback time;
- Pattern Map time;
- simulation time;
- beat, bar, phrase and section position.

Prove pause/resume, seek and frame-rate variation without adding gameplay bonuses yet.

### 6. Musical Input Evaluation

Evaluate Polly's existing attacks against Pattern Map windows.

Initial result vocabulary:

- acceptable;
- on-pattern;
- accent-perfect;
- phrase-perfect;
- alignment-perfect.

Existing combat moves and damage remain intact. This phase adds timing interpretation, not a new combat game.

### 7. Rat Hole Grunge Scaffolding

Rebuild Rat Hole encounters around home-scene musicians rather than Glam/Punk/Prog tutorial enemies.

Progression:

1. Polly alone — timing, riff repetition and phrase anticipation;
2. Drummer — pulse, beat, subdivision and accent;
3. Bassist — groove, lane stability and continuity;
4. Rhythm Guitarist — repeated cells, structure and phrase commitment;
5. Vocalist — call/response, interruption and response timing;
6. Full-band finale — all five layers together.

The four Grunge musicians are guaranteed story recruits.

### 8. Party and Soft-Lane Foundation

Add a five-member party model while preserving free belt-scroller movement.

Add:

- musical role identity;
- approximate upper/middle/lower tactical bands;
- ally lane tendencies;
- contextual repositioning;
- no RTS micromanagement requirement.

Polly remains directly controlled.

### 9. Performance and Coherence

Create two distinct systems:

**Performance** evaluates what happened across an encounter.

**Coherence** represents current shared band understanding during play.

Inputs may include:

- timing;
- phrase continuity;
- lane coordination;
- useful interrupts;
- damage avoidance;
- ally joins;
- cross-layer recognition.

Coherence must not degrade into a generic special meter.

### 10. Teaching and Learning

Implement explicit Polly-to-recruit teaching.

Polly demonstrates where a recruit's own vocabulary fits the current structure.

Persist separately:

- learned pattern-technique relationships;
- confidence/knowledge;
- host-genre familiarity.

Do not modify a musician's core identity merely because they learned another genre.

### 11. Technique Vocabulary

Formalize musician-specific stylistic techniques.

Examples:

- Tremolo Picking;
- Blast-Beat Lock;
- Palm-Mute Precision;
- Sustained Doom Resolution;
- Falsetto Call;
- Growl Projection;
- Shriek Accent;
- Odd-Meter Literacy.

A technique defines structural compatibility and performance treatment. It is not simply a damage modifier.

### 12. Automatic Opportunity Resolution

Once a recruit has learned a relationship, technique use becomes autonomous.

Automatic expression requires:

- learned relationship;
- valid Pattern Map opportunity;
- sufficient familiarity;
- sufficient current coherence.

Low coherence produces safe/basic contributions. High coherence permits more ambitious stylistic expression.

### 13. Fusion Audio Realization

Turn validated technique opportunities into audible musical contributions.

The host track remains authoritative.

Implement a bounded audio realization system using authored stems, one-shots, phrase variants or other pre-produced material chosen from runtime context.

Do not depend on live generative AI during gameplay.

The same structural event may receive different stylistic treatments depending on the active recruit.

### 14. Conditional Recruitment

After Rat Hole, make recruitment performance- and encounter-dependent.

Candidates may come from:

- the current level genre;
- other genres;
- support acts;
- backstage encounters;
- secret gigs;
- returning characters.

Recruit choice should be horizontal: different musical possibilities, not progressively higher-level replacements.

### 15. Musical Chains

Build multi-role combat chains that care about:

- phrase continuity;
- layer alignment;
- timing quality;
- ally joins;
- lane relationships;
- learned techniques;
- coherence.

Do not reduce this to hit count.

### 16. Glam / Punk / Thrash World Authoring

Build each campaign genre as a complete visual and musical world using the same five-role grammar.

- **Glam:** theatrical timing, bait, flourish and obvious accent language.
- **Punk:** direct pulse, aggression, interruption and pressure.
- **Thrash:** speed, subdivision density and precision.

Each world must ship as its own playable proof before the next is authored.

### 17. Black Metal / Death Metal / Doom Recruit Expansion

Add optional cross-genre musician vocabularies without requiring full campaign worlds.

Use Fusion Lab evidence to author techniques and compatibility.

Examples:

- Black Metal tremolo and shriek textures;
- Death Metal blast-beat and growl vocabulary;
- Doom sustain, drone and heavy-resolution vocabulary.

### 18. Prog Murder Chamber

Build the deliberate end-stage systems stress test.

Prove:

- odd meter;
- polymeter/polyrhythm;
- displaced accents;
- long phrase cycles;
- overlapping cells;
- convergence points;
- recruit familiarity;
- automatic learned fusion;
- readable player learning without theory vocabulary.

Thrash is physically savage. Prog is cognitively savage.

---

## Ship Gates

Every phase must satisfy all four before the next phase may depend on it:

1. **Playable or inspectable proof** exists.
2. **Deterministic tests** cover its core contract where applicable.
3. **Human review** confirms the intended feel or musical result.
4. **No regression** to the proven beat-'em-up baseline.

No giant rewrite.
No rhythm-game note highway.
No theory exam.
No runtime dependence on Suno or another cloud generative service.
No recruit style may overwrite the host song's structural authority.

The eventual fever dream is allowed to be complex. The implementation path is not.
