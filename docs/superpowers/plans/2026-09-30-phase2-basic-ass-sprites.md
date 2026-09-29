# Phase 2 Basic-Ass Sprites Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Phase 1 rectangles with chunky two-frame pixel sprites, rough Rat Hole Alley art, and prototype combat FX while preserving the proven combat simulation as the sole gameplay authority.

**Architecture:** Add a deterministic visual-state mapping layer that translates existing simulation truth into animation keys, then add a sprite-capable Phaser presentation path that falls back to the Phase 1 rectangle renderer whenever an asset is missing. Keep debug geometry independently toggleable so hitboxes, telegraphs, and the guitar sweep remain inspectable without altering simulation behavior.

**Tech Stack:** TypeScript 5.9.3, Phaser 3.90.0, Node test runner, existing fixed-step simulation, browser/mobile shell.

**Spec:** `docs/superpowers/specs/2026-09-30-phase2-basic-ass-sprites-design.md`

## Global Constraints

- Phase 1 movement, attack timing, hitboxes, hurtboxes, damage, stagger, knockback, AI, attack tokens, encounter flow, and MOVE gates remain authoritative and unchanged unless a failing regression test proves an integration defect.
- Default Phase 2 animation budget is two sprites per gameplay state.
- Character positioning remains foot-anchor driven; sprite size must never redefine world position.
- Polly working visual height remains approximately 104–120 px, centered around ~112 px.
- Raw geometry is hidden in normal aesthetic mode but available through a debug toggle.
- Missing or incomplete art must degrade to the Phase 1 block/fallback presentation rather than break playability.
- No final hair physics, cloth simulation, full animation density, music system, boss, progression system, or Phase 3 polish work in this plan.

## Review Focus

- Missing sprite keys or partially authored states must fall back cleanly instead of producing invisible actors or runtime errors.
- Facing flips must preserve the same foot anchor and world position on both left and right orientations.
- Two-frame animation timing must not advance simulation state or change attack-active timing.
- Mobile landscape rendering must preserve readable sprite scale, HUD, controls, and debug overlays without clipping.
- Debug geometry must remain aligned with sprites through movement, depth sorting, attack phases, and MOVE transitions.

---

### Task 1: Deterministic Visual-State Mapping

**Files:**
- Create: `src/render/visualState.ts`
- Create: `tests/visual-state.test.ts`

**Interfaces:**
- Consumes: `Actor` and existing simulation fields from `src/sim/types.ts`.
- Produces: `export type VisualStateKey = string`, `export interface VisualStateDescriptor`, `export function visualStateForActor(actor: Actor): VisualStateDescriptor`.

- [ ] **Step 1: Write the failing visual-state tests**

Cover Polly idle, walk, sprint, L1/L2/L3, Heavy startup/active, hurt/KO; Glam THREATEN/ATTACK; Prog THREATEN/ATTACK; Punk THREATEN/ATTACK. Assert the returned visual key, facing, and whether the state should loop.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `npm test -- --test-name-pattern="visual state"`
Expected: FAIL because `src/render/visualState.ts` does not exist.

- [ ] **Step 3: Implement the mapping layer**

Implement `visualStateForActor(actor: Actor): VisualStateDescriptor` with no writes to the actor. Derive movement presentation from velocity magnitude and attack presentation from existing attack IDs/phases.

- [ ] **Step 4: Add review-focus tests for unknown/incomplete states**

