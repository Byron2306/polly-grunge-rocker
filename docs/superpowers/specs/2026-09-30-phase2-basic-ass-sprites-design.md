# Polly Grunge Rocker — Phase 2 Basic-Ass Sprites Design

**Status:** PROPOSED FOR REVIEW  
**Date:** 2026-09-30  
**Branch:** `agent/shitty-block-double-dragon`  
**Phase 1 result:** PASS — human play acceptance confirmed the block prototype is dynamic and engaging.

## 1. Purpose

Phase 2 exists to prove that the visual identity of Polly Grunge Rocker survives contact with the already-proven Phase 1 combat skeleton.

The governing rule is simple:

> **Phase 1 combat remains sovereign. Phase 2 may change presentation, never combat authority.**

Phase 2 replaces rectangles with recognizable, deliberately unfinished pixel sprites and a rough Rat Hole Alley presentation while preserving movement, hit timing, hitboxes, hurtboxes, enemy AI, encounter flow, and zone transitions.

The success condition is not polish. The success condition is that the game becomes visibly Polly Grunge Rocker without losing the dynamic, engaging feel already proven by Shitty Block Fighter.

## 2. Approved aesthetic level

The approved target is a happy medium around the Asset Bible's Pass 2 direction:

- chunky low-detail pixel art;
- silhouettes and palette correct;
- strong pose language;
- recognizable characters at gameplay speed;
- deliberately unfinished detail density;
- no final animation density yet;
- no dependency on visual polish to make combat readable.

Polly should read immediately as Polly through hair, flannel, boots, guitar silhouette, and stance, but Phase 2 should not spend production time on final hair physics, jewelry motion, cloth animation, or exhaustive costume detail.

## 3. Two-frame animation rule

The default animation budget is **two sprites per gameplay state**.

This is intentional. The goal is a chonky illusion of movement with low asset cost.

Two-frame loops should rely on strong pose contrast, timing, hitstop, FX, knockback, and movement velocity to create apparent motion.

### Polly prototype state set

- Idle: 2 frames
- Walk: 2 frames
- Sprint: 2 frames
- Light 1: 2 frames
- Light 2: 2 frames
- Light 3: 2 frames
- Heavy guitar: 2 frames
- Hurt: 2 frames
- Knockback / knockdown: 2 frames
- Get-up: 2 frames
- Pickup / carry: 2 frames
- Victory / end pose: 2 frames

### Glam prototype state set

- Idle / pose: 2 frames
- Walk / swagger: 2 frames
- Attack: 2 frames
- Hurt: 2 frames
- KO / down: 2 frames

### Prog prototype state set

- Idle: 2 frames
- Walk: 2 frames
- Delayed strike: 2 frames
- Special / waveform pose: 2 frames
- Hurt: 2 frames
- KO / down: 2 frames

### Punk prototype state set

- Idle: 2 frames
- Walk / rush: 2 frames
- Shoulder charge: 2 frames
- Hurt: 2 frames
- KO / down: 2 frames

A state may temporarily use one frame if its second frame has not yet been authored, but the renderer and state mapping must be designed for two-frame ownership from the start.

## 4. Visual authority boundary

Simulation state remains authoritative.

The renderer may read:

- actor kind;
- actor state;
- facing;
- movement velocity;
- attack definition;
- attack phase;
- hitstop / hitstun state;
- held pickup;
- depth / ground anchor;
- encounter stage.

The renderer must not decide:

- whether a hit connects;
- when an attack becomes active;
- how far an attack reaches;
- whether an enemy owns an attack token;
- whether an encounter is cleared;
- whether MOVE progression is allowed;
- combat damage, stagger, or knockback values.

This keeps Phase 1 truth intact beneath Phase 2 art.

## 5. Animation mapping layer

Introduce a dedicated visual-state mapping layer between simulation actors and Phaser sprites.

Its responsibility is to convert existing sim truth into presentation keys such as:

