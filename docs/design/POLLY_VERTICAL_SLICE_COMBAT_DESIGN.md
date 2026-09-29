# POLLY GRUNGE ROCKER
## B. Vertical Slice Combat Design v0.1

Status: **APPROVED IN CHAT, CANONICAL DESIGN DRAFT**

## Design objective

The first playable build must already contain the game's core combat idea:

> **Simple controls, expressive consequences, enemies that make the player change behaviour.**

The target is classic arcade readability with modern impact and differentiated enemy behaviour:

**move → position → hit → react → improvise**

The player should understand Polly within thirty seconds. Mastery comes from spacing, crowd control, timing and reading enemy personalities.

---

## 1. Control contract

### Movement
- WASD / arrow keys
- left/right movement
- up/down movement within the combat lane

### Sprint
- double-tap direction initially
- Shift may be supported as a keyboard convenience

### Combat
- `J` = light attack
- `K` = heavy attack
- `L` = pickup / contextual interaction

### Optional controller mapping
- Left stick / D-pad = movement
- X / Square = light
- Y / Triangle = heavy
- B / Circle = interaction
- shoulder/trigger sprint can be evaluated later

Not part of the first slice:
- dedicated block
- dodge button
- jump

The opening build should avoid defensive-button bloat until positioning and base attack timing have proven themselves.

---

## 2. Combat plane

The game uses a classic belt-scroller plane:

- X = horizontal movement
- Y = shallow battlefield depth

An attack can only connect when horizontal range and lane separation are both valid.

Initial melee Y tolerance target:

- standard melee: approximately ±18–24 native gameplay units
- heavy guitar: somewhat wider
- punk shoulder charge: somewhat narrower

These are tuning values, not fixed laws.

---

## 3. Ground anchor and depth priority

Every character uses a feet-position ground anchor.

```text
groundAnchor = feet position
depth = groundAnchor.y
```

The same anchor drives:
- rendering depth
- shadow position
- body collision origin
- melee lane comparison
- pickup range

Characters lower on screen render in front of characters higher on screen.

---

## 4. Player movement

Polly should feel nimble but not floaty.

Initial relative tuning:

```text
walk speed       1.0
vertical speed   0.82
sprint speed     1.55
```

Vertical movement is intentionally slower than horizontal movement so lane movement remains tactical rather than becoming an easy universal escape.

Movement should have slight acceleration and deceleration. Polly should retain a sense of weight without feeling slippery.

---

## 5. Facing

Polly's facing direction changes from horizontal movement only.

Vertical motion does not change facing.

This avoids unnecessary directional sprite sets and keeps attack readability stable.

---

## 6. Sprint

Sprint is primarily for:
- traversal
- repositioning
- escaping pressure

For the first block prototype, sprinting into Light terminates into normal Light 1.

A bespoke running strike may be added later only if the base loop earns it.

---

## 7. Core light combo

The base combo is:

```text
LIGHT 1 → LIGHT 2 → LIGHT 3
```

Three deliberate strikes. No long mash chain.

### Light 1
Fast straight punch.

Purpose:
- check enemy
- initiate combo
- minimal commitment

Initial timing target:

```text
startup:   90 ms
active:    80 ms
recovery: 150 ms
```

Approximate total: 320 ms.

### Light 2
A more rotational continuation: hook, backhand or elbow-style strike.

Initial timing target:

```text
startup:  110 ms
active:    90 ms
recovery: 170 ms
```

Slightly stronger stagger than Light 1.

### Light 3
Combo finisher.

Potential final animation may be a hook, boot, shove or forearm depending on prototype feel.

Initial timing target:

```text
startup:  150 ms
active:   110 ms
recovery: 260 ms
```

Produces meaningful knockback and may contribute strongly to knockdown/stagger.

---

## 8. Combo input buffer

Input should be forgiving without allowing unlimited pre-queueing.

Initial input buffer:

**~180 ms**

If Light is pressed during the latter portion of the previous attack, the next combo strike queues.

