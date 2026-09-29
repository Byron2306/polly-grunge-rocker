# Shitty Block Double Dragon Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first playable block-art Rat Hole Alley combat slice proving Polly movement, the 3-hit light chain, heavy guitar commitment, three distinct enemy archetypes, crowd attack tokens, three encounter waves, pickups, and a slice-complete condition.

**Architecture:** TypeScript domain modules hold movement/combat/AI state and are testable without Phaser. Phaser renders deliberately primitive colored rectangles, collects keyboard input, advances the simulation, and owns the camera/UI shell. Combat geometry is explicit: body collision, hurtboxes and hitboxes remain separate, while a single feet-position ground anchor drives depth, lane checks and shadows.

**Tech Stack:** TypeScript, Vite, Phaser 3, Vitest, npm.

**Spec:** `docs/design/POLLY_VERTICAL_SLICE_COMBAT_DESIGN.md`

## Global Constraints

- Pass 1 uses only deliberately primitive block/capsule visuals; no production sprites, music, polished FX or final environment art.
- Keyboard controls: WASD/arrows move, double-tap direction or Shift may sprint, `J` light, `K` heavy, `L` interact.
- No jump, block or dodge in this implementation.
- Horizontal walk speed is the 1.0 baseline; vertical movement is `0.82x`; sprint is `1.55x`.
- Light timings are L1 `90/80/150 ms`, L2 `110/90/170 ms`, L3 `150/110/260 ms` for startup/active/recovery.
- Input buffer is approximately `180 ms`, queue depth is exactly one action, and post-chain reset target is approximately `300 ms`.
- Heavy guitar timing is `300/140/420 ms`; relative damage is L1 `1.0`, L2 `1.1`, L3 `1.5`, Heavy `2.8`.
- Standard melee lane tolerance begins at ±24 gameplay units; heavy is wider and Punk charge narrower.
- Hitstop and hitstun are distinct systems.
- Hidden stagger values begin at L1 `1`, L2 `1`, L3 `2`, Heavy `4`.
- Body collision, hurtboxes and hitboxes are separate concepts and separate data.
- Enemy AI uses the shared states `SPAWN`, `IDLE`, `APPROACH`, `ALIGN`, `THREATEN`, `ATTACK`, `RECOVER`, `HURT`, `KNOCKBACK`, `DOWN`, `GETUP`, `KO`.
- Normal simultaneous committed attacks are capped by exactly 2 attack tokens; Punk charge alone may use the controlled bypass rule.
- First-slice enemy health targets are Glam `6`, Prog `5`, Punk `6` relative Light-1 damage units.
- Maximum active enemy count is 3.
- Rat Hole Alley runs Encounter 1 Glam; Encounter 2 Prog then Glam; Encounter 3 Punk + Glam + Prog; final KO yields `SLICE COMPLETE`.

## Review Focus

- Large frame deltas / browser stalls must not skip entire attack phases or apply the same hit multiple times; fixed-step simulation owns this behavior in Task 2.
- A held `J` key must not enqueue infinite light attacks; edge-triggered input and queue depth one are pinned in Task 3.
- An attack whose X range overlaps but whose Y lane tolerance does not must miss; geometry tests belong to Task 2.
- Attack tokens must always be released on hit interruption, KO, wave cleanup and missed recovery; ownership/release tests belong to Task 5.
- Encounter progression must not advance while an earlier wave still has a living or down-but-not-KO enemy; director tests belong to Task 7.

---

## File Structure

- `package.json` — scripts and runtime/test dependencies.
- `tsconfig.json`, `vite.config.ts`, `index.html` — browser/test build shell.
- `src/main.ts` — Phaser bootstrap only.
- `src/game/config.ts` — canvas dimensions and scene registration.
- `src/game/scenes/RatHoleScene.ts` — presentation/input adapter for the slice.
- `src/sim/types.ts` — simulation primitives, actor state, vectors, rectangles, attack phases.
- `src/sim/constants.ts` — spec-pinned tuning values.
- `src/sim/fixedStep.ts` — fixed timestep accumulator.
- `src/sim/geometry.ts` — body/hurt/hit geometry and lane checks.
- `src/sim/player.ts` — Polly movement, facing, sprint and attack-state transitions.
- `src/sim/combat.ts` — hit resolution, damage, hitstop, hitstun, stagger and knockback.
- `src/sim/tokens.ts` — crowd attack-token ownership.
- `src/sim/enemies.ts` — shared enemy AI state machine and archetype configuration.
- `src/sim/pickups.ts` — bottle/mic-stand pickup and durability state.
- `src/sim/encounters.ts` — Rat Hole wave sequencing and slice completion.
- `src/sim/world.ts` — deterministic world update orchestration.
- `src/render/blockRenderer.ts` — colored rectangle/shadow/debug rendering only.
- `src/input/keyboard.ts` — edge/held keyboard intent mapping.
- `tests/**/*.test.ts` — Vitest coverage matching each simulation owner.

