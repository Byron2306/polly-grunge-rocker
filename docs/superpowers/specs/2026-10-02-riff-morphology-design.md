# Riff Morphology and Physical Gesture Design

## Purpose

Music DNA currently measures local note-density and articulation statistics well enough to distinguish broad genre envelopes, but Chainsaw Diplomacy exposed a deeper failure: a song can satisfy thrash ratios while still sounding repetitive because multiple bars are only cosmetic permutations of one riff sentence.

The engine needs to represent and reason about **distinct riff identities**, the **physical gesture** each riff is intended to produce, and the **transitions** between riff families. This must be genre-specific rather than a universal verse/chorus law.

## Goals

1. Represent a riff as a morphological object rather than a bag of notes.
2. Detect when two bars are the same riff family despite transposition or cosmetic note changes.
3. Detect when a song spends too long in one riff family.
4. Let genre profiles express structural priors without forcing every genre into conventional hook/chorus form.
5. Refactor Chainsaw Diplomacy to use multiple genuinely distinct thrash riff families with different physical behaviors.
6. Keep human-performed vocals external to synthesis. Polly may expose phrasing windows and intensity targets, but does not synthesize or imitate a named vocalist.

## Non-goals

- Copying notes, tabs, or melodies from Havok, Power Trip, Slayer, or any other reference track.
- Generating vocals.
- Building a universal music-theory ontology in this phase.
- Replacing existing symbolic feature extraction, hook scoring, or genre profiles.

## Riff morphology model

Create a focused `fusion_lab/music_dna/riff_morphology.py` module.

A `RiffSignature` represents one bar or phrase cell with these normalized features:

- `pedal_anchor`: dominant root/pedal pitch class or `None`
- `pitch_contour`: relative interval sequence between onset roots
- `onset_pattern`: onset positions normalized to one bar
- `rest_pattern`: gaps between sounding events
- `accent_pattern`: velocity accents normalized into low/medium/high buckets
- `articulation_pattern`: ordered semantic articulation classes
- `density`: onset density normalized 0..1
- `cadence_shape`: final quarter-bar behavior, including release/chromatic/held/empty

Pitch values are relative to the first/root anchor so transposing a riff does not create a fake new family.

A `RiffFamily` groups bars whose signatures are sufficiently close across rhythm, contour, cadence, and articulation. Similarity must weight rhythm and cadence more heavily than absolute pitch.

## Physical gesture

Each riff family receives one declarative gesture label:

- `STOMP`: spacious, syncopated, large landing accents, suited to mosh/half-time behavior
- `SPRINT`: dense downpicked/galloped propulsion
- `PANIC`: chromatic or tritone movement with unstable rhythmic pressure
- `HOOK`: memorable recurring anchor with clear cadence and callback value
- `TRANSITION`: one- or two-bar connective material whose job is to redirect energy
- `TRANCE`: sustained/repetitive texture where long repetition is intentional

Gesture labels are descriptive composition metadata. They are not genre labels and are not inferred as emotional judgments.

## Song-level morphology metrics

Add these explainable metrics to Music DNA reports:

- `riff_family_count`
- `riff_family_recurrence`
- `longest_same_family_run_bars`
- `section_riff_contrast`
- `transition_density`
- `gesture_diversity`

For deterministic analysis, family assignment must use stable ordering and deterministic thresholds.

## Genre structural priors

Genre profiles gain an optional `riff_structure.features` block. Existing profiles remain valid when the block is absent.

For `THRASH_CLASSIC`, seed preferred ranges that reward several distinct riff identities, limited same-family runs, meaningful transitions, and at least two physical gestures. These values are guards, not prescriptions for exact song form.

For `BLACK_METAL`, seed a contrasting profile that permits longer same-family runs, lower transition density, and `TRANCE` as a valid dominant gesture. Conventional hooks, solos, and chorus structure are explicitly not required by this layer.

The profile system must therefore distinguish **genre-specific structural grammar** from global correctness.