Maximum queued actions:

**1**

---

## 9. Combo reset

If the player does not continue within the combo chain window, the sequence returns to Light 1.

Initial post-recovery reset target:

**~300 ms**

---

## 10. Heavy attack: guitar swing

The guitar heavy is Polly's signature commitment attack.

It provides:
- wider Y tolerance
- broad horizontal coverage
- stronger hitstop
- stronger knockback
- better crowd control
- greater vulnerability on whiff

Initial timing target:

```text
startup:  300 ms
active:   140 ms
recovery: 420 ms
```

Approximate total: 860 ms.

### Relative damage model

```text
Light 1 = 1.0
Light 2 = 1.1
Light 3 = 1.5
Heavy   = 2.8
```

Damage is relative during early tuning.

---

## 11. Hitstop

Initial targets:

- light hit: 35–50 ms
- light finisher: 55–70 ms
- guitar heavy: 90–120 ms
- KO heavy: up to approximately 130 ms

Hitstop is separate from hitstun.

---

## 12. Hitstun and knockback

Hitstun controls victim action lockout after contact.

Knockback primarily follows X direction, with optional small Y variation to avoid visually perfect stacks.

Relative knockback categories:

```text
Light 1      tiny
Light 2      tiny-medium
Light 3      medium
Heavy        large
KO heavy     large, exaggerated but controlled
```

---

## 13. Hit reactions

Minimum reaction set:

- light hurt
- heavy hurt
- knockback
- knockdown
- KO

For the block prototype these may initially be state/color/position changes rather than animation.

---

## 14. Hidden stagger / poise

Each hit adds hidden stagger pressure.

Initial relative values:

```text
Light 1 = 1
Light 2 = 1
Light 3 = 2
Heavy   = 4
```

Each enemy has stagger resistance.

Stagger pressure decays quickly when not being hit.

This prevents every enemy from becoming a permanent stun-lock victim while preserving Heavy as a crowd-control and interruption tool.

---

## 15. Cancel rules

Initial allowed chain:

- Light 1 → Light 2
- Light 2 → Light 3

Potential later chain:

- Light 1 or Light 2 → Heavy

Not allowed in first block prototype:

- Heavy → Light
- hurt reaction → attack
- arbitrary attack → movement cancellation

Commitment matters.

---

## 16. Pickups

`L` near a pickup initiates collection.

While holding a weapon:

- Light = weapon attack
- Heavy = stronger/contextual weapon action later
- Interaction = drop

Functional first-slice pickup weapons:

### Beer bottle
- quick
- short reach
- 2–3 durability hits
- final use breaks the bottle

### Mic stand
- slower
- long reach
- good lane coverage
- moderate knockback
- approximately 5–6 durability hits during early tuning

No inventory. Pickup → use → discard/break.

---

## 17. Collision model

Three separate concepts are mandatory:

1. **Body collision** — prevents exact overlap.
2. **Hurtbox** — where a character may be damaged.
3. **Hitbox** — where an attack can deal damage.

Sprite rectangles must not be used as the universal collision model.

Characters may softly push one another using simple local separation.

---

## 18. Shared enemy AI state machine

All first-slice enemy archetypes share the same top-level state taxonomy:

```text
SPAWN
IDLE
APPROACH
ALIGN
THREATEN
ATTACK
RECOVER
HURT
KNOCKBACK
DOWN
GETUP
KO
```

Archetypes vary through data and attack selection rather than separate AI architectures.

Key tuning dimensions:
- desired range
- aggression
- attack timing
- movement style
- recovery
- crowd pressure
- special behaviour

---

## 19. Enemy positioning

Enemies do not simply move directly toward Polly.

They attempt to achieve:

```text
desired horizontal distance
+
acceptable Y alignment
```

before attacking.

---

## 20. Crowd attack-token system

A hidden attack-token system limits simultaneous committed attacks.

Initial maximum:

**2 attack tokens**

Typical behaviour:
- one enemy attacks
- another threatens, aligns or repositions

