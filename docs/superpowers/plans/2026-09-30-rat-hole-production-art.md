# Rat Hole Production Art Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Rat Hole's flat placeholder staging with a production-quality painterly pixel-art Grunge environment that preserves the proven combat plane and establishes the visual baseline for later genre worlds.

**Architecture:** Keep gameplay coordinates, encounters and combat simulation unchanged. Replace the current single flattened zone plates with authored environment layers and a small presentation-only descriptor model. Rat Hole remains one continuous physical venue/alley whose spaces gradually become better suited to the later musical teaching encounters.

**Tech Stack:** TypeScript 5.9.x, Phaser 3 presentation layer, PNG assets, Node test runner, existing fixed 960×540 scene composition.

**Spec:** `docs/superpowers/specs/2026-09-30-pattern-map-combat-architecture.md`

## Global Constraints

- Rat Hole is the Grunge home world and must visually read as Polly's own scene.
- Use the approved painterly pixel-art mockup as the visual target.
- Do not use flat procedural rectangles as production environment art.
- Environment art must not alter combat simulation, actor coordinates, walk-band constants or enemy AI.
- Preserve the accepted upper/lower walk band and foot-anchor behavior.
- Combat silhouettes must remain readable over the environment.
- Environment must support future teaching spaces without implementing Pattern Map runtime yet.
- Work locally with binary assets first; do not use text-only GitHub file writes for PNGs.

## Review Focus

1. **Combat readability over dense art:** Polly and enemies must remain visually separable at the darkest and brightest environment points.
2. **Camera seams:** overlapping zone transitions must not expose gaps or visible hard cuts while scrolling.
3. **Foreground occlusion:** near-camera art may cross the lower frame but must not hide actors inside the active walk band for sustained periods.
4. **Mobile presentation:** 960×540 art must remain sharp and compositionally legible under the existing landscape scaling path.
5. **Simulation isolation:** loading or moving environment layers must not mutate world state, actor positions, collision geometry or encounter progression.

---

## File Structure

### Create

- `assets/environment/rat-hole/production/zone1-far.png`
- `assets/environment/rat-hole/production/zone1-mid.png`
- `assets/environment/rat-hole/production/zone1-near.png`
- `assets/environment/rat-hole/production/zone2-far.png`
- `assets/environment/rat-hole/production/zone2-mid.png`
- `assets/environment/rat-hole/production/zone2-near.png`
- `assets/environment/rat-hole/production/zone3-far.png`
- `assets/environment/rat-hole/production/zone3-mid.png`
- `assets/environment/rat-hole/production/zone3-near.png`
- `docs/art/RAT_HOLE_PRODUCTION_MAP.md`
- `tests/rat-hole-production-layers.test.ts`

### Modify

- `src/render/ratHoleProductionBackdrop.ts`
- `src/game/scenes/RatHoleScene.ts`
- `tests/rat-hole-production-backdrop.test.ts`

### Do Not Modify

- `src/sim/constants.ts`
- `src/sim/player.ts`
- `src/sim/enemies.ts`
- `src/sim/world.ts`
- attack timing or damage definitions
- encounter progression logic

---

### Task 1: Freeze the Rat Hole Visual Map

**Files:**
- Create: `docs/art/RAT_HOLE_PRODUCTION_MAP.md`

**Interfaces:**
- Consumes: approved Rat Hole mockup and campaign architecture.
- Produces: exact composition brief for the three production spaces and layer ownership.

- [ ] **Step 1: Author the map document**

Pin these three spaces:

- Zone 1: club entrance / home-scene arrival. Warm red-magenta practical light, Rat Hole signage, wet asphalt, layered posters, dumpster and crowded brick facade.
- Zone 2: service/rehearsal alley. Colder cyan practical light, vents, pipes, fencing, backstage/service architecture and deeper spatial recession.
- Zone 3: loading/backstage performance threshold. Violet/red light, shutters, cases/crates, van/loading clutter and a denser final-arena silhouette.

Pin these layer responsibilities:

- `far`: skyline, upper architecture, remote silhouettes;
- `mid`: primary walls, doors, venue architecture, large props behind actors;
- `near`: near-camera poles, cables, fence fragments, trash, rain/steam framing that may parallax but does not own collision.

Document the invariant combat floor and the accepted walk band as presentation boundaries, not art collision.

- [ ] **Step 2: Review the document against the approved mockup**

Expected: no wording permits flat vector-like walls, procedural placeholder rectangles or large dead untextured areas as final art.

- [ ] **Step 3: Commit text-only art map**

```bash
git add docs/art/RAT_HOLE_PRODUCTION_MAP.md
git commit -m "docs: map Rat Hole production environment"
```

---

### Task 2: Define Production Layer Descriptors

**Files:**
- Modify: `src/render/ratHoleProductionBackdrop.ts`
- Create: `tests/rat-hole-production-layers.test.ts`

**Interfaces:**
- Consumes: existing camera offset.
- Produces:
  - `type RatHoleLayerKind = 'FAR'|'MID'|'NEAR'`
  - `interface RatHoleLayerDef`
  - `RAT_HOLE_LAYERS: readonly RatHoleLayerDef[]`
  - `ratHoleLayerScreenX(layer:RatHoleLayerDef,cameraOffsetX:number):number`

Required fields:

```ts
interface RatHoleLayerDef {
  zone:1|2|3;
  kind:RatHoleLayerKind;
  assetKey:string;
  path:string;
  worldX:number;
  width:960;
  height:540;
  depth:number;
  parallax:number;
}
```