---

### Task 1: Bootstrap the testable Phaser block-game shell

**Files:**
- Create: `package.json`
- Create: `tsconfig.json`
- Create: `vite.config.ts`
- Create: `index.html`
- Create: `src/main.ts`
- Create: `src/game/config.ts`
- Create: `src/game/scenes/RatHoleScene.ts`
- Create: `tests/bootstrap.test.ts`

**Interfaces:**
- Consumes: none.
- Produces: `createGameConfig(): Phaser.Types.Core.GameConfig` and a browser entry that mounts `RatHoleScene`.

- [ ] **Step 1: Write the failing bootstrap test**

Assert that `createGameConfig()` returns a Phaser config using a fixed logical canvas size, pixel-art rendering, and registers `RatHoleScene` without constructing a browser game during import.

- [ ] **Step 2: Run the bootstrap test and verify failure**

Run: `npm test -- --run tests/bootstrap.test.ts`

Expected: FAIL because the project/bootstrap modules do not exist.

- [ ] **Step 3: Add minimal Vite/TypeScript/Phaser/Vitest scaffolding and `createGameConfig()`**

Use `phaser` as a runtime dependency and `vite`, `typescript`, `vitest` as dev dependencies. Keep `src/main.ts` to game creation only; do not put combat logic in the scene.

- [ ] **Step 4: Run test and production build**

Run: `npm test -- --run tests/bootstrap.test.ts && npm run build`

Expected: test PASS and Vite build succeeds.

- [ ] **Step 5: Commit**

```bash
git add package.json tsconfig.json vite.config.ts index.html src tests/bootstrap.test.ts
git commit -m "chore: bootstrap shitty block fighter"
```

---

### Task 2: Establish deterministic fixed-step simulation and combat geometry

**Files:**
- Create: `src/sim/types.ts`
- Create: `src/sim/constants.ts`
- Create: `src/sim/fixedStep.ts`
- Create: `src/sim/geometry.ts`
- Create: `tests/fixed-step.test.ts`
- Create: `tests/geometry.test.ts`

**Interfaces:**
- Consumes: elapsed browser milliseconds.
- Produces: `FixedStepClock.advance(deltaMs: number, step: (dtMs: number) => void): number`; `overlaps(a: Rect, b: Rect): boolean`; `withinLane(aY: number, bY: number, tolerance: number): boolean`; shared `Actor`, `Rect`, `Facing`, `ActorState`, `AttackPhase` types.

- [ ] **Step 1: Write failing fixed-step tests**

Pin a `1000/60 ms` simulation step, cap catch-up work to prevent a stalled tab from executing unbounded updates, and assert that sub-step remainder is preserved between calls.

- [ ] **Step 2: Write failing geometry tests**

Assert independent body/hurt/hit rectangles, edge overlap behavior, standard ±24 lane tolerance, and that X overlap with invalid Y lane alignment is not a valid melee contact.

- [ ] **Step 3: Run tests to verify failure**

Run: `npm test -- --run tests/fixed-step.test.ts tests/geometry.test.ts`

Expected: FAIL because simulation primitives are absent.

- [ ] **Step 4: Implement the fixed-step clock, types, constants and geometry helpers**

No Phaser imports are permitted in `src/sim/**`.

- [ ] **Step 5: Run tests**

