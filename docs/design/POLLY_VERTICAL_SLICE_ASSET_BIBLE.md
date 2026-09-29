# Polly Grunge Rocker — Vertical Slice Asset Bible

**Status:** CANONICAL / APPROVED  
**Version:** 0.1  
**Approved direction:** Pass A complete  
**Project:** Polly Grunge Rocker  
**Vertical slice:** The Rat Hole Alley

## 1. Vertical-slice objective

Build one short, brutally clear arcade-brawler proof that demonstrates five things:

1. Polly feels great to control.
2. One street chunk has the correct grunge-rock atmosphere.
3. Three enemy archetypes feel mechanically distinct.
4. Combat feedback is crunchy, readable, and satisfying.
5. The art pipeline is repeatable without drowning production in asset work.

The first playable proof is intentionally small: one rainy club alley, Polly, three enemy archetypes, three short encounters, basic pickups, one destructible/environment interaction, and roughly 60–90 seconds of gameplay.

The slice exists to answer one question: **is controlling Polly and beating musical pretension out of people ridiculously fun?**

No boss, progression system, giant level, or sprawling moveset is required for the first proof.

---

## 2. Production philosophy: three-pass ratchet

Every gameplay asset progresses through the same three passes.

### Pass 1 — SHITTY BLOCKS

No polished character artwork.

- Polly = simple colored block/capsule.
- Glam enemy = pink block.
- Prog enemy = green block.
- Punk enemy = red block.
- Background = boxes and collision boundaries.
- Effects = circles/flashes/placeholders.

Test only:

- movement speed;
- lane depth;
- enemy navigation;
- attack range;
- hitboxes and hurtboxes;
- combo timing;
- knockback;
- hitstop;
- enemy spacing;
- wave composition;
- camera movement.

**Nothing becomes prettier until the block version is fun.**

### Pass 2 — BASIC-ASS SPRITES

Replace blocks with recognizable but deliberately unfinished assets.

Add:

- rough Polly sprites;
- rough enemy sprites;
- rough alley art;
- placeholder weapon art;
- prototype hit sparks;
- simple shadows;
- crude UI;
- temporary sound effects.

Goal: prove that the visual concept survives contact with real movement, timing, and collisions.

### Pass 3 — FULL POLISH

Only after Passes 1 and 2 work:

- polished character animation;
- hair secondary motion;
- flannel movement;
- enemy personality frames;
- rain, lighting, puddle reflections;
- parallax;
- hand-authored impact FX;
- final UI;
- final SFX;
- music;
- voice barks;
- ambience;
- breakables;
- screen shake and camera punches;
- restrained distortion/chromatic effects where useful.

---

## 3. Master sprite standard

### Native character scale

Polly should stand at approximately **112 px tall** in native sprite resolution.

Working range: **104–120 px**.

This preserves readable hair, flannel, chains, ripped jeans, boots, hands, and expressions without making animation prohibitively expensive.

### Rendering

- Pixel-sharp presentation.
- Avoid soft filtering and accidental resampling blur.
- Preserve coherent pixel density between characters, props, FX, and environment.

---

## 4. Camera and perspective

Use a classic belt-scroller / side-on beat-em-up presentation.

- X axis = left/right travel.
- Y axis = shallow battlefield depth.
- Characters stay primarily side-facing / three-quarter-side.
- No true Z gameplay is required for the first slice.
- Combat floor occupies roughly the lower 35–45% of the screen.

Characters may move vertically within the lane without rotating sprites toward camera. The classic arcade visual cheat is intentional.

---

## 5. Character grounding and anchors

Every character uses a consistent ground origin between the feet.

The foot anchor governs:

- movement;
- depth sorting;
- shadows;
- collisions;
- pickup placement;
- knockback;
- environmental occlusion.

Never position gameplay logic from sprite center. Hair, knockdown poses, and oversized weapons must not change world anchoring.

---

## 6. Polly visual identity

Polly's first-slice identity is frozen around these silhouette anchors:

- long flowing auburn/red hair;
- red-and-black open flannel;
- dark sleeveless grunge shirt with generic faded rock/smiley-style motif;
- layered necklaces/choker;
- torn black/charcoal jeans;
- hanging chain;
- substantial black combat boots.