```text
POLLY + IDLE                  -> polly.idle
POLLY + moving               -> polly.walk
POLLY + moving + sprint      -> polly.sprint
POLLY + ATTACK + L1          -> polly.light1
POLLY + ATTACK + L2          -> polly.light2
POLLY + ATTACK + L3          -> polly.light3
POLLY + ATTACK + HEAVY       -> polly.heavy
POLLY + HURT                 -> polly.hurt
GLAM  + THREATEN             -> glam.telegraph
GLAM  + ATTACK               -> glam.attack
PROG  + THREATEN             -> prog.hold
PROG  + ATTACK               -> prog.attack
PUNK  + THREATEN             -> punk.windup
PUNK  + ATTACK               -> punk.charge
```

The mapping layer must be deterministic and independently testable.

It should own presentation selection only, not game logic.

## 6. Sprite anchoring and depth

All sprites use the existing ground origin between the feet.

The foot anchor continues to govern:

- world position;
- Y-depth sorting;
- body collision relation;
- shadow position;
- pickup attachment;
- environmental occlusion.

Sprite art may extend far above or beside the actor without changing gameplay position.

Polly's working sprite scale remains approximately 104–120 px tall, centered around the Asset Bible target of roughly 112 px.

## 7. Rendering stack

Per actor, render in this conceptual order:

1. ground shadow;
2. character sprite;
3. held pickup / weapon sprite if applicable;
4. attack FX;
5. hit / KO FX;
6. optional debug geometry overlay.

The current rectangle renderer is not deleted. It becomes a debug/fallback presentation path.

## 8. Debug geometry toggle

Phase 2 must preserve the geometric truth developed during Phase 1.

Provide a debug mode capable of showing:

- body boxes;
- hurtboxes;
- attack shapes;
- enemy telegraph geometry;
- Polly guitar sweep geometry.

The normal aesthetic mode should hide raw geometry by default, while still permitting selected stylized telegraph FX where they improve readability.

The debug overlay exists so sprite art cannot hide bad spacing, range, or timing.

## 9. Polly visual identity

Phase 2 Polly must preserve these silhouette anchors:

- large auburn / red hair mass;
- open red-and-black flannel;
- dark sleeveless grunge top;
- torn dark jeans;
- heavy black boots;
- chain / necklace cues only where readable at prototype density;
- oversized guitar silhouette during Heavy.

Her idle should remain relaxed and cool rather than permanently angry. Combat poses may become explosive.

The two-frame approach should exaggerate pose contrast rather than relying on many in-between frames.

## 10. Attack presentation

### Light combo

Each light attack gets a distinct body pose pair.

- L1: compact, direct jab / straight silhouette;
- L2: more torso rotation or backhand shape;
- L3: visibly larger finisher silhouette.

The existing geometric strike bars remain available in debug mode.

### Heavy guitar

The guitar is visually prominent and may use a separate weapon / FX layer.

The Heavy presentation combines:

- two strong Polly body poses;
- separate guitar swing presentation;
- separate broad swing arc FX;
- hit spark;
- hitstop;
- knockback.

The guitar arc must remain a separate FX asset rather than being permanently baked into Polly's sprite.

## 11. Enemy visual grammar

### Glam

Prototype identity:

- large teased-hair silhouette;
- theatrical stance;
- elegant / cocky posture;
- saturated glam palette cues.

Telegraphing should visually support the existing long-windup bait/punish behavior.

### Prog

Prototype identity:

- glasses / academic musician silhouette;
- controlled posture;
- keytar or keyboard-like accessory if readable;
- angular visual language.

The delayed timing should be supported by restrained waveform geometry or FX, not replaced by animation timing logic.

### Punk

Prototype identity:

- tall mohawk;
- sleeveless / patched silhouette;
- forward lean;
- chain / boot cues;
- compressed aggressive posture.

The rush should visually read as velocity and pressure through pose, debris, and attack FX.

## 12. Rat Hole Alley Phase 2 environment scope

Phase 2 introduces a compact modular environment kit, not a giant flattened painting.

Minimum representative set:

- brick wall / alley background modules;
- club door / facade;
- neon sign;
- poster modules;
- fence / pipe detail;
- dumpster;
- asphalt / pavement gameplay plane;
- puddle decals;
- one or two foreground clutter elements;
- existing bottle and mic stand represented visually.

The environment should read as filthy, rainy, musical, urban, and grunge-adjacent while remaining visually subordinate to combat readability.

Parallax may remain minimal in Phase 2.

## 13. FX scope

