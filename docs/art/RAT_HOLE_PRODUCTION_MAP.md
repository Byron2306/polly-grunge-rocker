# Rat Hole Production Environment Map

**Date:** 2026-09-30  
**Status:** Production art brief  
**World:** Rat Hole / Grunge  
**Target frame:** 960×540  
**Reference:** approved painterly pixel-art Rat Hole concept

## 1. Purpose

Rat Hole is Polly's home scene and the first campaign world. It must feel inhabited, tactile, damp, improvised and unmistakably Grunge. It is not a generic alley, not a flat adventure-game backdrop, and not a procedural arrangement of rectangles.

The environment must support readable belt-scroller combat while establishing the visual baseline against which later genre worlds become more extravagant, aggressive, industrial or structurally strange.

The entire level is one continuous physical venue/alley system divided into three successive production spaces.

## 2. Locked visual language

Final Rat Hole art must use painterly pixel-art value structure with believable material depth.

Required qualities:

- layered brick and masonry with age, grime, chipped edges and shadow;
- dirty metal, timber, paper, wet asphalt, glass and painted surfaces that read as distinct materials;
- practical lighting from signs, doorways, fluorescents and backstage fixtures;
- irregular wet reflections rather than mirrored geometric strips;
- overlapping posters, stickers, cables, rubbish, bottles, cases and venue clutter;
- deep recesses around doors, alleys, fences and service architecture;
- foreground silhouettes and occluders that frame the action without hiding the walk band;
- uneven architecture and believable environmental history;
- dense detail around the world edges while preserving a clean combat silhouette zone;
- pixel-sharp rendering without soft resampling.

Explicitly reject as final art:

- flat brick wallpaper;
- clean vector-like rectangles posing as architecture;
- large dead untextured walls;
- floating neon signs with no material integration;
- icon-like props simply placed on a background;
- uniform puddles or reflections;
- visual treatment that evokes early flat adventure-game staging.

## 3. Continuous spatial progression

### Zone 1 — Rat Hole entrance / home-scene arrival

Purpose: establish that Polly has arrived on familiar turf.

Visual anchors:

- Rat Hole signage integrated into the club facade;
- warm red-magenta practical light;
- doorway light spilling physically across wet asphalt;
- crowded old brick facade;
- layered gig posters and stickers;
- dumpster, rubbish bags, bottles and alley debris;
- battered pipes, cables and fixtures;
- visible depth into the club entrance or adjacent recesses;
- warm reflections broken by puddles, cracks and surface grime.

This is the most welcoming area in Rat Hole, but never clean. It should feel like somewhere Polly has been a hundred times.

### Zone 2 — service / rehearsal alley

Purpose: move deeper into the working guts of the venue and prepare space for future music-role teaching encounters.

Visual anchors:

- colder cyan practical lighting;
- vents, exposed pipes, utility boxes and service doors;
- chain-link fence and partial sightlines into deeper recesses;
- rehearsal-room or loading-service clues;
- cable coils, stacked cases, battered equipment and backstage junk;
- more obvious depth recession than Zone 1;
- wet surfaces still physically continuous with the entrance alley;
- colder highlights without changing the world into a new genre.

The space should feel functional and used by musicians, roadies and venue staff rather than theatrically decorated.

### Zone 3 — loading / backstage performance threshold

Purpose: create the densest and most intense Rat Hole space for the level's final combined encounter.

Visual anchors:

- violet/red practical lighting layered over the established Grunge palette;
- loading shutters, backstage doors and service architecture;
- instrument cases, crates, amp stacks and van/loading clutter;
- heavier silhouette density around the frame edges;
- deeper dark pockets and stronger light pools;
- visual hints of the stage/performance world immediately beyond;
- the same brick, metal, asphalt and paper material language established earlier.

Zone 3 may feel more intense but must still unmistakably be the same Grunge venue.

## 4. Layer ownership

Each zone is authored as three 960×540 transparent/opaque production layers.

### FAR

Owns:

- skyline;
- upper architecture;
- remote windows;
- distant rooflines;
- remote silhouettes;
- far atmospheric depth.

Rules:

- always behind actors;
- lowest visual contrast around the combat plane;
- may parallax more slowly than world motion;
- never owns gameplay collision.

### MID

Owns:

- primary walls;
- club facade;
- doors and shutters;
- large props behind actors;
- signage;
- posters;
- pipes and vents;
- fences behind the combat plane;
- most baked practical lighting and wall shadow.

Rules:

- carries most visual identity;
- remains behind actors;
- must not imply walkable space above the accepted combat floor;
- never owns gameplay collision.

### NEAR

Owns:

- partial poles;
- cable silhouettes;
- fence fragments near camera;
- rubbish or crates at extreme lower/side edges;
- rain and steam framing elements when authored into the world layer;
- near-camera silhouettes used for depth.

Rules:

- may render above actors;
- must not obscure an actor in the active walk band for sustained periods;
- keep the middle combat corridor visually open;
- presentation only, with no collision authority.

## 5. Combat floor invariant

Art does not define gameplay collision.

The accepted simulation walk band remains authoritative. Environment painting must visually support that band by making the combat floor read as pavement/asphalt rather than facade, doorway, wall or inaccessible architecture.

The upper boundary should visually coincide with the believable edge of the usable alley floor. No painted doorway, stair or facade element may invite the player to walk into architecture the simulation correctly forbids.

Foot-anchor readability remains mandatory. Shadows and floor texture should make actor grounding obvious without changing actor coordinates.

## 6. Readability envelope

At every zone and lighting condition:

- Polly's auburn hair, flannel silhouette and dark jeans must remain separable from the background;
- dark enemies must not disappear into shadow pockets;
- bright practical lights must not bleach attack telegraphs;
- foreground elements must not sit over the center of the active combat band for long stretches;
- wet reflections must support atmosphere without competing with hit FX;
- the lowest and highest contrast areas must still permit immediate actor recognition on mobile.

## 7. Camera continuity

World anchors stay fixed at:

- Zone 1: `0`
- Zone 2: `850`
- Zone 3: `1700`

The 110-pixel overlap between successive 960-wide spaces is intentional and must be painted for continuity.

At overlaps:

- masonry direction and curb/floor height must agree;
- lighting may transition gradually but may not hard-cut;
- no duplicated large prop should expose the plate boundary;
- the asphalt/pavement texture must continue naturally;
- foreground framing should avoid revealing a seam.

## 8. Future teaching-space support

Rat Hole art should quietly prepare for the later onboarding structure without implementing any Pattern Map runtime yet.

The spaces should provide believable room for:

- Polly-alone opening combat;
- drummer timing lesson;
- bassist groove/lane lesson;
- rhythm-guitar structure lesson;
- vocalist call/response lesson;
- final full-band Grunge encounter.

These are staging needs, not painted tutorial labels. The venue must continue to feel like a real local scene.

## 9. Production acceptance

A zone is not production-ready merely because it is attractive in isolation.

It passes only when:

1. it belongs to the approved painterly pixel-art family;
2. it feels physically connected to the adjacent Rat Hole space;
3. actors remain readable through the entire walk band;
4. no foreground layer produces sustained combat occlusion;
5. native and mobile-scaled presentation remain sharp;
6. the environment changes no simulation or encounter behavior;
7. human review confirms that Rat Hole feels like Grunge home turf.
