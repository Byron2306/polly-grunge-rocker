# PASS 1 — SHITTY BLOCK ACCEPTANCE

**Status:** AUTOMATED PASS / HUMAN PLAY REQUIRED  
**Promotion to Pass 2:** `NEEDS_HUMAN_PLAY_APPROVAL`

## What this proves

The deliberately primitive Rat Hole Alley build now has a deterministic TypeScript combat simulation, playable browser presentation adapter, Polly movement and facing, a three-hit light chain, heavy guitar commitment attack, lane-aware melee contact, hitstop/hitstun separation, stagger/knockback, Glam/Prog/Punk AI identities, two-token ordinary crowd governance with Punk charge bypass, bottle/mic-stand pickups, three encounter waves, and a terminal `SLICE COMPLETE` state.

## Verification

Executed in the implementation sandbox:

```bash
npm test
npm run build
```

Result:

- 29 automated tests passed
- 0 failed
- TypeScript production build passed
- fixed-step stall cap and remainder behavior passed
- lane false-positive rejection passed
- held-key edge triggering passed
- attack-token cap/release contract passed
- three-wave director and final completion passed
- integrated Pass-1 gauntlet passed on first run after Tasks 1–8

## Tooling ruling

The execution sandbox could not resolve external npm/GitHub package hosts. To keep implementation and verification moving without weakening the simulation boundary, Pass 1 uses globally available TypeScript and Node's built-in test runner. Phaser 3 is loaded by the browser shell from the jsDelivr CDN rather than installed as an npm dependency; Vite/Vitest are therefore deferred tooling, not deferred gameplay behavior.

This changes bootstrap/tooling only. `src/sim/**` remains renderer-independent as required by the approved design.

## Human play checklist

Not executable inside this headless sandbox. Byron should judge these before Pass 2:

- [ ] Polly movement feels responsive rather than floaty.
- [ ] Vertical lane movement feels useful but not like an infinite escape.
- [ ] J → J → J reads naturally and does not feel mushy.
- [ ] K guitar heavy feels dangerous, weighty and punishable on whiff.
- [ ] Lane misses feel fair and visually understandable.
- [ ] Glam creates a clear interrupt/wait decision.
- [ ] Prog's delayed timing is weird but readable rather than random-feeling.
- [ ] Punk creates real repositioning pressure.
- [ ] Three-enemy composition feels busy without becoming soup.
- [ ] Bottle and mic stand are discoverable and satisfying enough to keep.
- [ ] Final wave and `SLICE COMPLETE` arrive without pacing drag.
- [ ] Rectangles are already fun enough to justify sprite production.

## Graduation rule

Pass 2 must not begin merely because automated tests are green.

**Required decision:** `NEEDS_HUMAN_PLAY_APPROVAL`

If the rectangles are not fun, tune Pass 1. Do not hide weak combat underneath better art.