Avoid copyrighted band logos or exact protected marks in production assets.

A black silhouette of Polly should remain recognizable through hair, flannel, stance, and boots alone.

### Personality baseline

Polly combines four tonal states:

1. quiet/deadpan sweetheart;
2. sarcastic, foul-mouthed gremlin when amused;
3. cool detached rocker;
4. sudden explosive combat rage.

Resting animation should not make her permanently angry. Contrast is part of her charm.

---

## 7. Polly animation manifest

| Animation | Prototype frames | Final target |
|---|---:|---:|
| Idle | 2 | 6 |
| Walk | 4 | 8 |
| Sprint | 4 | 6 |
| Light attack 1 | 3 | 5 |
| Light attack 2 | 3 | 5 |
| Light attack 3 | 4 | 6 |
| Heavy guitar swing | 4 | 8 |
| Hurt high | 1 | 3 |
| Hurt low | 1 | 3 |
| Knockback | 2 | 4 |
| Knockdown | 3 | 6 |
| Grounded | 1 | 2 |
| Get-up | 3 | 6 |
| Pickup | 2 | 4 |
| Carry idle | 1 | 3 |
| Weapon swing | 3 | 5 |
| Throw | 3 | 5 |
| Victory/end pose | 2 | 6 |

Prototype frames exist to test timing, not to imitate final frame density.

---

## 8. Polly combo visual grammar

### Light 1

Fast straight punch, minimal commitment.

### Light 2

Backhand, hook, or elbow-like continuation with more torso rotation.

### Light 3

Large finisher silhouette: heavy hook, boot, shove, or similar strong terminator. The silhouette must clearly communicate combo completion without UI text.

---

## 9. Heavy guitar attack

This is Polly's signature attack.

Approximate final sequence:

1. grip / anticipation;
2. shoulders rotate;
3. guitar travels backward;
4. hips drive forward;
5. giant swing;
6. contact pose;
7. follow-through;
8. recovery.

The swing arc is a **separate FX asset**, never baked permanently into Polly's body sprites.

That allows independent control over timing, color, scale, variants, and hit intensity.

---

## 10. Secondary motion

Final Polly animation includes authored secondary motion for:

- hair;
- flannel tails;
- waist chain;
- necklaces.

Do not require physical simulation. Deliberate frame-lag and overshoot are preferred.

---

## 11. Shared enemy state taxonomy

All three first-slice enemies share the same broad combat-state vocabulary:

```text
IDLE
APPROACH
POSITION
ANTICIPATE
ATTACK
RECOVER
HURT
KNOCKBACK
DOWN
GETUP
KO
```

Their identity should emerge from animation timing, range, aggression, movement, and special behavior rather than from three completely different codebases.

---

## 12. Enemy archetype 1 — Glam Hair-Metal Femboy

**Working dev codename:** `GLAMBO`

### Visual identity

- towering teased hair;
- makeup / eyeliner;
- leather, animal-print, neon, satin, or stagewear motifs;
- jewelry/chains;
- theatrical poses;
- visually elegant, cocky silhouette.

### Combat identity

**Stress created:** baited timing and deceptive flourish.

- long windups;
- flashy telegraphs;
- short evasive lean-back/dodge;
- punishes impatient mashing;
- taunt/pose behavior matters mechanically.

### Animation budget

| Animation | Prototype | Final |
|---|---:|---:|
| Idle/pose | 2 | 6 |
| Walk/swagger | 4 | 6 |
| Attack | 3 | 6 |
| Dodge | 2 | 4 |
| Hurt | 1 | 3 |
| Knockback | 2 | 4 |
| Down | 2 | 4 |
| Get-up | 2 | 4 |
| KO | 3 | 6 |
| Taunt | 2 | 5 |

---

## 13. Enemy archetype 2 — Prog Nerd

**Working dev codename:** `ODDMETER`

### Visual identity

- glasses;
- academic / awkwardly stylish clothing;
- controlled hair;
- niche-musician energy;
- portable keyboard, synth, or keytar-style accessory if readable.

