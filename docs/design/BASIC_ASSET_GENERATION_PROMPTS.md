# Polly Grunge Rocker — Basic Asset Generation Prompts

**Status:** CANONICAL WORKING PROMPT PACK  
**Scope:** Pass 2 — BASIC-ASS SPRITES  
**Depends on:** `POLLY_VERTICAL_SLICE_ASSET_BIBLE.md`

This document exists to produce consistent rough production assets quickly while the greybox combat slice is being designed and implemented.

The goal is **not** finished promotional art. The goal is readable, game-usable source material that can be cleaned, cut, aligned, and animated.

---

# 1. Generation strategy

Do **not** ask an image model to invent an entire polished sprite library in one image and assume the frames will be production-consistent.

Preferred workflow:

1. Generate one canonical master character pose.
2. Approve identity, silhouette, palette, and scale.
3. Use that same approved master as the visual reference for every later generation.
4. Generate one animation family at a time.
5. Prefer 4–8 frames per sheet.
6. Keep camera, scale, ground line, lighting, clothing, and facing direction fixed.
7. Cut individual frames after generation.
8. Reject any sheet where anatomy, clothing, hair length, proportions, or pixel density visibly drift.
9. Use nearest-neighbour scaling only after cleanup.

For rough Pass 2 assets, consistency beats detail.

---

# 2. Global master style block

Prepend this block to every character, prop, environment, and FX prompt unless a section explicitly overrides it.

```text
Create original 2D pixel-art production artwork for a gritty 1990s grunge-rock side-scrolling arcade beat-'em-up. Use a classic belt-scroller presentation with readable silhouettes, chunky deliberate pixels, strong contrast, restrained detail, and a hand-authored sprite-game feel rather than smooth painted illustration.

Native character scale target: approximately 112 pixels tall for the main playable character. Maintain one coherent pixel density across all characters and props. Use crisp hard pixel edges, no anti-aliased blur, no painterly smearing, no 3D rendering, no photorealism.

Camera: side-facing three-quarter beat-'em-up view, feet planted on one consistent horizontal ground line, body readable at gameplay size. Characters primarily face right unless otherwise requested. Preserve enough perspective to support shallow up/down movement on a belt-scroller combat lane, but do not use isometric perspective.

Art direction: rainy underground music-district grit, dirty black, charcoal, desaturated denim, oxidized metal, faded paper, nicotine beige, muted reds, occasional neon accents. Visual language should feel like screen-printed gig posters, photocopied flyers, worn record sleeves, wet asphalt, and cheap club lighting.

All designs must be original. Do not reproduce copyrighted band logos, exact album art, artist likenesses, or protected marks. Invent generic band-style graphics and fictional poster text where needed.

For character sheets: transparent background, no scenery, no cast shadows baked into the sprite unless explicitly requested. Keep every frame fully inside the canvas with generous spacing between frames. Do not crop hair, boots, hands, weapons, or motion arcs. Keep proportions, clothes, palette, face, hair length, and pixel density identical across frames.
```

---

# 3. Global negative / rejection block

Append this to character generation prompts.

```text
Avoid: realistic painting, 3D CGI, anime proportions, chibi proportions, excessive outlines, smooth vector art, soft gradients, motion blur, lens effects, photographic textures, inconsistent body size between frames, changing hairstyle, changing clothing, changing accessories, mirrored text, extra fingers, missing limbs, cropped feet, cropped hair, inconsistent guitar size, floating feet, duplicate frames, camera-angle drift, isometric perspective, front-facing fighting-game stance, over-detailed faces that cannot survive pixel scale.
```

---

# 4. Polly canonical master-pose prompt

Generate this first. It becomes Polly's identity reference.