Punk's charge may occasionally bypass this limit under controlled rules.

This keeps crowds active without creating unreadable simultaneous punishment.

---

# Enemy Archetype 1: Glam
## Working dev name: GLAMBO

### Tactical identity
**Bait and punish.**

The Glam enemy encourages the player to interrupt theatrical windups or wait through deceptive timing rather than mashing automatically.

### Desired range
Medium-close.

### Behaviour loop
1. approach
2. pause
3. theatrical windup
4. attack
5. long recovery / pose

### Primary move: Catwalk Backhand

Initial timing:

```text
anticipation:   420 ms
attack startup:  90 ms
active:         100 ms
recovery:       450 ms
```

The conspicuous anticipation is intentional and interruptible.

### Dodge
Occasional backward step when pressured.

- no invulnerability required initially
- cooldown prevents spam

### Taunt
May occur:
- between engagements
- if Polly remains distant
- never during immediate danger

The taunt creates a punish opening rather than functioning as filler only.

---

# Enemy Archetype 2: Prog Nerd
## Working dev name: ODDMETER

### Tactical identity
**Break predictable rhythm.**

The Prog enemy disrupts attack timing rather than overwhelming through raw aggression.

### Desired range
Medium.

### Primary move: Odd Meter Poke

Sequence:

windup → visible hold → attack

Initial timing:

```text
startup: 170 ms
hold:    180–420 ms bounded variation
active:   90 ms
recovery: 320 ms
```

The hold must be visually readable. Delay variation must be bounded rather than arbitrary.

### Optional slice special: Keytar Pulse

- short ranged waveform
- clear charge cue
- linear horizontal travel
- avoided primarily through Y movement

This special is optional for the earliest block prototype and should be added only after melee behaviour works.

---

# Enemy Archetype 3: Mohawk Punker
## Working dev name: RAMJET

### Tactical identity
**Pressure and displacement.**

The Punk has the highest aggression and shortest tactical decision time of the three initial archetypes.

### Approach
At medium distance the Punk frequently enters Rush state.

He aims toward Polly's current lane and closes distance aggressively.

### Primary move: Shoulder Charge

Initial timing:

```text
telegraph: 180 ms
charge:    350–600 ms
impact
miss recovery: ~500 ms
```

On hit:
- strong stagger

On miss:
- major punish window

### Crowd exception
The Punk may occasionally obtain an attack token for charge even when the normal attack-token pool is occupied.

This exception applies to the charge only.

---

## 21. Friendly collision

For the first prototype:

- enemies do not deal damage to one another
- Punk charge may physically shove another enemy

Actual enemy-on-enemy damage is reserved for a later faction such as Thrashers.

---

## 22. Health and invulnerability

### Player
- simple health bar
- no regeneration during active encounters

### Relative enemy health targets
- Glam: ~6 Light-1 damage units
- Prog: ~5
- Punk: ~6

### Knockdown invulnerability
Brief invulnerability around ground impact / early get-up transition.

Initial target:

**~350 ms**

This prevents degenerate pile-on combos against prone targets.

---

## 23. Camera

Horizontal camera follows Polly within a soft dead zone.

The camera only begins scrolling as Polly approaches dead-zone boundaries.

Vertical camera tracking should be minimal or absent during the first prototype.

### Polished combat response
- Light: none or extremely subtle shake
- Heavy: tiny positional impulse
- KO Heavy: moderate brief impulse

---

# The Rat Hole Alley Slice

Target size:

**approximately 3–4 screen widths**

Zones:

### Zone A
Club exit / free movement space.

### Zone B
Dumpster and poster section.

### Zone C
Wider combat arena.

### Zone D
Neon back entrance / exit trigger.

---

## 24. Opening

Polly exits the club into an empty space.

No text tutorial wall.

The player receives several seconds to naturally test movement, sprint and attack buttons.

A beer bottle is visible nearby.

---

## 25. Encounter 1: Pretty Problem

One Glam enemy.

