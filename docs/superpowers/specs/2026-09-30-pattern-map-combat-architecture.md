# Polly Grunge Rocker — Pattern Map Combat, Recruitment and Fusion Architecture

**Date:** 2026-09-30  
**Status:** DESIGN LOCK — REVIEW REQUIRED BEFORE IMPLEMENTATION PLAN UPDATE  
**Programme branch:** `agent/polly-pattern-map-programme`

## 1. Canon

Polly Grunge Rocker is a belt-scrolling beat-'em-up in which music is not background decoration. Music is the battlefield grammar.

Two phrases define the system:

> **MAP THE PATTERNS.**

> **STRUCTURE IS SHARED. STYLE IS PERSONAL.**

A third phrase defines the runtime relationship between a level track and recruited musicians:

> **The song tells you where. The musician tells you how.**

The host level's genre owns the underlying musical structure: tempo, meter, section boundaries, phrase timing, harmonic motion, accents, rests, transitions and cross-layer alignment windows. Recruited musicians do not replace that song. Their learned techniques reinterpret valid structural opportunities inside it.

The result should feel like a live band learning how to fight inside somebody else's musical language until strange but coherent fusion emerges.

The game must remain fun as a beat-'em-up even before the player consciously understands any theory vocabulary.

---

## 2. Campaign Genre Progression

A level is a genre world, not merely a location with genre-themed enemies.

The campaign baseline is:

1. **Rat Hole — Grunge**
2. **Glam**
3. **Punk**
4. **Thrash**
5. **Prog**

The intended learning curve is:

- **Grunge:** familiar, readable, human, forgiving. Learn the common musical grammar.
- **Glam:** theatrical exaggeration, baiting, obvious accents, performance flourishes.
- **Punk:** pressure, aggression, direct pulse, short decision windows.
- **Thrash:** speed, subdivision density, relentless precision.
- **Prog:** structural ambiguity, odd meter, polymeter/polyrhythm, displaced accents, long phrase cycles, convergence points.

Thrash is physically savage. Prog is cognitively savage.

Later optional recruit genres may include Black Metal, Death Metal, Doom and other scenes without requiring those genres to become full campaign worlds immediately.

---

## 3. Rat Hole Is Grunge Home Turf

Rat Hole is the first level and Polly's home scene.

It is not a generic alley where Glam, Punk and Prog enemies happen to appear. Those archetypes were useful vertical-slice test pieces. The production campaign version of Rat Hole becomes a Grunge social ecosystem and onboarding scaffold.

Rat Hole contains local musicians, rivals, friends, scene regulars, roadies and bands. They are not ideological gatekeepers and they are not anti-other-genre zealots. They love Grunge. Rivalries can be real, physical and competitive, but the scene remains Polly's community.

The emotional premise is:

- this is home;
- these people know Polly;
- they can knock her flat and still share a drink later;
- the player learns the game's musical grammar by sparring with people who already understand it.

Rat Hole should feel like a rehearsal room, proving ground and local music scene without ever presenting itself as a tutorial academy.

---

## 4. Rat Hole Scaffolding Progression

Rat Hole teaches one musical layer at a time and gradually assembles Polly's starter band.

### Act 1 — Polly Alone

Polly occupies the **Lead / Keys** role as the game's melodic, adaptive fighter.

The opening teaches:

- movement and belt-scroller depth;
- basic attacks and spacing;
- attack timing;
- repeated riff cells;
- phrase anticipation;
- the idea that combat can sit inside the song rather than merely occur over it.

### Act 2 — Drummer

Primary lesson: **Time**.

Teach:

- pulse;
- beat;
- subdivisions;
- accents;
- readable anticipation;
- the difference between merely landing a hit and landing it inside a useful timing window.

The drummer becomes a guaranteed story recruit.

### Act 3 — Bassist

Primary lesson: **Groove**.

Teach:

- repeated low-end anchors;
- lane stability;
- sustained rhythmic continuity;
- moving while preserving groove;
- how one role can create space for another.