Required world anchors remain `0`, `850`, `1700`.

- [ ] **Step 1: Write failing descriptor tests**

Assert:

- exactly nine production layers exist;
- every zone has one FAR, MID and NEAR layer;
- all layers remain 960×540;
- world anchors remain `[0,850,1700]` per layer family;
- FAR and MID depths are behind actors;
- NEAR is presentation-only and above actors;
- parallax is deterministic and never mutates input descriptors.

- [ ] **Step 2: Run the focused test**

Run the repository's normal test-build path and execute the compiled test, rather than passing raw `.ts` paths to `npm test`.

Expected: FAIL because the production layer API does not exist.

- [ ] **Step 3: Implement the descriptor API**

Keep all calculations pure. Do not import Phaser or simulation modules.

- [ ] **Step 4: Run focused and existing backdrop tests**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/render/ratHoleProductionBackdrop.ts tests/rat-hole-production-layers.test.ts tests/rat-hole-production-backdrop.test.ts
git commit -m "refactor: define Rat Hole production layers"
```

---

### Task 3: Author Zone 1 Production Art

**Files:**
- Create three Zone 1 PNGs under `assets/environment/rat-hole/production/`.

**Interfaces:**
- Consumes: Task 1 art map and Task 2 layer dimensions.
- Produces: production-ready Zone 1 binary assets.

- [ ] **Step 1: Create the three authored images**

Required visual evidence:

- layered brick and masonry texture;
- practical neon and doorway light spill;
- irregular wet reflections;
- overlapping posters and scene clutter;
- believable depth recession;
- readable combat floor;
- no procedural-flat aesthetic.

- [ ] **Step 2: Inspect at native 960×540 and mobile-scaled size**

Expected: Polly remains readable at the darkest and brightest points.

- [ ] **Step 3: Verify PNG integrity locally**

Check file signatures and dimensions before Git staging.

- [ ] **Step 4: Commit binaries with local Git**

```bash
git add assets/environment/rat-hole/production/zone1-*.png
git commit -m "art: add Rat Hole entrance production layers"
```

---

### Task 4: Author Zones 2 and 3 Production Art

**Files:**
- Create the six remaining PNGs.

**Interfaces:**
- Consumes: the same visual language and continuous physical-space map.
- Produces: complete production environment set.

- [ ] **Step 1: Author Zone 2**

Keep the same world and material language while shifting toward colder service/rehearsal lighting and increased depth complexity.

- [ ] **Step 2: Author Zone 3**

Keep continuity while increasing backstage/loading density and visual intensity without becoming a different genre world.

- [ ] **Step 3: Inspect continuity across all three spaces**

Expected: they feel like successive areas of one Grunge venue, not three disconnected paintings.

- [ ] **Step 4: Verify PNG signatures and dimensions**

Expected: all six new files are valid 960×540 PNGs.

- [ ] **Step 5: Commit binaries with local Git**

```bash
git add assets/environment/rat-hole/production/zone2-*.png assets/environment/rat-hole/production/zone3-*.png
git commit -m "art: complete Rat Hole production environment"
```

---

### Task 5: Wire Production Layers Into Rat Hole Scene

**Files:**
- Modify: `src/game/scenes/RatHoleScene.ts`
- Modify: `tests/rat-hole-production-backdrop.test.ts`

**Interfaces:**
- Consumes: `RAT_HOLE_LAYERS` and `ratHoleLayerScreenX()`.
- Produces: layered Rat Hole presentation using the existing camera and simulation.

- [ ] **Step 1: Extend scene tests around loading and placement**

Assert the scene contract loads all nine assets and derives placement from layer descriptors rather than hardcoded asset names.

- [ ] **Step 2: Run tests to verify failure**

Expected: FAIL because the scene still uses the old backdrop list.

- [ ] **Step 3: Replace old backdrop setup with descriptor-driven layer setup**

Use descriptor `depth` and `parallax`. Do not add gameplay collision or alter world state.

- [ ] **Step 4: Run full test suite and build**

```bash
npm test
npm run build
```

Expected: all tests PASS and build exits 0.

- [ ] **Step 5: Commit**

```bash
git add src/game/scenes/RatHoleScene.ts tests/rat-hole-production-backdrop.test.ts
git commit -m "feat: render Rat Hole production environment"
```

---

### Task 6: Human Visual Gauntlet

**Files:**
- No product code unless the gauntlet exposes a defect.

**Interfaces:**
- Consumes: Tasks 1–5.
- Produces: human acceptance or a focused defect list.

- [ ] **Step 1: Launch the game locally**

```bash
npm run dev
```

- [ ] **Step 2: Play from opening through slice completion**

Review:

- visual depth;
- world continuity;
- Polly/enemy readability;
- foreground occlusion;
- camera seams;
- mobile landscape composition;
- whether Rat Hole feels like Grunge home turf.

- [ ] **Step 3: Compare directly with the approved concept mockup**

Expected: production result belongs to the same painterly pixel-art family. Reject any result that falls back to flat adventure-game staging.

- [ ] **Step 4: Re-run regression gauntlet after any visual fixes**

```bash
npm test
npm run build
```

Expected: PASS.

- [ ] **Step 5: Mark Phase 1 ship gate only after human approval**

No Pattern Map runtime work depends on Rat Hole production art until this gate is accepted.