Assert an unknown or transitional actor state maps to a stable idle/fallback key rather than throwing.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `npm test`
Expected: existing suite plus new visual-state tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/render/visualState.ts tests/visual-state.test.ts
git commit -m "feat: map simulation state to visual states"
```

### Task 2: Sprite Manifest and Two-Frame Animation Contract

**Files:**
- Create: `src/render/spriteManifest.ts`
- Create: `tests/sprite-manifest.test.ts`
- Create directories under: `assets/characters/polly/`, `assets/enemies/glam/`, `assets/enemies/prog/`, `assets/enemies/punk/`, `assets/fx/`, `assets/environments/rat_hole/`

**Interfaces:**
- Consumes: `VisualStateKey` from Task 1.
- Produces: `SpriteFrameRef`, `SpriteAnimationDef`, `PHASE2_SPRITE_MANIFEST`, `framesForVisualState(key: VisualStateKey)`.

- [ ] **Step 1: Write failing manifest tests**

Assert every approved Phase 2 Polly state and enemy state has a manifest entry supporting exactly two frame slots, while allowing either slot to temporarily reference the same placeholder image.

- [ ] **Step 2: Run and verify RED**

Run: `npm test -- --test-name-pattern="sprite manifest"`
Expected: FAIL because manifest module is absent.

- [ ] **Step 3: Implement the manifest contract**

Keep asset paths declarative and centralized. Do not put Phaser objects into the manifest.

- [ ] **Step 4: Add missing-key fallback test**

Assert `framesForVisualState()` returns the explicit fallback descriptor for an unregistered key.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `npm test`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/render/spriteManifest.ts tests/sprite-manifest.test.ts assets
git commit -m "feat: define phase2 sprite manifest"
```

### Task 3: Sprite-Capable Actor Renderer With Block Fallback

**Files:**
- Create: `src/render/actorPresenter.ts`
- Modify: `src/game/scenes/RatHoleScene.ts`
- Modify: `src/phaser-global.d.ts`
- Create: `tests/actor-presenter.test.ts`

**Interfaces:**
- Consumes: `visualStateForActor()`, `framesForVisualState()`, existing block descriptors, camera offset, world actors.
- Produces: `ActorPresenter` with `syncActor(actor, cameraOffsetX)`, `removeMissing(actorIds)`, `setDebugGeometry(enabled)`, `destroy()`.

- [ ] **Step 1: Write failing presenter tests around pure placement decisions**

Test that presentation X/Y derives from actor foot anchor, left/right facing flips presentation without changing anchor coordinates, and missing sprite assets select the block fallback path.

- [ ] **Step 2: Run and verify RED**

Run: `npm test -- --test-name-pattern="actor presenter"`
Expected: FAIL because presenter module is absent.

- [ ] **Step 3: Implement presenter boundary**

Keep Phaser-specific creation/update logic inside `ActorPresenter`; keep state selection in Task 1 and asset lookup in Task 2.

- [ ] **Step 4: Integrate presenter into `RatHoleScene`**

Retain the Phase 1 block renderer as fallback/debug instead of deleting it. Continue depth ordering from actor ground `y`.

- [ ] **Step 5: Add regression test for sim non-mutation**

Snapshot actor simulation fields before and after presenter synchronization and assert no gameplay field changes.

- [ ] **Step 6: Run full tests and build**