The bassist becomes a guaranteed story recruit.

### Act 4 — Rhythm Guitarist

Primary lesson: **Structure**.

Teach:

- repeating riff cells;
- pattern continuation;
- chain structure;
- recognizing when repetition changes;
- committing to a phrase rather than treating every hit as isolated.

The rhythm guitarist becomes a guaranteed story recruit.

### Act 5 — Vocalist

Primary lesson: **Call / Response and Disruption**.

Teach:

- phrase calls;
- interruptions;
- counters;
- response timing;
- crowd-control-like disruption windows.

The vocalist becomes a guaranteed story recruit.

### Rat Hole Finale — Full Band Battle

The final Rat Hole battle combines the complete five-role grammar.

The game should stop explicitly isolating lessons and let the player hear that all previous lessons were layers of the same musical language.

The intended realization is:

> "Those separate lessons were the song."

Rat Hole ends with Polly's full starter band assembled.

---

## 5. Starter Band Is Guaranteed

This decision is locked.

Rat Hole's four core recruits are guaranteed story recruits:

- Drummer
- Bassist
- Rhythm Guitarist
- Vocalist

Polly fills Lead / Keys.

The player cannot accidentally leave the onboarding level without a complete party because of poor score or missed optional objectives.

Performance during Rat Hole may affect:

- dialogue;
- respect reactions;
- initial familiarity values;
- starting confidence;
- optional rematches;
- cosmetic acknowledgements;

It does not block the four required recruits.

After Rat Hole, recruitment becomes conditional and expressive.

---

## 6. Shared Five-Role Musical Grammar

Every genre uses the same semantic roles so knowledge transfers between worlds.

### Drums

Owns:

- pulse;
- subdivisions;
- fills;
- tempo pressure;
- accent density.

### Bass

Owns:

- groove;
- low-end anchor;
- lane stability;
- recurring movement patterns;
- structural glue.

### Rhythm Guitar

Owns:

- repeating riffs;
- chugs;
- recurring structural cells;
- phrase skeletons.

### Lead / Keys

Owns:

- melody;
- phrasing;
- anticipation;
- syncopation;
- resolution;
- adaptive interpretation.

Polly occupies this role by default.

### Vocals

Owns:

- calls;
- interruptions;
- crowd control;
- phrase timing;
- call-response relationships.

A later electronic or industrial genre may reskin the instrumentation, but the semantic roles remain transferable.

---

## 7. Pattern Map

Every combat track is accompanied by a machine-readable Pattern Map.

The Pattern Map is deterministic domain data. It is not the audio engine and it is not a rhythm-game note highway.

It describes:

### Global timing

- absolute track time;
- BPM regions;
- tempo changes;
- meter/time-signature regions;
- bar and beat position;
- subdivision relationships;
- sections;
- transitions;
- phrase boundaries.

### Per-role events

For Drums, Bass, Rhythm Guitar, Lead / Keys and Vocals:

- onset;
- accent;
- repeated cell;
- phrase start;
- phrase end;
- fill;
- rest;
- tension;
- resolution.

### Cross-layer alignment events

The map records moments where several layers converge.

These can become candidates for:

- stronger staggers;
- coordinated ally joins;
- finishers;
- recruitment evaluation moments;
- fusion opportunities;
- high-confidence automatic technique expression.

Pattern Map data must be queryable from explicit track time and must not depend on `Date.now()`, Phaser or WebAudio.

---

## 8. Pattern Map Authoring / Analysis Tool

Because the game cannot rely on the developer manually annotating complex Prog by ear forever, the programme requires a dedicated authoring tool.

The tool should ingest available stems, MIDI and/or rendered audio and assist with:

- BPM candidates;
- downbeats;
- meter candidates;
- onset/transient detection;
- repeated-cell candidates;
- phrase/riff candidates;
- section boundaries;
- cross-layer alignment candidates;
- confidence visualization;
- manual correction;
- final deterministic export.