```text
[GLOBAL MASTER STYLE BLOCK]

Design the canonical gameplay sprite for POLLY, the playable protagonist.

Polly is a young adult grunge-rock woman with long flowing auburn/red hair, expressive but understated features, and a relaxed deadpan confidence. She wears an open red-and-black flannel overshirt, a dark sleeveless grunge-style shirt with an original faded smiley/rock graphic, layered necklaces and a black choker, ripped black/charcoal jeans, a hanging wallet chain, wristbands, and substantial black lace-up combat boots.

Her resting personality should read as quiet, cool, slightly amused, and unimpressed rather than permanently angry. She is attractive without glamor posing, practical without looking militarized, and unmistakably a 1990s underground rocker.

Create ONE clean full-body gameplay sprite in a relaxed side-facing three-quarter stance, facing right. Feet flat on a single ground line. Arms loose. Hair silhouette large and recognizable. Flannel tails readable. Chain visible. Boots visually weighty.

Native sprite target: about 112 px character height. Transparent background. No text. No environment. No weapon. No special effects.

This is a model-sheet master, not an action pose.

[GLOBAL NEGATIVE / REJECTION BLOCK]
```

Acceptance criteria:

- silhouette reads immediately;
- boots and hair survive thumbnail scale;
- flannel remains visible against dark shirt;
- no copyrighted band logo;
- foot anchor is obvious;
- all later Polly prompts use this image as reference.

---

# 5. Polly idle prompt

```text
Use the approved canonical Polly master sprite as the strict character reference.

[GLOBAL MASTER STYLE BLOCK]

Create a rough production sprite strip for POLLY IDLE, facing right.

Exactly 6 clearly separated keyframes on one transparent canvas, ordered left to right. Keep identical scale, ground line, proportions, outfit, face, hair length, palette, and pixel density in every frame.

Animation action:
1. neutral relaxed stance;
2. subtle breathing shift;
3. slight weight transfer onto rear leg;
4. tiny hair/flannel settle;
5. faint half-smile or eyebrow attitude without changing face identity;
6. return toward neutral.

Movement should be restrained. Polly is not bouncing like a fighting-game character. Her personality is deadpan and cool.

No weapon. No scenery. No labels. No frame borders. Transparent background.

[GLOBAL NEGATIVE / REJECTION BLOCK]
```

---

# 6. Polly walk prompt

```text
Use the approved canonical Polly master sprite as the strict character reference.

[GLOBAL MASTER STYLE BLOCK]

Create an 8-frame rough production WALK CYCLE for Polly, facing right, laid out left to right on a transparent canvas.

Classic grounded beat-'em-up walking motion, not a fashion runway walk. Maintain one identical foot-anchor ground line across frames. Natural arm swing, slight flannel and hair lag, substantial boot contact, modest hip movement, readable stride at gameplay scale.

Frames should cover one complete seamless walk cycle: contact, down, passing, up, opposite contact, opposite down, opposite passing, opposite up.

Do not change camera angle or body scale. No scenery, text, or FX.

[GLOBAL NEGATIVE / REJECTION BLOCK]
```

---

# 7. Polly sprint prompt

```text
Use the approved canonical Polly master sprite as the strict character reference.

[GLOBAL MASTER STYLE BLOCK]

Create a 6-frame rough production SPRINT CYCLE for Polly, facing right, transparent background.

She runs with committed forward lean, heavy boot drive, arms pumping, flannel trailing, chain lagging, and long red hair streaming backward. Preserve the same character scale and side-three-quarter camera as the canonical master.

The run should feel fast and slightly reckless but athletic enough for a beat-'em-up. Keep the feet readable and grounded. Do not turn this into a side-view platformer sprint silhouette.

No dust FX baked into the body sheet. No scenery. No labels.

[GLOBAL NEGATIVE / REJECTION BLOCK]
```

---

# 8. Polly light combo prompt

For Pass 2, generate the three attacks as separate sheets. Do not ask for the whole combo in one giant sheet.

## Light 1 — straight punch