Run: `npm test && npm run build`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/render/actorPresenter.ts src/game/scenes/RatHoleScene.ts src/phaser-global.d.ts tests/actor-presenter.test.ts
git commit -m "feat: render actors through sprite-capable presenter"
```

### Task 4: Debug Geometry Toggle

**Files:**
- Create: `src/render/debugGeometry.ts`
- Modify: `src/game/scenes/RatHoleScene.ts`
- Modify: `src/input/keyboard.ts`
- Create: `tests/debug-geometry.test.ts`

**Interfaces:**
- Consumes: existing block/hurt/strike geometry and actor positions.
- Produces: `DebugGeometryMode`, `toggleDebugGeometry(mode)`, `debugGeometryDescriptors(world)`.

- [ ] **Step 1: Write failing tests**

Assert default mode is aesthetic/no raw boxes, toggle enables body/hurt/attack shapes, and descriptors remain aligned to world coordinates during movement and facing changes.

- [ ] **Step 2: Run and verify RED**

Run: `npm test -- --test-name-pattern="debug geometry"`
Expected: FAIL.

- [ ] **Step 3: Implement debug descriptor layer and keyboard toggle**

Use one explicit key such as `F2` on desktop; mobile may remain aesthetic-only for Phase 2 unless a simple HUD toggle is already available without expanding scope.

- [ ] **Step 4: Render debug geometry after sprite/FX layers**

Ensure geometry can coexist with sprite presentation and is never required for normal rendering.

- [ ] **Step 5: Run tests/build and commit**

Run: `npm test && npm run build`
Expected: PASS.

```bash
git add src/render/debugGeometry.ts src/game/scenes/RatHoleScene.ts src/input/keyboard.ts tests/debug-geometry.test.ts
git commit -m "feat: preserve toggleable combat geometry"
```

### Task 5: Polly Basic-Ass Sprite Slice

**Files:**
- Add/update: `assets/characters/polly/**`
- Modify: `src/render/spriteManifest.ts`
- Create: `tests/polly-phase2-assets.test.ts`

**Interfaces:**
- Consumes: sprite manifest contract and ActorPresenter.
- Produces: Phase 2 Polly visual coverage for idle, walk, sprint, L1, L2, L3, Heavy, hurt, knockback/down, get-up, pickup/carry, victory.

- [ ] **Step 1: Add failing asset-coverage tests**

Assert every Polly visual key resolves to two frame references and Heavy references a separate guitar/arc FX key rather than embedding the swing arc into the body sprite contract.

- [ ] **Step 2: Run and verify RED**

Run: `npm test -- --test-name-pattern="Polly Phase 2"`
Expected: FAIL until the manifest/assets are populated.

- [ ] **Step 3: Add chunky Polly assets**

Target ~112 px character height, strong auburn hair mass, red-black flannel, dark top/jeans, heavy boots, readable guitar silhouette. Prefer strong pose contrast over extra frames.

- [ ] **Step 4: Register Polly assets and animation cadence**

Two-frame loops for locomotion; attack frames selected by visual state and simulation timing, never by an animation callback that advances combat state.

- [ ] **Step 5: Verify mobile-scale readability**

Build and manually inspect landscape at 960×540 logical scale with touch controls visible. Confirm feet align to the existing anchor and sprites are not clipped.

- [ ] **Step 6: Run full tests/build and commit**

Run: `npm test && npm run build`
Expected: PASS.

```bash
git add assets/characters/polly src/render/spriteManifest.ts tests/polly-phase2-assets.test.ts
git commit -m "feat: add chunky Polly phase2 sprites"
```

### Task 6: Glam, Prog, and Punk Basic-Ass Sprite Slice

**Files:**
- Add/update: `assets/enemies/glam/**`, `assets/enemies/prog/**`, `assets/enemies/punk/**`
- Modify: `src/render/spriteManifest.ts`
- Create: `tests/enemy-phase2-assets.test.ts`

**Interfaces:**
- Consumes: visual-state mapper, sprite manifest, ActorPresenter.
- Produces: two-frame prototype coverage for each approved enemy state.

- [ ] **Step 1: Write failing enemy coverage tests**

Assert Glam, Prog, and Punk required visual keys each resolve to two frame references and remain visually distinguishable by manifest family/palette identity.

- [ ] **Step 2: Run and verify RED**

Run: `npm test -- --test-name-pattern="enemy Phase 2"`
Expected: FAIL.

- [ ] **Step 3: Add enemy prototype art**

Glam: teased-hair/theatrical silhouette. Prog: glasses/controlled posture/keytar cue. Punk: mohawk/forward lean/charge silhouette.

- [ ] **Step 4: Register assets without changing enemy timing**

THREATEN/ATTACK visuals must subscribe to the existing enemy state machine exactly as authored in Phase 1.

- [ ] **Step 5: Run full tests/build and commit**

Run: `npm test && npm run build`
Expected: PASS.

```bash
git add assets/enemies src/render/spriteManifest.ts tests/enemy-phase2-assets.test.ts
git commit -m "feat: add chunky enemy phase2 sprites"
```

### Task 7: Rat Hole Alley Basic Environment

**Files:**
- Create: `src/render/ratHoleEnvironment.ts`
- Add/update: `assets/environments/rat_hole/**`
- Modify: `src/game/scenes/RatHoleScene.ts`
- Create: `tests/rat-hole-environment.test.ts`

**Interfaces:**
- Consumes: camera offset and encounter stage.
- Produces: modular far/mid/ground/foreground environment descriptors and Phaser presentation.

- [ ] **Step 1: Write failing environment tests**

Assert modular layers exist for far, middle, gameplay plane, and foreground; world-space layers apply deterministic camera/parallax offsets; gameplay collision is not derived from art dimensions.

- [ ] **Step 2: Run and verify RED**

Run: `npm test -- --test-name-pattern="Rat Hole environment"`
Expected: FAIL.

- [ ] **Step 3: Add minimal Rat Hole art kit**

Include brick/facade, club door, fence/dumpster, asphalt/puddle tiles, posters/neon, and a small foreground clutter set. No giant flattened painting.

- [ ] **Step 4: Integrate environment renderer**

Keep actors/FX layered correctly by ground depth and ensure MOVE transitions scroll through connected visual space.

- [ ] **Step 5: Run tests/build and commit**

Run: `npm test && npm run build`
Expected: PASS.

```bash
git add src/render/ratHoleEnvironment.ts assets/environments/rat_hole src/game/scenes/RatHoleScene.ts tests/rat-hole-environment.test.ts
git commit -m "feat: add basic Rat Hole alley art"
```

### Task 8: Prototype Combat FX

**Files:**
- Create: `src/render/combatFx.ts`
- Add/update: `assets/fx/**`
- Modify: `src/game/scenes/RatHoleScene.ts`
- Create: `tests/combat-fx.test.ts`

**Interfaces:**
- Consumes: attack phase, actor kind, hit/KO outcomes already exposed by simulation/render descriptors.
- Produces: presentation-only FX descriptors for light hit, heavy hit, guitar arc, Prog waveform, Punk rush, KO burst, bottle break, dust/debris.

- [ ] **Step 1: Write failing FX mapping tests**

Assert guitar Heavy maps to a separate swing-arc FX, Prog and Punk remain visually distinct, and no FX descriptor can alter damage/hit resolution.

- [ ] **Step 2: Run and verify RED**

Run: `npm test -- --test-name-pattern="combat FX"`
Expected: FAIL.

- [ ] **Step 3: Implement FX descriptors and renderer**

Keep effects short, chunky, and screen-print/gig-poster adjacent. Reuse Phase 1 geometry timing where useful for telegraph alignment.

- [ ] **Step 4: Run full tests/build and commit**

Run: `npm test && npm run build`
Expected: PASS.

```bash
git add src/render/combatFx.ts assets/fx src/game/scenes/RatHoleScene.ts tests/combat-fx.test.ts
git commit -m "feat: add phase2 prototype combat fx"
```

### Task 9: Phase 2 Regression and Human Acceptance Gauntlet

**Files:**
- Create: `tests/phase2-gauntlet.test.ts`
- Modify only if required by proven defects: Phase 2 renderer/presentation files
- Update: `docs/superpowers/specs/2026-09-30-phase2-basic-ass-sprites-design.md` status after acceptance

**Interfaces:**
- Consumes: all Phase 2 presentation modules plus existing Phase 1 gauntlet.
- Produces: machine verification that the aesthetic layer did not change simulation truth, followed by human play acceptance.

- [ ] **Step 1: Write the Phase 2 integration gauntlet**

Assert the same deterministic encounter can progress through E1 → MOVE1 → E2 → MOVE2 → E3 → COMPLETE with sprite presentation enabled, maximum active enemy/token constraints unchanged, and all actor world positions/hit outcomes matching the simulation-only run.

- [ ] **Step 2: Add review-focus regressions**

Cover missing sprite fallback, facing anchor stability, animation frame advancement without sim mutation, mobile logical viewport descriptors, and debug-overlay alignment.

- [ ] **Step 3: Run all automated verification**

Run: `npm test && npm run build`
Expected: all tests PASS and build completes with no TypeScript errors.

- [ ] **Step 4: Perform mobile human play acceptance**

On Termux/Android, run the full Rat Hole slice in landscape. Confirm Polly/enemies remain readable, controls remain smooth, MOVE flow still feels good, combat remains dynamic/engaging, and art does not obscure telegraphs or hit timing.

- [ ] **Step 5: Mark Phase 2 PASS only after human acceptance**

Update the design doc status only after the user explicitly confirms the aesthetic build retains the Phase 1 combat feel.

- [ ] **Step 6: Commit acceptance evidence/documentation**

```bash
git add tests/phase2-gauntlet.test.ts docs/superpowers/specs/2026-09-30-phase2-basic-ass-sprites-design.md
git commit -m "test: verify phase2 sprite vertical slice"
```