Automatic analysis is advisory.

Human correction is final authority.

The tool must support deliberately complex material including odd meter, tempo changes and overlapping phrase cycles.

---

## 9. Music Is Learned Through Play, Not Theory Vocabulary

The player does not need to know terms like syncopation, polymeter or metric modulation.

The teaching grammar is:

> **sound → body language → visual anticipation → action → payoff**

A musician may recognize formal theory. A non-musician should still be able to notice:

> "It goes da-da-DA, then he swings."

Difficulty can deepen recognition without becoming a theory exam:

- beginner: beat cues;
- intermediate: repeated patterns;
- advanced: phrases/riffs;
- expert: multiple layers and cross-layer convergence.

No Guitar Hero-style note highway is required.

---

## 10. Soft Combat Lanes

The existing free Y-axis remains a belt-scroller space.

It evolves into approximately three functional bands without becoming rigid rails.

Lanes provide meaning for:

- role tendencies;
- ally positioning;
- lane control;
- teaching demonstrations;
- cross-lane attacks;
- formation coherence.

Exact lane count and widths remain tuneable implementation constants rather than narrative rules.

---

## 11. Recruitment After Rat Hole

After the guaranteed Grunge starter band, recruits are optional and can be encountered through:

- current-level musicians;
- rival or support acts;
- scene crossovers;
- backstage encounters;
- secret gigs;
- visiting musicians;
- optional battles;
- returning characters.

A Glam level can therefore contain a Black Metal guitarist, Doom bassist or Punk drummer without requiring the whole level to change genre.

Recruitment should be based on demonstrated performance and encounter context rather than simple experience level.

Possible evaluation inputs include:

- timing quality;
- damage avoided;
- efficiency;
- phrase completion;
- lane control;
- useful interrupts;
- multi-layer coherence;
- successful technique placement;
- expressive combat without score farming.

Recruits are not vertical RPG upgrades. They are musical possibilities.

---

## 12. Musician Identity Model

A musician is defined by persistent identity plus learnable familiarity.

### Core musical attributes

Core attributes describe tendencies rather than generic power levels.

Recommended universal dimensions:

- **Tempo Handling** — ability to operate cleanly at demanding speeds.
- **Groove Stability** — ability to maintain useful rhythmic continuity.
- **Phrase Reading** — ability to anticipate and resolve structural phrases.
- **Precision** — consistency inside narrow timing windows.
- **Adaptability** — ability to operate outside the musician's native genre.

These should stay mostly stable. They define character identity.

### Technique vocabulary

Techniques describe how a musician expresses structure.

Examples:

- Tremolo Picking
- Blast-Beat Lock
- Palm-Mute Precision
- Syncopated Chug
- Sustained Doom Resolution
- Falsetto Call
- Growl Projection
- Shriek Accent
- Harmonic Density
- Odd-Meter Literacy
- Drone Stability

A technique is not simply `+14 damage`.

It is a musical solution with structural conditions.

### Genre familiarity

Familiarity is learnable.

A Death Metal drummer remains a Death Metal drummer, but can become increasingly fluent at placing Death Metal vocabulary inside Prog, Glam or Punk structure.

This preserves identity while allowing meaningful growth.

---

## 13. Knowledge, Familiarity, Coherence, Technique and Opportunity Are Separate

These concepts must not collapse into one stat.

### Knowledge

What pattern-technique relationships the recruit has actually learned.

### Familiarity

How well the recruit understands a host genre or pattern family.

### Coherence

How well the current band is functioning together right now.

### Technique

What stylistic musical vocabulary the recruit can perform.

### Opportunity

Whether the current Pattern Map contains a valid structural opening for that vocabulary.

Automatic expression occurs only when these conditions align.

Conceptually:

```text
learned relationship
+ valid Pattern Map opportunity
+ sufficient familiarity
+ sufficient current coherence
= automatic stylistic contribution
```

There is no random automatic technique spam.

---

## 14. Teaching Recruits