### Combat identity

**Stress created:** timing disruption and awkward spacing.

- delayed attacks;
- intentionally strange hold timing;
- keeps uncomfortable distance;
- optional short-range waveform/keytar special;
- readable enough to be fair despite unusual rhythm.

### Animation budget

| Animation | Prototype | Final |
|---|---:|---:|
| Idle | 2 | 5 |
| Walk | 4 | 6 |
| Delayed strike | 4 | 7 |
| Keytar/special | 3 | 6 |
| Hurt | 1 | 3 |
| Knockback | 2 | 4 |
| Down | 2 | 4 |
| Get-up | 2 | 4 |
| KO | 3 | 5 |

---

## 14. Enemy archetype 3 — Mohawk Punker

**Working dev codename:** `RAMJET`

### Visual identity

- tall mohawk;
- sleeveless patched jacket;
- chains;
- torn trousers;
- boots;
- forward-leaning silhouette.

### Combat identity

**Stress created:** pressure.

- fast approach;
- rush/shoulder attack;
- short flurry;
- low patience;
- interrupts calm spacing;
- lower complexity, higher velocity.

### Animation budget

| Animation | Prototype | Final |
|---|---:|---:|
| Idle | 2 | 4 |
| Walk | 4 | 6 |
| Sprint/rush | 3 | 5 |
| Shoulder strike | 3 | 5 |
| Punch flurry | 3 | 6 |
| Hurt | 1 | 3 |
| Knockback | 2 | 4 |
| Down | 2 | 4 |
| Get-up | 2 | 4 |
| KO | 3 | 5 |

---

## 15. Ground shadows

Every standing character gets a reusable soft pixel-art ground shadow.

The shadow remains anchored to the floor and can scale subtly during knockback/jump states if needed.

The primary purpose is lane/depth readability.

---

## 16. Pickup asset set

Only two pickups need to be functional in the first production slice.

### Functional V1

**Beer bottle**

- ground sprite;
- pickup/carry presentation;
- swing/use state;
- broken state;
- debris FX.

**Mic stand**

- ground sprite;
- carried state;
- attack state.

### Decorative until pickup architecture is proven

- trash-can lid;
- broken guitar.

---

## 17. Rat Hole Alley environment kit

Build the alley from reusable modules rather than one enormous flattened painting.

### Background layer

- brick wall sections;
- club facade;
- distant skyline;
- fire escapes;
- upper windows.

### Midground

- club door;
- neon sign;
- posters;
- pipes/drainpipes;
- chain-link fence;
- dumpster.

### Gameplay plane

- asphalt tiles;
- puddles;
- pavement edge;
- alley markings;
- debris decals.

### Foreground

- rubbish bags;
- cable coils;
- crates;
- bollard/pole;
- partial fence fragments.

### Interactive

- bottle spawn;
- mic stand;
- one destructible crate or amp stack;
- dumpster collision.

---

## 18. Parallax

Initial slice uses only:

- far layer: skyline/distant structures;
- middle layer: buildings/alley;
- near layer: gameplay props;
- optional foreground layer.

Rain can live as a separate screen-space overlay.

Avoid unnecessary parallax-layer proliferation.

---

## 19. Environmental animation

Polished slice may include small atmospheric loops:

- neon flicker;
- rain;
- steam plume;
- puddle ripple;
- club-door light pulse;
- silhouette movement inside the venue;
- occasional poster-edge flutter.

These are atmosphere multipliers, not gameplay systems.

---

## 20. FX visual bible

The effects language should feel like **screen-printed gig-poster violence**, not magical fantasy combat.

### Required slice FX

- light hit: cream/white jagged burst;
- heavy hit: larger cream burst with red accent and particles;
- guitar arc: dirty white dry-brush crescent;
- KO: black/red ink explosion behind silhouette;
- ground slam: dust ring and grit;
- bottle break: glass fragments and pale sparkle;
- punk rush: small shoe-dust/debris trail;
- prog special: restrained angular waveform motif.

---

## 21. Hit-effect timing

FX serves timing rather than decoration.

Example heavy impact:

