# Polly Grunge Rocker — Pattern Map Programme Roadmap

**Date:** 2026-09-30
**Status:** APPROVED DESIGN → IMPLEMENTATION PROGRAMME

## Programme Order

### 0. Rat Hole closeout
- Tighten upper walk boundary based on accepted screenshot.
- Re-run local combat gauntlet.
- Freeze Phase 2B.1 as the visual/combat baseline.

### 1. Phase 2C — Rat Hole Visual Upgrade
Goal: replace the current flat staging with the grimy, neon, wet, violent visual language established in the approved mockup.

No Pattern Map runtime work lands here. Phase 2C must preserve the combat baseline.

### 2. Pattern Map Foundation
Build deterministic track-map data structures, validation, querying, fixtures and inspection tooling.

This is the first implementation plan attached to this roadmap.

### 3. Pattern Map Authoring / Analysis Tool
Build the tool that ingests stems/MIDI/audio and assists with:
- BPM/downbeat detection
- meter candidates
- onset/transient extraction
- repeated pattern candidates
- phrase/riff annotations
- cross-layer alignment candidates
- manual correction and export

Human review remains final authority.

### 4. Audio Clock + Runtime Synchronization
Create a single authoritative track clock and deterministic mapping between:
- audio time
- Pattern Map time
- simulation time
- beat/bar/phrase position

No gameplay advantage is added yet. This phase proves timing truth.

### 5. Musical Input Evaluation
Evaluate attacks against Pattern Map windows:
- acceptable
- on-pattern
- accent-perfect
- phrase-perfect
- alignment-perfect

Keep existing combat moves intact while adding timing metadata.

### 6. Soft Combat Lanes
Interpret the existing free Y-axis as upper/middle/lower tactical bands without turning movement into rigid rails.

Add:
- lane occupancy
- lane transitions
- cross-lane targeting
- lane-aware attack metadata

### 7. Performance Score
Score clean play:
- timing
- damage avoidance
- efficiency
- phrase completion
- lane control
- interrupts
- expressive combat

Prevent score farming.

### 8. Recruitment
Use performance output between encounters to recruit:
- named recurring allies
- temporary locals

Recruits are musical-role capabilities, not generic stat sticks.

### 9. Ally AI + Coherence
Allies fight autonomously according to:
- musical role
- lane tendency
- learned patterns
- current synchronization

Add player-side and enemy-side coherence.

### 10. Teaching Recruits
Polly can step into another musical role/lane and demonstrate the correct pattern.

Successful demonstration increases a recruit's confidence in that pattern.

This is where Polly becomes fighter + guitarist + bandleader.

### 11. Musical Chains
Build multi-layer combat chains and synchronized finishers.

Chains care about:
- timing
- phrase continuity
- layer alignment
- ally joins
- lane relationships

Not merely hit count.

### 12. Genre Authoring
Author the shared five-role grammar across:
- Grunge
- Punk
- Glam
- Thrash
- Prog

Each genre changes the timing language while preserving transferable role meaning.

### 13. Prog Murder Chamber
Create the deliberately complex Prog stress-test track.

The encounter should prove:
- odd meter
- overlapping layer patterns
- displaced accents
- phrase cycles
- cross-layer convergence

The player must be able to learn it without knowing formal theory vocabulary.

## Non-Negotiable Rule

Each stage must ship as a playable proof before the next layer of architecture is allowed to depend on it.

No giant rewrite.
No rhythm-game note highway.
No theory exam.
No replacement of the proven beat-'em-up combat feel.

**MAP THE PATTERNS.**
