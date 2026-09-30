# Polly Grunge Rocker — Style Trait / Function Separation

**Date:** 2026-09-30  
**Status:** DESIGN LOCK  
**Applies to:** Pattern Map combat, recruit identity, fusion, teaching, compatibility and later audio realization.

## Canonical Rule

> **Stylistic trademark does not have to equate to convergent function.**

A musician's recognizable stylistic identity and the compositional job that identity performs in a particular moment are separate concepts.

The system must therefore not encode a genre trademark as one fixed musical function.

Examples:

- tremolo picking is not inherently a phrase ending, tension device, minor-key device or Black-Metal-only function;
- a pinch harmonic is not inherently a slam ending; it may act as punctuation, climax, melodic material, release or sustained color;
- D-beat is not inherently a main groove; it may provide propulsion, section lift, post-blast release or transition drive;
- Doom sustain is not inherently resolution; it may be an anchor, drone, tension floor, atmosphere, harmonic bed or contrast layer;
- a tritone is not inherently an "evil" function; context, duration, voicing, register, timbre and resolution behavior determine its musical effect;
- Prog identity is not reducible to odd meter or virtuosity; timbral experimentation, re-orchestration, unusual sound sources and role reassignment are first-class stylistic vocabulary.

## Separation of Concerns

The model must distinguish at least these dimensions:

### Style Trait

What makes a musician recognizably themselves.

Examples:

- tremolo articulation;
- pinch harmonic attack;
- D-beat groove vocabulary;
- blast-beat vocabulary;
- thumb/slap articulation;
- sustained Doom chord bloom;
- pedal/drone voicing;
- raw/tinny drum timbre;
- Mellotron-like choir texture;
- unusual synth or found-sound texture.

### Placement

Where the contribution occurs in the Pattern Map.

Examples:

- phrase start;
- phrase end;
- transition;
- fill window;
- resolution;
- cross-layer alignment;
- sustained section bed;
- role-local cycle;
- convergence point.

### Function

What compositional job the contribution performs in this specific context.

Examples:

- melody;
- counterline;
- harmonic bed;
- tension;
- resolution;
- propulsion;
- groove restoration;
- punctuation;
- transition;
- atmosphere;
- anchor;
- destabilization;
- section lift;
- contrast;
- convergence setup.

### Context

The host conditions under which the expression occurs.

Examples:

- host harmony;
- tempo;
- meter;
- subdivision;
- section;
- density;
- register;
- role occupancy;
- other active layers;
- current coherence;
- genre familiarity;
- learned pattern relationships.

### Expression

The actual result selected for playback/behavior.

Conceptually:

```text
STYLE TRAIT
+ PLACEMENT
+ FUNCTION
+ CONTEXT
= EXPRESSION
```

## Consequence for Learning

Knowledge must not collapse to "knows technique".

A recruit learns relationships between a stable stylistic trait and new functional/contextual uses.

Conceptually:

```text
knowledge = learned(trait × function × context)
```

Example:

```text
TREMOLO_TEXTURE × MELODIC_FILL × GLAM_PHRASE_END
TREMOLO_TEXTURE × HARMONIC_BED × DOOM_SECTION
TREMOLO_TEXTURE × COUNTERLINE × PROG_POLYMETER
```

The recruit keeps the same trademark while learning additional jobs for it.

This is a primary mechanism for growth without homogenizing musician identity.

## Consequence for Compatibility

Compatibility must be evaluated between an expression and its current musical context, not between genre labels alone.

A technique that clashes in one function may fit perfectly in another.

For example, sustained Black-Metal tremolo may overwhelm a Glam hook when used as rhythm-guitar replacement, while the same articulation may work as a brief counterline or upper-voice texture without damaging host identity.

Similarly, a Doom sustain may be native as a harmonic bed but disruptive as constant foreground punctuation.

## Consequence for the Pattern Map

The Pattern Map answers **where** and describes structural opportunity.

It must not hard-code one stylistic trademark to one semantic function.

Later technique/opportunity systems should be able to evaluate:

```text
what trait is available?
where is the opportunity?
what function is useful here?
what host context constrains it?
what expression preserves coherence?
```

## Consequence for Fusion Lab Research

Fusion experiments must isolate dimensions rather than treating a genre as one indivisible stereotype.

Useful independent variables include:

- articulation;
- rhythmic density;
- local pattern length;
- voicing;
- harmonic relationship to host;
- register;
- timbre;
- sustain/decay;
- role assignment;
- placement;
- function;
- duration/density of guest expression.

A/B/C experiments should therefore test not only "genre X inside genre Y" but specific trait/function/context combinations.

## Locked Design Laws

1. **STYLE ≠ FUNCTION.**
2. **GENRE ≠ ONE FIXED TECHNIQUE BUNDLE.**
3. **INTERVAL ≠ EMOTION.** Context determines effect.
4. **ARTICULATION, TIMBRE, VOICING, RHYTHM AND HARMONY ARE SEPARABLE TRAIT AXES.**
5. **A MUSICIAN CAN KEEP THEIR STYLE WHILE LEARNING NEW FUNCTIONS.**
6. **THE HOST PROVIDES STRUCTURAL CONTEXT; THE RECRUIT PROVIDES PERSONAL EXPRESSION.**
7. **PATTERN MAP OPPORTUNITY DOES NOT PREDETERMINE THE ONLY VALID STYLE TREATMENT.**
8. **FUSION COMPATIBILITY IS CONTEXTUAL, NOT A GENRE-PAIR LOOKUP TABLE.**

## Canonical Summary

> **The song tells you where. The musician tells you how. The situation tells you why.**

This amendment supersedes any earlier reading of the architecture that implies a stylistic trademark has one fixed compositional function.