Run: `npm test -- --run tests/fixed-step.test.ts tests/geometry.test.ts`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/sim tests/fixed-step.test.ts tests/geometry.test.ts
git commit -m "feat: add deterministic combat simulation core"
```

---

### Task 3: Implement Polly movement, facing, sprint and the three-hit light chain

**Files:**
- Create: `src/input/keyboard.ts`
- Create: `src/sim/player.ts`
- Create: `tests/player-movement.test.ts`
- Create: `tests/player-combo.test.ts`

**Interfaces:**
- Consumes: `PlayerIntent { moveX, moveY, sprint, lightPressed, heavyPressed, interactPressed }`, `dtMs`.
- Produces: `createPolly(): Actor`; `updatePolly(actor: Actor, intent: PlayerIntent, dtMs: number): void`; `readKeyboardIntent(...): PlayerIntent`.

- [ ] **Step 1: Write failing movement/facing tests**

Assert horizontal baseline speed, vertical `0.82x`, sprint `1.55x`, slight bounded acceleration/deceleration, and that vertical-only movement preserves horizontal facing.

- [ ] **Step 2: Write failing combo tests**

Assert L1/L2/L3 timing phases, one-action queue depth, `180 ms` buffer behavior, combo reset after roughly `300 ms`, and that holding J does not repeatedly generate edge-triggered attacks.

- [ ] **Step 3: Run tests and verify failure**

Run: `npm test -- --run tests/player-movement.test.ts tests/player-combo.test.ts`

Expected: FAIL.

- [ ] **Step 4: Implement keyboard intent and Polly state transitions**

Movement cannot arbitrarily cancel an active attack. Sprinting into Light uses normal Light 1 in this pass.

- [ ] **Step 5: Run tests**

Run: `npm test -- --run tests/player-movement.test.ts tests/player-combo.test.ts`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/input src/sim/player.ts tests/player-*.test.ts
git commit -m "feat: add polly block movement and light combo"
```

---

### Task 4: Add heavy guitar, hit resolution, hitstop, stagger and knockback

**Files:**
- Create: `src/sim/combat.ts`
- Modify: `src/sim/player.ts`
- Create: `tests/combat.test.ts`

**Interfaces:**
- Consumes: attacker `Actor`, victim `Actor`, attack definition and world time.
- Produces: `resolveAttackHit(attacker: Actor, victim: Actor, attack: AttackDefinition): HitResult`; actor timers for hitstop/hitstun; damage/stagger/knockback mutation.

- [ ] **Step 1: Write failing damage/timing tests**

Pin relative damage L1 `1.0`, L2 `1.1`, L3 `1.5`, Heavy `2.8`; heavy phases `300/140/420 ms`; stagger L1 `1`, L2 `1`, L3 `2`, Heavy `4`.

- [ ] **Step 2: Write failing contact/idempotence tests**

Assert a single active attack cannot damage the same victim twice, lane-invalid contacts miss, Heavy has wider lane tolerance than light, and hitstop does not consume hitstun time incorrectly.

- [ ] **Step 3: Write failing reaction tests**

Assert light/finisher/heavy choose increasing knockback classes, KO clamps HP to zero, and down-state invulnerability prevents prone re-hits for about `350 ms`.

- [ ] **Step 4: Run test and verify failure**

Run: `npm test -- --run tests/combat.test.ts`

Expected: FAIL.

- [ ] **Step 5: Implement heavy attack and combat resolver**

Keep hit detection/data independent from renderer dimensions.

- [ ] **Step 6: Run test**

Run: `npm test -- --run tests/combat.test.ts`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/sim/player.ts src/sim/combat.ts tests/combat.test.ts
git commit -m "feat: add guitar heavy and block combat impact"
```

---

### Task 5: Implement shared enemy AI and crowd attack-token governance

**Files:**
- Create: `src/sim/tokens.ts`
- Create: `src/sim/enemies.ts`
- Create: `tests/enemy-ai.test.ts`
- Create: `tests/attack-tokens.test.ts`

**Interfaces:**
- Consumes: Polly position/state, enemy `Actor`, `AttackTokenPool`, `dtMs`.
- Produces: `createEnemy(kind: EnemyKind): Actor`; `updateEnemy(enemy, worldView, dtMs): void`; `AttackTokenPool.acquire(actorId, reason): boolean`; `release(actorId): void`.

- [ ] **Step 1: Write failing shared-state tests**

Assert all archetypes transition through the common top-level state taxonomy rather than bespoke state machines and align by desired X distance plus lane tolerance.

- [ ] **Step 2: Write failing token tests**

Assert normal committed attacks cap at 2 simultaneous owners and tokens release on attack recovery, interruption, KO and encounter cleanup.

- [ ] **Step 3: Write failing archetype tests**

Pin Glam's long anticipation and punishable recovery, Prog's bounded `180–420 ms` visible hold variation, and Punk's `180 ms` telegraph / bounded charge / ~`500 ms` miss recovery. Assert only Punk charge can use the controlled token bypass.

- [ ] **Step 4: Run tests and verify failure**

Run: `npm test -- --run tests/enemy-ai.test.ts tests/attack-tokens.test.ts`

Expected: FAIL.

- [ ] **Step 5: Implement shared AI with data-driven archetype configuration**

Use deterministic seeded/bounded timing selection for tests; do not call `Math.random()` directly from enemy decision code.

- [ ] **Step 6: Run tests**

Run: `npm test -- --run tests/enemy-ai.test.ts tests/attack-tokens.test.ts`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/sim/tokens.ts src/sim/enemies.ts tests/enemy-ai.test.ts tests/attack-tokens.test.ts
git commit -m "feat: add glam prog punk block ai"
```