Polly can teach recruits by stepping into their musical role/lane and demonstrating the correct structure.

The loop is:

1. recruit performs poorly or fails to recognize a pattern;
2. player notices;
3. Polly enters the relevant role/lane;
4. Polly performs the correct Pattern Map timing;
5. the game evaluates the demonstration;
6. recruit knowledge/confidence increases;
7. recruit later reproduces the learned timing autonomously.

The key principle is:

> Polly does not teach the recruit to stop sounding like themselves. She teaches them where their own vocabulary fits.

A Death Metal drummer can learn an odd-meter blast relationship without becoming a Prog drummer.

A Black Metal guitarist can learn where tremolo belongs in a Glam phrase without becoming a Glam guitarist.

This creates character progression without homogenization.

---

## 15. Coherence

Coherence represents the band's present shared understanding.

It is not merely a special-move meter.

Coherence reflects factors such as:

- player timing;
- ally timing;
- lane coordination;
- phrase continuity;
- successful responses;
- damage avoidance;
- whether multiple members are recognizing the same structural moment.

### Low coherence

Musicians play safely.

They may:

- use simpler contributions;
- hesitate;
- miss optional fusion windows;
- avoid ambitious ornaments.

### High coherence

Musicians become musically ambitious.

They may automatically:

- answer phrases;
- ornament valid windows;
- harmonize;
- contribute genre-specific fills;
- join multi-layer chains;
- trigger learned fusion techniques.

The desired player feeling is:

> "He heard it too."

Automatic ally expression should be foreshadowed by readable body-language and/or audio cues rather than appearing as unexplained effects.

---

## 16. Host Genre Owns Grammar; Recruit Genre Owns Accent

This is a locked rule.

The active level track remains the host.

The host owns:

- tempo;
- meter;
- phrase lengths;
- section changes;
- harmonic motion;
- structural accents;
- rests;
- alignment windows.

A recruit contributes an alternate **performance treatment** at a valid event.

Example phrase:

```text
E5 - G5 - A5 - G5
```

Possible treatments:

- Glam: clean theatrical lead.
- Black Metal: tremolo-picked figure.
- Punk: octave attack.
- Doom: sustained heavy resolution.
- Prog: displaced or syncopated interpretation.

The phrase identity and structural location remain valid.

The timbre, articulation and technique change.

This is how cross-genre fusion avoids becoming unrelated audio pasted over the song.

---

## 17. Fusion Compatibility

Technique placement should be classified by compatibility rather than simple good/bad bonuses.

A useful authoring model is:

### Native

The technique naturally fits the host structure and can appear relatively freely once learned.

### Fusion

The technique can enrich the host when used selectively in valid structural windows.

### Clash

The technique is only musically useful in rare, explicitly authored opportunities.

`Clash` does not mean forbidden forever. It means placement tolerance is narrow.

Compatibility is between a technique and musical structure, not merely between two genre labels.

For example, tremolo picking may be:

- native in Black Metal;
- comfortable fusion in Prog or Thrash;
- selective fusion in Glam;
- highly contextual in Doom.

The Pattern Map opportunity remains authoritative.

---

## 18. Automatic Fusion After Learning

This decision is locked.

The player does **not** manually trigger every learned ally technique forever.

Learning is explicit. Expression becomes automatic.

The recruit's behavior progresses through three broad states:

### Unlearned

- does not understand the relationship;
- may fail to use the technique appropriately;
- can require Polly demonstration.

### Learned, Low Coherence

- technically understands the pattern;
- tends toward safe/basic phrasing;
- uses signature techniques rarely.

### Learned, High Coherence

- recognizes valid opportunities automatically;
- expresses learned genre vocabulary inside the host song;
- can participate in fusion chains and alignments.

The result is **earned automatic musical intelligence**.

---

## 19. Audible Party Composition

Party composition must become audible.

A recruit's genre identity is not merely a character-sheet property. Successful rhythmic expression contributes actual timbre, articulation or fill material to the fight.

Examples:

- Black Metal lead inserts a tremolo-picked melodic fill.
- Death Metal drummer contributes a short blast-beat fill.
- Doom bassist holds a massive low-end resolution.
- Glam vocalist answers with a harmonized or high-register call.
- Punk rhythm guitarist attacks a structural cell with terse octave/chord emphasis.

Two players fighting the same Prog encounter with different bands should be capable of producing recognizably different arrangements while still obeying the same host Pattern Map.

The game is therefore capable of emergent fusion such as:

> Prog host + Death Metal drums + Doom bass + Black Metal rhythm guitar + Glam vocals + Polly's Grunge melodic identity.

This should sound intentional when coherence and placement are high, not like six unrelated stems colliding.

---

## 20. Audio Realization Boundary

The runtime should not depend on free-form generative audio to make the core combat system work.

Pattern recognition and gameplay decisions remain deterministic.

A practical production architecture is:

1. Pattern Map event is active.
2. Host track defines current musical context.
3. Recruit technique offers one or more authored compatible realizations.
4. Runtime checks knowledge, familiarity, coherence and opportunity.
5. If valid, an authored audio treatment is selected.
6. The treatment is quantized/placed against the authoritative audio clock.
7. Its mix level and duration are constrained so it enriches rather than replaces the host.

Possible realization assets include:

- short fills;
- alternate articulations;
- phrase stems;
- one-shot accents;
- layered timbral variants;
- harmonized response clips.

The host song remains recognizable.

---

## 21. Suno Fusion Lab

Suno is a pre-production experimentation tool for discovering what bizarre combinations actually work by ear.

It is not required as a runtime dependency.

The programme should deliberately create a **Fusion Lab** corpus containing controlled experiments such as:

- Glam host + Black Metal tremolo lead;
- Punk host + Death Metal blast fills;
- Doom host + Glam vocal harmonies;
- Prog host + Punk drummer;
- Thrash host + Doom bass sustain;
- Grunge host + Black Metal vocal treatment;
- odd-meter Prog + Death Metal drum vocabulary;
- Glam chorus + tremolo ornament;
- Punk refrain + blast-beat transition;
- Doom resolution + high-register theatrical vocal answer.

Each experiment should answer:

1. Does the guest style enrich the host or hijack it?
2. Which structural windows make it work?
3. Which timbral frequency ranges collide?
4. How long can the guest technique remain active before the host identity is lost?
5. Is the combination readable during combat?
6. Does the result suggest a reusable technique rule or only a one-off authored moment?

The lab should create evidence for compatibility tables and audio-asset authoring.

It should not replace deterministic Pattern Map authoring.

---

## 22. Performance and Recruitment

Performance scoring should evaluate musical combat quality rather than raw hit count.

Useful dimensions include:

- timing accuracy;
- phrase completion;
- damage avoidance;
- efficient use of openings;
- lane control;
- successful responses;
- clean interrupts;
- ally joins;
- alignment participation;
- coherence maintenance;
- successful learned-technique placement.

After Rat Hole, recruit availability can depend on combinations of:

- encounter completion;
- minimum demonstrated competence;
- specific musical feats;
- optional side encounters;
- current party composition;
- prior interactions.

Do not use a simple `Level N recruit replaces Level N-1 recruit` ladder.

A new recruit should create a new musical option, not make a loved character obsolete by arithmetic.

---

## 23. Genre Familiarity Progression

Core musician identity stays mostly stable.

What grows strongly is familiarity.

Example:

```text
Death Metal drummer
Prog familiarity: 12% → 31% → 58%
```

At higher familiarity, the drummer is better at identifying where Death Metal vocabulary fits into Prog structure.

This can unlock cross-genre techniques such as:

```text
ODD-METER BLAST
requires:
- Death Metal drum technique vocabulary
- sufficient Prog familiarity
- learned odd-meter relationship
- successful demonstrations / use
```

Growth means learning to place your own identity intelligently, not becoming stylistically neutral.

---

## 24. Musical Chains