```text
Use the approved canonical Polly master sprite as the strict character reference.

[GLOBAL MASTER STYLE BLOCK]

Create a 5-frame rough production LIGHT ATTACK 1 animation for Polly, facing right.

Attack: fast straight punch.

Frame intent:
1. neutral combat-ready stance;
2. small shoulder/hip anticipation;
3. fist drives forward with clean readable extension;
4. brief contact pose with committed weight transfer;
5. fast recovery toward neutral.

Keep the attack compact and fast. No hit spark or impact effect baked into the sprite. No enemy. Transparent background.

[GLOBAL NEGATIVE / REJECTION BLOCK]
```

## Light 2 — hook/backhand

```text
Use the approved canonical Polly master sprite as the strict character reference.

[GLOBAL MASTER STYLE BLOCK]

Create a 5-frame rough production LIGHT ATTACK 2 animation for Polly, facing right.

Attack: a compact hook or backhand continuation with visibly stronger torso rotation than Light 1.

Frame intent:
1. chained-ready pose from previous strike;
2. rotational anticipation;
3. arm begins sweeping arc;
4. contact pose with shoulder and hips turned;
5. recovery that naturally permits chaining into a finisher.

No FX, enemy, scenery, labels, or baked motion blur. Transparent background.

[GLOBAL NEGATIVE / REJECTION BLOCK]
```

## Light 3 — finisher

```text
Use the approved canonical Polly master sprite as the strict character reference.

[GLOBAL MASTER STYLE BLOCK]

Create a 6-frame rough production LIGHT ATTACK 3 FINISHER for Polly, facing right.

The finisher must have a much larger, unmistakable silhouette than Light 1 and Light 2. Use a powerful rock-and-roll street-fight strike such as a savage overhand hook, boot, or committed shove-strike. Prioritize a readable anticipation, explosive contact pose, and satisfying follow-through.

Do not make it magical. No FX baked into the body. No enemy. Transparent background.

[GLOBAL NEGATIVE / REJECTION BLOCK]
```

---

# 9. Polly heavy guitar-swing prompt

```text
Use the approved canonical Polly master sprite as the strict character reference. Use one approved black electric-guitar master design as the strict weapon reference.

[GLOBAL MASTER STYLE BLOCK]

Create an 8-frame rough production HEAVY GUITAR SWING animation for Polly, facing right.

The guitar is used as an exaggerated heavy melee weapon. Preserve its dimensions, stickers/markings, strap state, and orientation logic consistently across frames.

Frame progression:
1. grip and plant feet;
2. shoulders and hips load backward;
3. guitar pulled into backswing;
4. body begins explosive rotation;
5. wide horizontal strike enters the hit zone;
6. strongest contact pose with full-body commitment;
7. long follow-through, hair and flannel overshooting;
8. heavy recovery.

Important: DO NOT include the white slash arc, hit spark, debris, enemy, or contact FX in this sheet. Those are separate assets.

Transparent background. Keep feet on a stable ground line. The move should feel slightly excessive and physically satisfying.

[GLOBAL NEGATIVE / REJECTION BLOCK]
```

---

# 10. Shared enemy-master prompt prefix

Use this before each enemy-specific master-pose description.

```text
Create one original enemy gameplay sprite for the same 2D pixel-art belt-scroller as Polly. Match Polly's native pixel density and camera exactly. Enemy should be approximately similar human scale, with intentional height variation of no more than about 10–15% unless otherwise specified.

Transparent background. Full body. Facing left so the enemy naturally confronts right-facing Polly. Feet on the same type of ground line. Strong silhouette readable at gameplay size. No scenery. No effects. No text. No copyrighted logos.
```

---

# 11. Glam hair-metal femboy master prompt