---

### Task 6: Add body separation and first-pass pickup weapons

**Files:**
- Create: `src/sim/pickups.ts`
- Modify: `src/sim/world.ts` (created in this task)
- Create: `tests/body-separation.test.ts`
- Create: `tests/pickups.test.ts`

**Interfaces:**
- Consumes: actor list, pickup list, player intent, `dtMs`.
- Produces: `createWorld(): WorldState`; `stepWorld(world, intents, dtMs): void`; `separateBodies(actors): void`; pickup states for `BOTTLE` and `MIC_STAND`.

- [ ] **Step 1: Write failing body-separation tests**

Assert actors cannot occupy the exact same ground-anchor/body space, separation is soft rather than teleporting, and depth/lane anchors remain valid after resolution.

- [ ] **Step 2: Write failing pickup tests**

Assert `L` collects only a nearby pickup, `L` drops a held pickup, Bottle lasts 3 prototype hits before breaking, and Mic Stand lasts 6 prototype hits with longer attack range than unarmed Light.

- [ ] **Step 3: Run tests and verify failure**

Run: `npm test -- --run tests/body-separation.test.ts tests/pickups.test.ts`

Expected: FAIL.

- [ ] **Step 4: Implement world orchestration, separation and pickups**

Do not add inventory. One held pickup maximum.

- [ ] **Step 5: Run tests**

Run: `npm test -- --run tests/body-separation.test.ts tests/pickups.test.ts`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/sim/world.ts src/sim/pickups.ts tests/body-separation.test.ts tests/pickups.test.ts
git commit -m "feat: add block body separation and pickups"
```

---

### Task 7: Build the Rat Hole three-wave encounter director

**Files:**
- Create: `src/sim/encounters.ts`
- Modify: `src/sim/world.ts`
- Create: `tests/encounters.test.ts`

**Interfaces:**
- Consumes: world actor states and elapsed slice time.
- Produces: `createRatHoleEncounter(): EncounterState`; `updateEncounter(world, encounter, dtMs): EncounterEvent[]`; terminal `sliceComplete: boolean`.

- [ ] **Step 1: Write failing Encounter 1 test**

Assert opening free-movement state precedes one Glam spawn and the encounter does not advance until that enemy is KO.

- [ ] **Step 2: Write failing Encounter 2 test**

Assert Prog appears first and Glam joins only after the configured delay/health gate; no more than 2 enemies are introduced here.

- [ ] **Step 3: Write failing Encounter 3 and completion tests**

Assert Punk + Glam + Prog are the final composition, global active-enemy maximum remains 3, down-but-not-KO actors block completion, and final KO sets `sliceComplete=true` exactly once.

- [ ] **Step 4: Run test and verify failure**

Run: `npm test -- --run tests/encounters.test.ts`

Expected: FAIL.

- [ ] **Step 5: Implement director and encounter events**

Keep encounter logic independent from Phaser scene coordinates except for spawn descriptors.

- [ ] **Step 6: Run test**

Run: `npm test -- --run tests/encounters.test.ts`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/sim/encounters.ts src/sim/world.ts tests/encounters.test.ts
git commit -m "feat: add rat hole block encounter sequence"
```

---

### Task 8: Wire the simulation into the deliberately ugly playable scene

**Files:**
- Create: `src/render/blockRenderer.ts`
- Modify: `src/game/scenes/RatHoleScene.ts`
- Modify: `src/game/config.ts`
- Modify: `src/main.ts`
- Create: `tests/block-renderer.test.ts`
- Create: `tests/rat-hole-integration.test.ts`