## Chainsaw Diplomacy refactor

Replace the current `_riff_for_bar(base, variant)` plus section variant tables with explicit riff-family composers. Keep the existing successful tone/articulation stack.

Chainsaw should contain at least five riff families with distinct jobs:

1. `A_HOOK`: recognizable E-pedal hook with memorable upper movement and a strong cadence.
2. `B_SPRINT`: continuous downpicked/galloped forward motion with fewer chord-stab resets.
3. `C_STOMP`: spacious half-time/syncopated bridge material with large chord landings.
4. `D_PANIC`: chromatic/tritone attack with reduced pedal dependence.
5. `E_TRANSITION`: short connective cells that redirect into another family and are not looped as a main riff.

Target section flow:

- intro: A
- verse1: A -> B
- pre: D -> B
- chorus1: A' -> C
- verse2: B -> D
- chorus2: A' -> C'
- solo backing: B / D
- bridge: C -> E
- final chorus: A' -> B -> C
- outro: D -> E

The exact notes remain original to Chainsaw. Prime directive: sections must feel physically different, not merely numerically different.

## Drum and bass coupling

Riff families expose their gesture to accompaniment generation.

- `SPRINT`: kick follows propulsion anchors and supports gallop/downpick motion.
- `STOMP`: kick/snare emphasize sparse landing points and leave space between them.
- `PANIC`: drums may increase accent displacement or short double-kick bursts.
- `TRANSITION`: fills are allowed to trigger or answer the transition rather than merely occur at fixed section ends.

Bass continues to follow riff roots but may use fills at family boundaries. Existing audibility calibration remains mandatory.

## Lead behavior

The lead remains subordinate to riff-family structure. It must not become a generic scalar layer.

- Solo backing should use B/D families rather than a repeated hook loop.
- Lead phrases should use rests, sustained notes, and bounded register.
- The existing lead-believability tests remain in force.

## Vocal handoff

Vocals are human-performed. Music DNA may emit per-window metadata such as:

- `delivery`: bark / sustained shout / syncopated shout / call-response
- `density_target`
- `attack_alignment`: riff onset / snare backbeat / offbeat
- `intensity`: 0..1

This metadata should describe delivery mechanics, not imitate a named person. Existing `VocalWindow` objects remain the starting point; implementation of richer vocal metadata is deferred unless needed for Chainsaw's next vocal pass.

## Truth gates

For `THRASH_CLASSIC`, Chainsaw must refuse or mutate when:

- fewer than the configured minimum distinct riff families are present
- one riff family exceeds the configured longest-run threshold
- section riff contrast is too low
- transition density is too low
- gesture diversity is too low

Existing feature gates for gallop rate, downpick ratio, harmony, drums, bass fills, and production truth remain active.

## Compatibility

- Existing genre JSON without `riff_structure` continues to load unchanged.
- Existing analysis payload keys remain stable; new metrics are additive.
- Existing songs that do not supply explicit gesture metadata are analyzed from morphology only and may report `UNKNOWN` gesture rather than fail.
- No new runtime dependency is introduced.

## Verification

Required tests:

1. Transposed copies of one riff resolve to the same riff family.
2. Rhythmically/cadentially distinct riffs resolve to different families even when they share the same pedal note.
3. A deliberately repetitive song reports a long same-family run and low section contrast.
4. A multi-riff thrash fixture reports at least the configured family count and gesture diversity.
5. Black-metal fixture with long `TRANCE` repetition remains valid under the black-metal profile.
6. Chainsaw remains inside the full `THRASH_CLASSIC` envelope after the refactor.
7. Chainsaw contains A/B/C/D/E family coverage and no main family is held beyond the configured run limit.
8. Existing Music DNA and production gauntlets remain green.

## Success criterion

A listener should be able to hear Chainsaw move between distinct physical behaviors: hook, sprint, stomp, panic, and transition. The engine should be able to explain that difference numerically without mistaking transposition for novelty or treating long-form black-metal repetition as a universal defect.