```text
frame N     swing
frame N+1   CONTACT
            hitstop
            hit spark
            sound transient
frame N+2   knockback begins
            debris
frame N+3   camera settles
```

---

## 22. KO standard

First-slice enemies are arcade KOs, not realistic deaths.

Sequence:

1. final hit;
2. exaggerated knockback;
3. ink/silhouette impact burst;
4. ground hit;
5. short defeated hold;
6. despawn, retreat, or later crawl/flee behavior.

No gore system is required for the first slice.

---

## 23. Basic UI asset set

Minimal first-slice UI only:

- Polly portrait;
- health bar;
- optional placeholder special/guitar meter;
- enemy health/name strip for tougher enemies;
- pickup indicator;
- pause icon.

No inventory, minimap, skill tree, or progression UI yet.

---

## 24. Audio asset bible

Audio enters as placeholders in Pass 2 and becomes production material in Pass 3.

### Polly

- punch swish;
- heavy guitar swish;
- boot movement;
- hurt vocal;
- effort sounds;
- small pool of combat barks.

### Enemies

Each archetype eventually needs:

- attack vocal;
- hurt variants;
- KO vocal;
- taunt.

### Impact families

- light body hit;
- heavy body hit;
- boot impact;
- guitar-body impact;
- metal impact;
- bottle break;
- enemy-ground impact.

Avoid one repeated impact sample for every contact.

---

## 25. Music plan

The slice needs one original grunge-rock track built in reactive layers.

### Base layer

Dirty bass, drums, restrained guitar texture.

### Combat layer

Additional distorted guitar/cymbals/more aggressive rhythm.

### Wave-clear drop

Brief reduction after encounters.

The music should respond to combat without requiring an elaborate adaptive-score system.

---

## 26. Voice philosophy

Polly should not chatter constantly.

Voice moments should be sparse and contextual:

- occasional encounter-start bark;
- response to particularly ridiculous enemy taunt;
- occasional big-KO remark;
- occasional pickup line;
- level-end line.

Silence is part of Polly's deadpan personality.

---

## 27. Suggested asset directory

```text
assets/
  characters/
    polly/
      idle/
      walk/
      sprint/
      combat/
      hurt/
      weapons/

    enemies/
      glam/
      prog/
      punk/

  environments/
    rat_hole/
      bg/
      mid/
      ground/
      fg/
      props/
      interactables/

  fx/
    hits/
    movement/
    weapons/
    ko/

  ui/

  audio/
    music/
    ambience/
    impacts/
    characters/
    environment/
```

---

## 28. First-slice asset budget

### Pass 1

**Zero polished sprites.**

### Pass 2 target

- Polly: roughly 40–50 rough frames;
- Glam: roughly 18–25 rough frames;
- Prog: roughly 18–25 rough frames;
- Punk: roughly 18–25 rough frames;
- environment: roughly 15–25 modular pieces;
- FX: 5–8;
- functional pickup weapons: 2;
- minimal UI.

### Pass 3 target

Approximately **120–170 polished character frames total**, depending on final holds, timing, and animation economy.

---

## 29. Anti-bloat rule

Every new asset must answer at least one of these questions:

1. Does it improve gameplay readability?
2. Does it strengthen musical/subculture identity?
3. Does it make impact feel better?
4. Does it strengthen place/atmosphere?

If the answer to all four is **no**, do not make it yet.

---

## 30. Locked first-slice decisions

- approximately 112 px native character scale;
- classic belt-scroller camera;
- fixed foot-anchor convention;
- shared enemy-state taxonomy;
- constrained frame budgets;
- modular alley construction;
- separate FX sprites;
- three-pass blocks → rough sprites → polished production workflow;
- two functional pickup weapons in first slice;
- KO rather than gore for V1;
- one reactive original grunge track;
- sparse Polly dialogue;
- first enemies: Glam Hair-Metal Femboy, Prog Nerd, Mohawk Punker;
- first location: The Rat Hole Alley.

---

## 31. Canonicality

This document is the canonical asset and visual-production bible for the first Polly Grunge Rocker vertical slice until replaced by an explicitly approved later version.