```text
[GLOBAL MASTER STYLE BLOCK]
[SHARED ENEMY-MASTER PREFIX]

Design the canonical GLAM HAIR-METAL FEMBOY enemy.

Young adult man with an intentionally androgynous, pretty, theatrical glam-metal presentation. Huge teased blonde or platinum hair with optional restrained pink/purple streaks, eyeliner and stage makeup, slim athletic build, crop-top or open stage vest, tight patterned trousers, belts/chains, bracelets, boots, and flashy accessories.

The design should be affectionate satire rather than hateful caricature. He is stylish, cocky, performative, and visually elegant. His silhouette should communicate that he fights like he is permanently halfway through a music-video pose.

Pose: relaxed theatrical combat idle, weight on one hip, one hand poised dramatically, slight smug expression, facing left.

Palette family: platinum/blonde, magenta/purple accents, black leather, small metallic highlights.

One character only. Transparent background.

[GLOBAL NEGATIVE / REJECTION BLOCK]
```

---

# 12. Glam rough animation prompts

## Swagger walk

```text
Use the approved Glam enemy master sprite as strict reference.

Create a 6-frame rough production swagger-walk cycle facing left. Keep body scale, hair mass, outfit, makeup, palette, and ground line identical. Walk should be combat-functional but theatrically cocky, with slightly exaggerated shoulders and hair bounce.

Transparent background, no FX, no labels.
```

## Telegraph attack

```text
Use the approved Glam enemy master sprite as strict reference.

Create a 6-frame rough production melee attack facing left. The attack must have a conspicuously theatrical windup: pose, flourish, committed strike, contact pose, overextended recovery. Make the telegraph readable enough that the player can interrupt it.

No FX or opponent. Transparent background.
```

## Lean-back dodge

```text
Use the approved Glam enemy master sprite as strict reference.

Create a 4-frame lean-back evade animation facing left. Feet mostly remain planted while torso and hair sweep dramatically backward, then recover. The move should read as smug evasiveness rather than acrobatics.

Transparent background.
```

---

# 13. Prog Nerd master prompt

```text
[GLOBAL MASTER STYLE BLOCK]
[SHARED ENEMY-MASTER PREFIX]

Design the canonical PROG NERD enemy.

Young adult man with glasses, slightly awkward but carefully chosen clothes, restrained academic/musician styling, brown or dark hair, slim build, practical shoes, muted green/olive/brown palette, and a compact portable keytar/synth-inspired instrument or controller that can function as a quirky combat prop.

He should look physically less threatening than the punk or glam enemy but mentally certain that he is operating on a superior time signature.

Pose: slightly guarded, analytical posture, facing left, one hand positioned around his instrument/controller, expression focused and mildly judgmental.

No parody of a specific real musician. No logos. Transparent background.

[GLOBAL NEGATIVE / REJECTION BLOCK]
```

---

# 14. Prog rough animation prompts

## Walk

```text
Use the approved Prog Nerd master sprite as strict reference.

Create a 6-frame rough production walk cycle facing left. Movement is cautious and measured, almost counting steps. Preserve instrument size and position coherently.

Transparent background.
```

## Delayed strike

```text
Use the approved Prog Nerd master sprite as strict reference.

Create a 7-frame rough production delayed melee strike facing left.

Critical timing language: anticipation begins normally, then include a clearly readable held pose before the actual strike. The delay must look intentional, not like a missing frame. Follow with a precise sudden attack and restrained recovery.

No FX or opponent. Transparent background.
```

## Keytar / waveform special

```text
Use the approved Prog Nerd master sprite as strict reference.

Create a 6-frame rough production keytar/synth special animation facing left. He braces the instrument, performs a precise absurdly serious input, then releases a short ranged effect.

Do not draw the projectile/waveform into the character sheet. End with a clear release pose so a separate FX sprite can spawn from a consistent point.

Transparent background.
```

---

# 15. Mohawk Punker master prompt