Purpose:
- teach basic attacking
- teach obvious telegraph/recovery

Behaviour:
- slow approach
- large windup
- large recovery

---

## 26. Encounter 2: Wrong Time Signature

Start with one Prog enemy.

After a short delay or health threshold, add one Glam enemy.

Purpose:
- introduce odd timing
- introduce first multi-enemy pressure
- expose attack-token behaviour

---

## 27. Encounter 3: Somebody Started Something

A Punk rushes in quickly.

Final active composition target:

- 1 Punk
- 1 Glam
- 1 Prog

Maximum active enemies in the first slice:

**3**

A mic stand is present as an optional environmental weapon.

---

## 28. End condition

When the final enemy is KO'd:

1. combat ends
2. rain / club ambience becomes perceptually prominent again
3. Polly returns to idle
4. block prototype shows a simple completion state such as:

```text
SLICE COMPLETE
```

Potential diagnostic stats:
- completion time
- damage taken
- enemies KO'd

No grading/rank system yet.

---

## 29. Encounter rhythm

```text
QUIET
↓
simple fight
↓
breath
↓
timing problem
↓
crowd problem
↓
brief breath
↓
three-archetype brawl
↓
silence
```

Breathing room is intentional. Intensity requires contrast.

---

## 30. Audio integration direction

A final guitar heavy may layer:

1. cloth / arm whoosh
2. guitar resonance
3. body impact
4. low transient
5. restrained feedback sting on exceptional hits

The music should remain one continuous track with state layers such as:

```text
AMBIENT INTRO
COMBAT LOW
COMBAT HIGH
RESOLVE
```

Encounter 1 activates the low combat layer.
Encounter 3 may activate the full layer.
The final KO may transition into a feedback tail / decay.

---

## 31. Character power philosophy

Polly's power fantasy comes from **commitment**, not extreme speed.

She throws her body weight into attacks, fights imperfectly and uses environmental tools.

The guitar should look cumbersome because it is cumbersome.

This physical roughness is part of the game's grunge identity.

---

## 32. Enemy readability rule

Every enemy attack must communicate intent.

Difficulty should come from:
- overlapping intentions
- positioning
- timing
- pressure

not unreadable attacks.

---

## 33. Crowd rule

More enemies must not be treated as synonymous with more interesting difficulty.

The first slice caps concurrent enemies at three because differentiated interactions are more important than enemy count.

---

# SHITTY BLOCK DOUBLE DRAGON
## First implementation scope

The first playable implementation uses deliberately primitive geometry.

### Polly block
- move
- face
- sprint
- Light 1–3
- Heavy
- hurt
- health

### Enemy blocks
- Glam AI
- Prog AI
- Punk AI

### Shared combat systems
- hitboxes
- hurtboxes
- body collision
- lane tolerance
- hitstop
- hitstun
- knockback
- stagger
- attack tokens
- simple camera
- encounter triggers
- win condition

### Arena
Rectangles and primitive shapes only.

No production sprites are required to validate the combat skeleton.

---

## 34. Graduation criteria from Block Pass

The project does **not** graduate to production sprites merely because the code runs.

It graduates only when all of the following are true:

### Polly
- feels responsive

### Light combo
- feels naturally timed

### Heavy
- feels dangerous and satisfying

### Glam
- causes interrupt-or-wait decisions

### Prog
- causes rhythm reconsideration

### Punk
- causes repositioning

### Mixed crowd
- three enemies together remain challenging but readable

### Impact
- hits already feel weighty even with rectangles and placeholder FX

If hitting a pink rectangle with a red rectangle carrying a black rectangle labelled GUITAR feels good, the combat skeleton has passed.

---

## Canonical combat thesis

> **Polly is easy to operate. Enemies force decisions. Impact rewards commitment. Crowds create combinations rather than merely increasing numbers.**

Features intentionally deferred until the core loop earns them:

- block
- dodge roll
- jumping
- air combat
- specials/supers
- throws/grappling trees
- rage meters
- parries
- executions
- assists
- skill trees