Phase 2 adds rough prototype FX with a screen-printed gig-poster violence direction:

- light hit spark;
- heavy hit spark;
- guitar swing arc;
- Glam telegraph accent;
- Prog angular waveform;
- Punk rush debris / streak;
- KO burst;
- bottle-break fragments;
- small movement dust / debris where useful.

FX serve timing first and style second.

They must not conceal hitboxes or make active windows ambiguous.

## 14. UI and mobile readability

The Phase 1 mobile control layout remains intact unless playtesting reveals a real issue.

Phase 2 may skin basic HUD elements, but must preserve readability on phone screens.

Minimum HUD work:

- cleaner Polly health presentation;
- encounter / MOVE messaging compatible with the aesthetic;
- optional portrait placeholder;
- debug text available behind a development toggle.

No inventory, progression tree, minimap, or elaborate menu work belongs in Phase 2.

## 15. Audio boundary

Temporary audio may enter in Phase 2, but only as placeholders.

Allowed:

- light hit sound;
- heavy guitar swish / impact;
- hurt / KO placeholder sounds;
- small movement cues;
- basic ambient alley loop if readily available.

Final music, voice barks, and finished sound design remain Phase 3 work.

## 16. Production order

Implement in this order:

1. visual-state mapping layer and renderer seam;
2. Polly core proof: idle, walk, sprint, L1, Heavy;
3. debug geometry toggle;
4. Glam visual set;
5. Punk visual set;
6. Prog visual set;
7. remaining Polly states;
8. Rat Hole Alley modular environment;
9. rough combat FX;
10. basic HUD skin and placeholder audio if useful;
11. full Phase 2 playtest pass on mobile and desktop.

This order keeps the aesthetic risk front-loaded into the smallest useful slice.

## 17. Testing strategy

### Unit tests

Add tests for:

- simulation-state to visual-state mapping;
- deterministic two-frame selection;
- facing / mirroring behavior;
- debug geometry enable / disable contract;
- sprite descriptor depth from ground anchor;
- fallbacks when an asset or second frame is missing.

### Integration tests

Verify:

- Phase 1 combat values do not change;
- attack active windows remain simulation-driven;
- MOVE encounter progression is unchanged;
- sprite renderer can coexist with debug geometry;
- mobile controls still feed the same `PlayerIntent` contract;
- no rendered sprite changes body / hurt / attack geometry.

### Human play acceptance

Phase 2 is not complete until a human play pass confirms:

- combat remains at least as dynamic and engaging as Phase 1;
- Polly reads clearly in motion;
- Glam, Prog, and Punk are distinguishable at a glance;
- telegraphs remain readable;
- Heavy guitar reads as a signature swing;
- MOVE transitions still feel good;
- mobile combat remains clear and comfortable.

## 18. Phase 2 acceptance gate

Phase 2 passes only when all of the following are true:

1. The block renderer is no longer required for normal play.
2. Polly is immediately recognizable through silhouette and color.
3. All three enemy archetypes are readable at gameplay speed.
4. The two-frame animation approach feels intentionally chonky rather than broken.
5. Combat timing and feel remain Phase 1-equivalent.
6. Attack telegraphs remain clear with sprites present.
7. Rat Hole Alley has a coherent rough aesthetic identity.
8. Debug geometry can still expose the underlying truth.
9. Mobile readability remains strong.
10. Human play acceptance is PASS.

## 19. Explicitly out of scope

Phase 2 does **not** include:

- final animation frame counts;
- full secondary hair / cloth motion;
- final parallax treatment;
- final rain / lighting / reflections;
- final UI;
- final music;
- final voice work;
- boss implementation;
- progression systems;
- new combat mechanics merely because sprites exist;
- rewriting proven Phase 1 timings for aesthetic convenience.

Those belong to later phases unless a Phase 2 acceptance failure demonstrates they are necessary.

## 20. Design summary

Phase 2 is a presentation ratchet, not a combat rewrite.

Shitty Block Fighter already proved the game can be fun without aesthetics. Basic-Ass Sprite Mode now asks whether a small amount of deliberately chunky art can make that same game unmistakably Polly Grunge Rocker.

The guiding principle is:

> **Two strong frames, truthful timing, loud silhouettes, dirty FX, zero bullshit.**