```text
[GLOBAL MASTER STYLE BLOCK]
[SHARED ENEMY-MASTER PREFIX]

Design the canonical MOHAWK PUNKER enemy.

Young adult punk with a tall red mohawk, sleeveless black patched vest, torn dark trousers, chains, heavy boots, wrist wraps/studs, and a lean aggressive build. Use original generic patches and symbols only.

His entire silhouette should point forward toward Polly. Shoulders pitched in, hands ready, knees bent, zero patience. He should look like he will sprint before the player has finished thinking.

Palette family: black, charcoal, desaturated denim, hard red mohawk accent, small pale metal highlights.

Pose: aggressive forward-leaning idle facing left.

Transparent background.

[GLOBAL NEGATIVE / REJECTION BLOCK]
```

---

# 16. Punk rough animation prompts

## Walk

```text
Use the approved Mohawk Punker master sprite as strict reference.

Create a 6-frame rough production aggressive walk cycle facing left. Short impatient steps, shoulders forward, fists ready. No swagger, no flourish.

Transparent background.
```

## Rush

```text
Use the approved Mohawk Punker master sprite as strict reference.

Create a 5-frame rough production rush/sprint cycle facing left. Strong forward lean, explosive boot drive, mohawk staying readable, jacket and chain trailing. It should feel like a human shopping cart thrown downhill.

No dust FX baked into the body sheet. Transparent background.
```

## Shoulder charge

```text
Use the approved Mohawk Punker master sprite as strict reference.

Create a 5-frame rough production shoulder-charge attack facing left: tiny load, explosive drive, shoulder-first contact pose, overrun, recovery. Keep attack silhouette extremely simple and readable.

No impact FX or opponent. Transparent background.
```

---

# 17. Shared hurt / knockdown prompt template

Use once per character reference.

```text
Use the approved [CHARACTER] master sprite as strict reference.

Create a rough production reaction sheet on transparent background containing separate readable poses for:

1. high hit recoil;
2. low/body hit recoil;
3. backward knockback;
4. falling toward ground;
5. grounded/down pose;
6. beginning recovery/get-up.

Preserve outfit, anatomy, scale, camera, and palette exactly. Exaggerate silhouettes enough to read at gameplay size. Do not include the attacker, blood, gore, impact FX, dust, or scenery. Maintain one consistent ground line wherever the body touches the floor.
```

---

# 18. KO silhouette / ink-burst FX prompt

```text
[GLOBAL MASTER STYLE BLOCK]

Create a transparent-background pixel-art FX sprite sheet for an arcade beat-'em-up KO impact.

Visual language: screen-printed gig-poster violence, black and dark-red ink explosion, cream/white impact accents, gritty halftone-like pixel clusters, no gore and no realistic blood.

Create 6 separate frames left to right:
1. tiny pre-impact flecks;
2. sharp impact star;
3. expanding black/red ink burst;
4. largest irregular burst with debris pixels;
5. collapsing fragments;
6. fading specks.

No character artwork. No text. No background. Hard pixel edges. Frames must not overlap.
```

---

# 19. Light hit-spark prompt

```text
Create a transparent pixel-art FX sheet for a gritty arcade beat-'em-up LIGHT HIT SPARK.

6 small frames, left to right. Dirty cream/white jagged impact star with tiny black grit pixels. Very fast expansion and disappearance. Screen-printed gig-poster feel. No glow, no magical energy, no background, no text, no character.
```

---

# 20. Heavy hit-spark prompt

```text
Create a transparent pixel-art FX sheet for a HEAVY MELEE HIT in a grunge-rock arcade beat-'em-up.

6 frames. Larger than the light hit spark. Cream-white jagged core, restrained dark-red accent, black debris/grit, slightly asymmetric explosion. Hard-edged screen-print aesthetic rather than anime energy burst. No blood, no gore, no characters, no background.
```

---

# 21. Guitar swing arc prompt