**Interfaces:**
- Consumes: `WorldState`, `EncounterState`, keyboard intent, fixed-step clock.
- Produces: a browser-playable Rat Hole block slice with camera dead zone, color-coded actors, HP display, attack/debug state labels and `SLICE COMPLETE` terminal overlay.

- [ ] **Step 1: Write failing renderer contract test**

Assert Polly, Glam, Prog and Punk have distinct block colors/labels; renderer derives Y-depth from ground anchor and does not mutate simulation state.

- [ ] **Step 2: Write failing integration test**

Drive the world through a deterministic synthetic input/KO sequence and assert the same world instance progresses from opening through all three encounters to `SLICE COMPLETE` without exceeding 3 active enemies or 2 ordinary attack tokens.

- [ ] **Step 3: Run tests and verify failure**

Run: `npm test -- --run tests/block-renderer.test.ts tests/rat-hole-integration.test.ts`

Expected: FAIL.

- [ ] **Step 4: Implement block renderer and scene adapter**

Render only primitive geometry: Polly block, pink Glam, green Prog, red Punk, shadows, crude alley boundaries, bottle, mic stand, simple HP bars and state/debug text. Add a horizontal camera dead zone and minimal vertical tracking.

- [ ] **Step 5: Run full verification**

Run: `npm test -- --run && npm run build`

Expected: all tests PASS and production build succeeds.

- [ ] **Step 6: Manual smoke test**

Run: `npm run dev -- --host 0.0.0.0`

Verify: movement/facing, J-J-J chain, K heavy, lane misses, each enemy's distinct pressure pattern, bottle/mic pickup, three waves and final `SLICE COMPLETE`.

- [ ] **Step 7: Commit**

```bash
git add src tests
 git commit -m "feat: make rat hole shitty block slice playable"
```

---

### Task 9: Pass-1 gauntlet and graduation evidence

**Files:**
- Create: `tests/pass1-gauntlet.test.ts`
- Create: `docs/evidence/PASS1_SHITTY_BLOCK_ACCEPTANCE.md`

**Interfaces:**
- Consumes: the complete block implementation.
- Produces: one automated acceptance gauntlet plus a human-tuning checklist; no art promotion decision is made automatically.

- [ ] **Step 1: Write the failing acceptance gauntlet**

Assert the core contract together: Polly movement ratios, L1→L2→L3, Heavy commitment, lane rejection, Glam interruption window, Prog timing variation bounds, Punk pressure/bypass rule, attack-token cap, active-enemy cap and final completion state.

- [ ] **Step 2: Run the gauntlet**

Run: `npm test -- --run tests/pass1-gauntlet.test.ts`

Expected before any missing fixes: FAIL on the exact uncovered contract; otherwise PASS.

- [ ] **Step 3: Fix only defects required by the approved design**

Do not add new mechanics while closing the gauntlet.

- [ ] **Step 4: Run all verification**

Run: `npm test -- --run && npm run build`

Expected: PASS.

- [ ] **Step 5: Record evidence**

In `docs/evidence/PASS1_SHITTY_BLOCK_ACCEPTANCE.md`, record test/build commands, results, manual play observations for responsiveness/weight/enemy distinction, and explicitly mark Pass 2 promotion as `NEEDS_HUMAN_PLAY_APPROVAL` until Byron says the rectangles are fun.

- [ ] **Step 6: Commit**

```bash
git add tests/pass1-gauntlet.test.ts docs/evidence/PASS1_SHITTY_BLOCK_ACCEPTANCE.md
git commit -m "test: close shitty block pass one gauntlet"
```

---

## Self-review notes

- **Spec coverage:** core controls, movement ratios, facing, sprint, combo, heavy, input buffer, collision separation, lane logic, hitstop/hitstun, stagger, health, knockdown invulnerability, three enemy identities, attack tokens, pickups, camera shell, all three encounters and completion are assigned to tasks. Audio/music/polished camera shake remain outside Pass 1 by design.
- **Step scan:** each task has one independently testable deliverable and follows red → green → verify → commit.
- **Type consistency:** `Actor`, `WorldState`, `PlayerIntent`, `AttackTokenPool`, `EncounterState` and `AttackDefinition` have single ownership and are consumed downstream by those names.
- **Review Focus:** fixed-step stalls, held-key buffering, lane false positives, leaked attack tokens and premature wave completion are each tied to an owning task test.
- **Proportion:** the plan specifies interfaces and acceptance behavior without transcribing implementation bodies.