Combo quality eventually becomes multi-layer musical continuity rather than merely hit count.

Chains care about:

- timing;
- phrase continuity;
- role alignment;
- lane relationships;
- ally joins;
- successful responses;
- structural resolution;
- valid fusion techniques.

A chain may be described conceptually as multiple layers locking rather than `17 hits`.

The UI should remain restrained. The system can understand rich state without constantly shouting genre algebra at the player.

Occasional high-value feedback such as `3 LAYERS LOCKED` is preferable to constant explanatory text.

---

## 25. Visual Campaign Mapping

Every genre world needs the same production-art quality while changing material language.

### Rat Hole / Grunge

- painterly pixel art;
- dirty brick;
- wet asphalt;
- battered wood and metal;
- posters layered over posters;
- dumpsters, cables, bottles, amps;
- warm club light against cold rain;
- tactile, human, lived-in clutter.

This is Polly's natural habitat.

### Glam

- chrome;
- lacquer;
- mirrors;
- velvet;
- dressing-room bulbs;
- hot pink/cyan/gold stage spill;
- decadent backstage excess.

### Punk

- DIY warehouse/squat;
- pasted flyers;
- stencil art;
- broken signage;
- barricades;
- fluorescent tubes;
- beer crates;
- patched fencing.

### Thrash

- industrial freight/rehearsal spaces;
- steel;
- corrugated metal;
- concrete;
- floodlights;
- smoke;
- repetitive architectural rhythm.

### Prog

- brutalist or high-design performance architecture;
- controlled geometry;
- asymmetric repetition;
- overlapping visual cycles;
- structural patterns that can subtly mirror polyrhythmic ideas.

The environment can teach musical structure visually without becoming a puzzle diagram.

---

## 26. Rat Hole Art Direction Correction

Production Rat Hole must not use flat, primitive, adventure-game-like environmental plates as its final visual language.

The approved target is dense painterly pixel art with:

- material texture;
- deep light and shadow;
- believable clutter;
- environmental storytelling;
- strong foreground/background separation;
- irregular wet reflections;
- occlusion around doors and recesses;
- cohesive pixel density;
- spaces that feel inhabited rather than diagrammed.

Procedurally assembled flat primitives are acceptable for prototypes only.

The visual benchmark is the approved Rat Hole mock-up shown during Phase 2C discussion.

---

## 27. Runtime Data Boundaries

The architecture should evolve into isolated modules with clear ownership.

### Pattern Map Domain

Owns structural musical truth.

### Audio Clock

Owns authoritative current track time and deterministic mapping between audio time, simulation time and Pattern Map time.

### Timing Evaluator

Evaluates player/allied actions against Pattern Map windows.

### Musician Model

Owns role, home genre, core attributes, techniques, knowledge and familiarity.

### Coherence Engine

Owns current band synchronization state.

### Opportunity Resolver

Matches learned techniques against current structural opportunities.

### Fusion Realizer

Selects and schedules authored audio treatments without changing structural truth.

### Recruitment Evaluator

Consumes performance evidence and encounter rules to decide recruit availability.

### Teaching System

Evaluates Polly demonstrations and updates recruit knowledge/familiarity.

### Ally AI

Chooses movement and combat behavior using role, lane, learned patterns, coherence and opportunity signals.

No single module should own all of these concerns.

---

## 28. Revised Implementation Programme

The previous roadmap remains directionally correct but must be expanded because Rat Hole is now the onboarding scaffold and fusion is a first-class system.

The implementation programme should be rewritten into these stages after this spec is approved.

### Phase 0 — Rat Hole Baseline Closeout

Preserve the proven Phase 1/2 combat feel and approved walk-band behavior.

### Phase 1 — Rat Hole Production Art

Replace prototype flat environmental plates with production-quality painterly pixel-art scene layers while preserving collision and combat coordinates.

### Phase 2 — Pattern Map Foundation

Build pure deterministic types, validation, queries, fixtures and inspection tooling.