```text
Create a transparent pixel-art FX sprite strip for a wide horizontal guitar swing.

6 frames showing a dirty off-white dry-brush crescent appearing, widening, fragmenting, and disappearing. The arc should feel like scraped paint or photocopied brush texture translated into pixel art, not magical energy.

Wide enough to accompany a heavy melee guitar swing by a roughly 112 px-tall character. No weapon, no person, no background, no text.
```

---

# 22. Punk rush dust prompt

```text
Create a transparent pixel-art 5-frame foot-level debris FX strip for a fast rushing enemy in a wet gritty alley.

Small brown-grey grit, dark pavement flecks, tiny pale dust/splash pixels. Low and horizontal. Restrained enough not to obscure feet. No character, no background.
```

---

# 23. Prog waveform projectile prompt

```text
Create a transparent pixel-art short-range projectile/attack FX for the Prog Nerd enemy.

Design language: angular audio waveform / oscilloscope motif, pale cream with muted sickly-green accent, deliberately mathematical and tidy, slightly absurd but not magical. 6-frame animation from compact waveform pulse to short forward propagation to breakup.

Keep it visually distinct from Polly's impact FX. No text, no instrument, no character, no background.
```

---

# 24. Beer-bottle pickup prompt

```text
[GLOBAL MASTER STYLE BLOCK]

Create a small game-ready pixel-art BEER BOTTLE pickup prop for the same grunge beat-'em-up.

Original generic green/brown glass bottle with worn unlabeled or fictional-label appearance. Readable at game scale. Provide four separated sprites on transparent background:

1. intact bottle lying on ground;
2. intact bottle held upright side-view;
3. cracked bottle;
4. broken bottle with jagged remaining neck.

No real brand. No text required. Match the game's pixel density.
```

---

# 25. Mic-stand pickup prompt

```text
[GLOBAL MASTER STYLE BLOCK]

Create a game-ready pixel-art microphone stand melee pickup for the same grunge beat-'em-up.

Provide three separated transparent sprites:
1. full mic stand lying/leaning on ground;
2. side-view carried orientation;
3. horizontal striking orientation.

Black worn metal with small silver highlights, battered club equipment, readable silhouette, consistent scale beside a 112 px-tall character. No character, no background.
```

---

# 26. Rat Hole Alley master environment prompt

Generate the environment as a layered reference first, then derive modular pieces.

```text
Create a wide original 2D pixel-art side-scrolling beat-'em-up environment concept for THE RAT HOLE ALLEY, a fictional rainy 1990s underground music district at night.

Camera and perspective must match a classic belt-scroller: side-facing street with a shallow playable depth lane across the lower portion of the scene, not isometric, not a platformer side-view, not a cinematic perspective shot.

Scene ingredients:
- old brick club facade;
- narrow warm-red club doorway;
- fictional neon club sign reading THE RAT HOLE;
- wet black asphalt and puddles;
- dirty curb and pavement edge;
- layered fictional gig posters;
- pipes and drainpipes;
- chain-link fence;
- battered dumpster;
- rubbish bags;
- cable coils;
- wooden crates;
- one battered amp stack;
- distant rainy city silhouettes;
- occasional red neon and dirty amber lamps;
- urban grime and photocopied-flyer texture.

Mood: hostile but inviting underground nightlife, rain, cigarette-smoke atmosphere, cheap amps, sweat, neon reflected in puddles.

Keep the gameplay lane visually readable and less cluttered than the walls. Leave clear horizontal space for four or five combatants.

No real band names, album covers, brands, or copied venues. All posters and symbols original or generic.

No characters. No UI. No combat FX.
```

---

# 27. Rat Hole modular-background prompt

```text
Using the approved Rat Hole Alley environment as strict visual reference, create a modular pixel-art environment asset sheet on transparent background.

Separate pieces with generous spacing. Include:
- 3 brick-wall modules;
- 1 club-door facade module;
- 2 drainpipe modules;
- 2 chain-link fence sections;
- 1 dumpster;
- 2 rubbish-bag piles;
- 2 wooden-crate stacks;
- 1 battered amp stack;
- 1 cable coil;
- 1 traffic/bollard-style street prop;
- 4 original torn gig-poster clusters;
- 3 puddle/debris decals.

Match the approved environment's pixel density, lighting direction, palette, and perspective exactly. No characters. No UI. Transparent background wherever technically appropriate.
```

---

# 28. Ground / alley tile prompt

```text
Create a seamless-able pixel-art ground asset sheet for the Rat Hole Alley combat lane.

Include:
- dark wet asphalt base tiles;
- cracked asphalt variants;
- puddle-edge variants;
- curb/pavement boundary pieces;
- drain/grate;
- small litter/debris decals.

Use black-charcoal-blue wet pavement, subtle dirty reflections, restrained texture, and sufficient empty visual space for combat readability. Classic belt-scroller perspective. No characters, no text, no UI.
```

---

# 29. Neon-sign prompt

```text
Create an original pixel-art neon club sign reading THE RAT HOLE for a gritty 1990s underground music venue.

Worn red/orange neon tubes, imperfect illumination, slightly rusted black backing, handmade dive-bar character. Provide three transparent-background frames: fully lit, partially flickering, dim/off-flicker.

No copied venue logo. No additional text.
```

---

# 30. Poster-cluster prompt

```text
Create a transparent pixel-art sheet of 8 fictional underground gig posters for a dirty 1990s music-district wall.

Screen-printed and photocopied aesthetic, torn edges, faded black/red/cream/green ink. Use invented band names and abstract original symbols only. Mix punk, glam, prog, metal, noise-rock, and grunge visual cues without reproducing real album art or logos.

Keep typography blocky enough to survive pixel-art reduction. Posters should be usable individually or layered into clusters.
```

---

# 31. Basic Pass-2 UI prompt

```text
Create a minimal pixel-art HUD concept for a gritty grunge-rock beat-'em-up.

Elements only:
- small Polly portrait frame;
- horizontal health bar;
- optional empty secondary guitar/special meter;
- compact enemy name/health strip;
- small pickup/interact icon;
- simple pause icon.

Visual language: torn gig-poster paper, black tape, dirty cream, dark red accents, photocopied club-flyer texture. Keep gameplay readability higher than decoration. No copyrighted logos. Transparent or dark neutral presentation sheet.
```

---

# 32. Asset-generation acceptance checklist

Reject and regenerate an asset if any of the following occur:

- wrong camera angle;
- inconsistent character scale;
- feet do not share the same ground anchor;
- clothing changes between frames;
- hair length/style changes between frames;
- accessories teleport or disappear;
- hands/weapons crop out of frame;
- sprite pixel density differs from Polly;
- anatomy visibly mutates;
- important silhouette detail disappears at thumbnail size;
- weapon size changes frame to frame;
- hit FX are accidentally baked into body animations;
- background is baked into a transparent sprite request;
- copyrighted logos or real band marks appear;
- over-rendered painterly detail destroys game readability.

---

# 33. Recommended first generation order

Generate assets in this order:

1. Polly canonical master pose.
2. Glam canonical master.
3. Prog canonical master.
4. Punk canonical master.
5. Polly idle.
6. Polly walk.
7. Polly light attack 1.
8. Glam walk + attack.
9. Punk rush + shoulder charge.
10. Prog delayed strike.
11. Rat Hole Alley master environment.
12. Light hit spark.
13. Heavy hit spark.
14. Guitar swing arc.
15. Beer bottle.
16. Mic stand.

Do **not** spend time on sprint, full knockdown families, UI polish, parallax micro-animation, or secondary environmental loops until the block combat and first rough encounter feel good.

---

# 34. Canonical generation rule

Once a master image for Polly or an enemy is approved, that image becomes the strict visual reference for every later animation prompt for that character.

Do not silently redesign characters during animation generation.

**Identity first. Motion second. Polish third.**