Existing foundation plan remains the starting point.

### Phase 3 — Pattern Map Authoring / Analysis Tool

Build ingestion, candidate detection, manual correction and deterministic export.

### Phase 4 — Fusion Lab

Before dynamic fusion runtime exists, use controlled Suno/audio experiments to establish:

- host/guest compatibility evidence;
- useful technique categories;
- mix/timbre constraints;
- examples of successful and failed fusion.

The output is an authored test corpus plus compatibility rules, not production runtime code.

### Phase 5 — Audio Clock and Runtime Sync

Establish authoritative track time and deterministic Pattern Map synchronization.

### Phase 6 — Musical Input Evaluation

Evaluate attacks and movement events against beat, phrase and alignment windows while preserving current combat moves.

### Phase 7 — Rat Hole Scaffolding Encounters

Rebuild Rat Hole encounter progression around:

- Polly alone;
- Drummer lesson/recruit;
- Bass lesson/recruit;
- Rhythm Guitar lesson/recruit;
- Vocal lesson/recruit;
- Full Band finale.

Guarantee all four starter recruits.

### Phase 8 — Party and Soft-Lane Foundation

Add role-aware allies, soft combat bands, lane tendencies and party presentation without advanced fusion.

### Phase 9 — Performance and Coherence

Add performance evidence, current-band coherence and readable feedback.

### Phase 10 — Teaching and Learning

Implement Polly demonstration, recruit knowledge, confidence and genre familiarity progression.

### Phase 11 — Technique Vocabulary

Implement musician techniques as structural capabilities rather than stat bonuses.

### Phase 12 — Automatic Opportunity Resolution

Once learned, allies automatically detect valid opportunities according to knowledge, familiarity and coherence.

### Phase 13 — Fusion Audio Realization

Layer authored fills/treatments into the host track at validated opportunities.

The host song remains authoritative and recognizable.

### Phase 14 — Conditional Recruitment

Implement post-Rat-Hole performance/encounter recruitment and cross-genre candidates.

### Phase 15 — Musical Chains

Implement multi-layer joins, alignments and synchronized resolutions/finishers.

### Phase 16 — Genre World Authoring

Author Glam, Punk and Thrash using the shared grammar but distinct visual, behavioral and musical languages.

### Phase 17 — Cross-Genre Recruit Expansion

Add optional recruit families such as Black Metal, Death Metal and Doom with authored techniques and fusion compatibility.

### Phase 18 — Prog Murder Chamber

Build the deliberate final complexity stress test:

- odd meter;
- polymeter/polyrhythm;
- displaced accents;
- overlapping phrase cycles;
- metric changes where useful;
- convergence windows;
- learned cross-genre ally vocabulary.

The player must be able to learn it through play without formal theory terminology.

---

## 29. Acceptance Vision

The architecture succeeds when all of the following can be true at once:

1. A player who knows no music theory can learn Rat Hole through sound, animation and action.
2. Rat Hole naturally assembles Polly's complete Grunge starter band.
3. The player later recruits musicians because of musical possibilities, not larger numbers.
4. A Black Metal guitarist remains recognizably Black Metal after learning Prog.
5. A Death Metal drummer can learn where a blast beat belongs in an odd-meter phrase.
6. Learned ally expression becomes automatic when current coherence is high enough.
7. The host song remains structurally and audibly recognizable.
8. Successful recruit contributions sound like intentional fills, articulations, harmonies or responses.
9. Two different party compositions can produce audibly different versions of the same encounter.
10. Cross-genre combinations can become strange, beautiful fusion instead of uncontrolled audio mud.
11. Prog can challenge the player's structural understanding without requiring a theory textbook.
12. The original beat-'em-up remains satisfying even if the player never verbalizes the architecture beneath it.

The ultimate fantasy is not simply "win the fight."

It is:

> enter another scene, hear its language, survive it, understand it, teach your band how to inhabit it, and eventually make something musically new inside it.

**MAP THE PATTERNS.**
