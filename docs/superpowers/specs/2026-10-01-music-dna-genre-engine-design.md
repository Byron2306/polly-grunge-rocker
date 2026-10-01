# Music DNA Genre Engine Design

Date: 2026-10-01
Branch: `agent/music-dna-genre-engine`
Status: Design specification for review

## 1. Purpose

Polly's current Fusion Lab can author MIDI-like note events, route articulations, apply tone controls, render SFZ instruments, and mix stems. That is not enough to generate convincing genre music. The current system can label events `PALM_MUTE`, `THRASH_SKANK`, or set `distortion=6.8` while still producing a musically weak or sonically unconvincing result.

This subsystem introduces a symbolic **Music DNA** layer that learns and represents genre behavior numerically across the whole band, then constrains composition, performance, orchestration, and production against those learned distributions.

The goal is not to copy individual songs. The goal is to learn the structural grammar common to representative songs and generate novel material that occupies the same genre region.

Initial supported genre families:

- thrash metal
- black metal
- death metal
- doom metal
- punk
- glam metal
- progressive metal

Thrash is the first validation target because `host-003-chainsaw-diplomacy` already exposes failures in riff grammar, drum coupling, articulation routing, and production tone.

## 2. Non-goals

This phase does not:

- reproduce copyrighted songs, riffs, tabs, or notation verbatim;
- train an opaque generative neural network;
- replace the existing deterministic composition and rendering pipeline;
- require cloud inference;
- treat one band's style as the definition of a genre;
- hardcode a single fixed recipe per genre.

The engine stores distributions, feature ranges, and relationships. Individual reference tracks are observations, not templates.

## 3. Architecture

The system is divided into cooperating, independently testable components. Their boundaries follow responsibility rather than an arbitrary component count.

### 3.1 Corpus descriptors

A curated corpus stores metadata and extracted non-infringing musical features for reference tracks. Each record contains:

- genre and optional subgenre;
- artist and track identifiers for provenance only;
- tempo / tempo range;
- meter and meter-change data;
- tuning;
- phrase lengths;
- pitch-class and interval distributions;
- rhythmic subdivision distributions;
- articulation proportions;
- role-specific behavior for guitar, bass, drums, vocals, and keys where present;
- production descriptors such as gain class, cabinet requirement, stereo strategy, room amount, and gating style;
- evidence/source notes.

No complete copyrighted score, tab, lyric, or melody is persisted.

### 3.2 Symbolic performance model

The current `NoteEvent` remains the compatibility primitive, but the Music DNA layer adds richer performance semantics above it.

Proposed event types:

```python
@dataclass(frozen=True)
class GuitarPerformanceEvent:
    start_tick: int
    duration_ticks: int
    midi_note: int
    velocity: int
    string: int | None
    fret: int | None
    pick_direction: str | None
    palm_mute: float
    accent: float
    technique: str
    chord_shape: str | None
    phrase_role: str

@dataclass(frozen=True)
class BassPerformanceEvent:
    start_tick: int
    duration_ticks: int
    midi_note: int
    velocity: int
    technique: str
    lock_target: str | None
    phrase_role: str

@dataclass(frozen=True)
class DrumPerformanceEvent:
    start_tick: int
    duration_ticks: int
    midi_note: int
    velocity: int
    limb: str | None
    technique: str
    groove_role: str
    accent: float

@dataclass(frozen=True)
class VocalPerformanceEvent:
    start_tick: int
    duration_ticks: int
    pitch: int | None
    syllabic_density: float
    delivery: str
    phrase_role: str

@dataclass(frozen=True)
class KeyPerformanceEvent:
    start_tick: int
    duration_ticks: int
    midi_note: int
    velocity: int
    voicing_role: str
    articulation: str
```

These types express how a note is played and what structural function it serves. Conversion to the existing deterministic `NoteEvent` path occurs only after composition and performance validation.

### 3.3 Genre DNA profiles

Each genre profile stores distributions, not constants.

Top-level model:

```python
@dataclass(frozen=True)
class GenreDNA:
    id: str
    tempo: Distribution
    meters: Distribution
    harmony: HarmonyDNA
    guitar: GuitarDNA
    bass: BassDNA
    drums: DrumDNA
    vocals: VocalDNA
    keys: KeysDNA
    arrangement: ArrangementDNA
    production: ProductionDNA
```

Representative feature families:

#### Harmony DNA

- tonic/pedal ratio
- pitch-class histogram
- interval histogram
- chromaticity
- minor-second rate
- minor-third rate
- tritone rate
- perfect-fifth rate
- modal/scale-family weights
- chord-density and chord-type weights
- harmonic-change rate

#### Guitar DNA

- attack density
- palm-mute ratio
- tremolo ratio
- downpick ratio
- alternate-pick ratio
- gallop and reverse-gallop rates
- chord vs single-note ratio
- sustain distribution
- rest distribution
- string/fret locality
- phrase length
- motif repetition
- phrase-end mutation
- hook recurrence

#### Bass DNA

- guitar lock rate
- kick lock rate
- root/fifth bias
- octave usage
- melodic independence
- fill probability
- pick/finger technique distribution
- sustain distribution

#### Drum DNA

- kick density
- snare/backbeat placement
- skank probability
- blast probability
- double-kick density
- half-time probability
- cymbal subdivision
- fill frequency
- fill length
- guitar-kick coupling
- transition density

#### Vocal DNA

- syllable density
- phrase length
- pitch-range distribution
- harsh/clean delivery weights
- sustain probability
- gang-vocal probability
- call/response probability
- chorus-hook recurrence

#### Keys DNA

- presence probability
- pad/countermelody/lead/unison roles
- harmonic-extension rate
- rhythmic independence

#### Arrangement DNA

- common section lengths
- intro/verse/chorus/bridge/solo probabilities
- riff reuse across sections
- contrast between sections
- density arcs
- transition types
- solo placement
- breakdown / half-time / atmospheric section probability

#### Production DNA

- tuning distribution
- pitch-shift policy
- pickup/sample-source family
- boost/overdrive class
- preamp gain range
- distortion topology class
- amp EQ ranges
- cabinet/IR requirement
- mic/IR voicing family
- gate strength
- double-track policy
- stereo width
- bass saturation
- drum room amount
- reverb ranges
- master loudness target band

## 4. Initial genre grammar

The first seven DNA profiles are initialized from the researched corpus, then remain editable as the corpus grows.

### 4.1 Thrash

Core identity:

- fast tempo distribution, generally around 175–225 BPM for the aggressive reference set;
- high low-string pedal-note use;
- high palm-mute and downpick probability;
- straight eighths, sixteenth bursts, gallops, reverse gallops;
- chromatic neighbors, minor seconds, minor thirds, tritones, power chords;
- one-to-four-bar memorable riff motifs;
- phrase-end mutation and turnarounds;
- selective kick reinforcement of guitar attacks;
- strong snare/backbeat or skank feel;
- double-kick bursts, not constant mandatory double kick;
- near-zero blast-beat prior for classic thrash;
- audible picked bass with frequent riff lock;
- real distorted amp/cabinet chain with strong pick articulation and no modern djent-style hard gate by default.

### 4.2 Black metal

Core identity:

- high tremolo-picking density;
- low palm-mute probability;
- longer melodic/harmonic arcs than thrash;
- minor/modal motion, semitone tension, parallel interval movement, arpeggiated harmony;
- sustained note-stream texture rather than pedal-stab architecture;
- high blast/double-kick priors with half-time contrast;
- bass commonly follows harmonic motion but may sustain more than guitar;
- raw or atmospheric production profiles with less low-end surgery and lower hard-gate prior.

### 4.3 Death metal

Core identity:

- high chromaticity and dissonance;
- strong minor-second, minor-third, tritone, and perfect-fifth usage;
- lower tuning prior than classic thrash;
- mix of palm-muted attacks, tremolo, gallops, triplets, abrupt rests, and slams;
- high double-kick and blast priors;
- abrupt transitions between high-density and half-time material;
- bass may be riff-locked or highly independent depending on substyle;
- production subprofiles for Florida-style definition and Stockholm-style buzzsaw saturation.

### 4.4 Doom metal

Core identity:

- low note density and long sustain;
- slow harmonic-change rate;
- power chords, minor thirds, tritones, minor seconds;
- strong use of space as a compositional feature;
- sparse kick and large snare/cymbal decay;
- audible bass with sustain/fuzz and melodic fills;
- production favors low-mid weight, fuzz/tube saturation, speaker/cabinet character, room, and weak gating.

### 4.5 Punk

Core identity:

- predominantly 4/4;
- fast eighth-note drive;
- very high downstroke prior;
- simple power-chord / triadic harmony;
- short one-to-four-bar phrases;
- high hook repetition and low solo prior;
- simple backbeat drums with short fills;
- bass ranges from root-heavy lock to melodic counter-motion depending on substyle;
- vocals emphasize short high-density phrases and repeated hooks.

### 4.6 Glam metal

Core identity:

- hook strength is a first-class metric;
- moderate riff complexity and high harmonic clarity;
- power chords, pentatonic/blues vocabulary, double stops, octaves, open-chord movement;
- lead guitar has high bend/vibrato/legato/shred-burst probability but must resolve melodically;
- bass often locks to kick/root/fifth structure;
- huge 4/4 backbeat and chorus crashes;
- high chorus-vocal hook and harmony-stack priors;
- production favors real amp/cabinet guitar, wide doubled rhythm guitars, large snare, lead delay/chorus, and strong stereo width.

### 4.7 Progressive metal

Core identity:

- meter-change and odd-grouping probability are high;
- motif transformation is high;
- clean/distorted contrast is common;
- longer phrase structures and greater harmonic complexity;
- bass and drums have higher rhythmic independence;
- keys may act as pads, counterpoint, leads, unison lines, or harmonic extension;
- production profile is substyle-dependent and must not be collapsed into one fixed tone.

## 5. Cross-instrument coupling

Genre identity cannot be validated one stem at a time.

The engine must calculate relational features.

Required coupling metrics:

- guitar-to-kick coincidence ratio;
- bass-to-guitar onset lock;
- bass-to-kick onset lock;
- snare placement relative to guitar phrase accents;
- cymbal density relative to guitar subdivision density;
- vocal phrase boundaries relative to riff/section boundaries;
- keys-to-guitar harmonic agreement or deliberate tension;
- section density contrast across the whole band.

Example: a thrash riff with correct pitch vocabulary but quarter-note kick plodding receives a low thrash score even if the guitar alone looks valid.

## 6. Hook and catchiness model

Catchiness must be measurable enough to reject mechanically correct but forgettable riffs.

The first deterministic hook score combines:

- motif recurrence within 2–8 bars;
- rhythmic fingerprint uniqueness;
- controlled repetition;
- phrase-end mutation;
- accent recurrence;
- pitch-contour recurrence;
- rest-pattern recurrence;
- contrast between core motif and turnaround.

The engine must penalize:

- exact short-cycle repetition across long sections;
- uniform attack density;
- phrases with no stable motif;
- random mutation that destroys motif identity.

Hook scoring is a heuristic, not a claim about human aesthetic value. It is used as a compositional guardrail.

## 7. Genre distance and validation

Each generated section receives a feature vector. The engine compares it against the selected genre profile.

Outputs:

```text
ALLOW
MUTATE
REJECT
```

Suggested initial logic:

- `ALLOW`: all hard constraints pass and weighted normalized distance is inside the configured acceptance band;
- `MUTATE`: no hard contradiction, but one or more high-weight genre features are outside preferred ranges;
- `REJECT`: hard contradictions such as missing required cabinet for a validated metal production profile, impossible instrument mapping, or feature distance well outside the genre envelope.

The validator reports *why* a candidate missed the genre instead of returning a single opaque score.

Example:

```json
{
  "state": "MUTATE",
  "genre": "THRASH_CLASSIC",
  "reasons": [
    "riff_hook_recurrence_below_range",
    "guitar_kick_coupling_below_range",
    "palm_mute_ratio_below_range"
  ]
}
```

## 8. Genre blending

Genre blends operate on feature distributions and coupling rules, not text labels.

Example request:

```text
60% thrash + 25% black metal + 15% progressive metal
```

may yield:

- thrash pedal-note rhythmic architecture;
- black-metal melodic tremolo contour in selected sections;
- progressive phrase-length and meter mutations;
- corresponding changes to drum density, bass independence, keys, and production.

Blending must preserve hard compatibility rules. Incompatible features are resolved explicitly rather than averaged blindly.

## 9. Production truth

The existing tone controls remain useful but are not sufficient to claim authentic metal production.

For distorted guitar profiles that require amp/cabinet tone, the validated signal path is conceptually:

```text
source DI / sample
  -> tuning / pitch policy
  -> articulation shaping
  -> boost / overdrive
  -> preamp saturation
  -> amp EQ / presence
  -> optional power-stage shaping
  -> cabinet / IR
  -> mic / post-EQ shaping
  -> per-performance L/R treatment
  -> guitar bus
```

Rules:

- input volume is not equivalent to amplifier gain;
- a generic tanh soft clip is not sufficient to satisfy an `amp_distortion_required` profile;
- cabinet/IR becomes a hard requirement for genre profiles that demand a conventional amplified-guitar sound;
- palm-muted performance must have distinct transient/envelope behavior from sustained articulation;
- double tracks must represent two performance variants rather than one identical render duplicated left/right;
- render manifests record the actual production topology used.

The production validator may refuse rendering when a requested DNA profile cannot be produced truthfully with installed assets.

## 10. Corpus ingestion

The first implementation supports manually curated feature observations and machine-readable symbolic inputs.

Accepted source forms:

- MIDI where legally usable;
- MusicXML where legally usable;
- user-owned or permissively licensed tablature converted into events;
- manually entered aggregate observations from published lessons/analyses;
- existing Polly compositions.

Future optional parsers may read Guitar Pro or other symbolic formats only when legally and technically appropriate.

The ingestion pipeline extracts aggregate features and stores provenance. It does not store or emit full copyrighted third-party notation.

## 11. Proposed repository layout

```text
fusion_lab/
  music_dna/
    __init__.py
    model.py
    distributions.py
    feature_extractors.py
    coupling.py
    hook_score.py
    validator.py
    blend.py
    corpus.py
    genre_profiles.py
    performance.py
    production_truth.py

  data/music_dna/
    corpus.json
    genres/
      thrash.json
      black_metal.json
      death_metal.json
      doom_metal.json
      punk.json
      glam_metal.json
      progressive_metal.json

  tests/
    test_music_dna_model.py
    test_music_dna_features.py
    test_music_dna_coupling.py
    test_music_dna_hook_score.py
    test_music_dna_validator.py
    test_music_dna_blend.py
    test_music_dna_production_truth.py
    test_chainsaw_music_dna.py
```

Existing modules remain consumers/producers around this subsystem rather than being rewritten wholesale.

## 12. Chainsaw Diplomacy validation path

`host-003-chainsaw-diplomacy` is the first end-to-end acceptance target.

The validation sequence is deliberately staged:

1. Generate or transform the symbolic composition under `THRASH_CLASSIC` DNA.
2. Validate guitar feature vector before rendering.
3. Validate bass and drum vectors.
4. Validate guitar/bass/drum coupling.
5. Validate hook score and phrase mutation.
6. Render isolated rhythm guitar through a truthful production chain.
7. Compare isolated guitar metrics against the accepted thrash control band.
8. Only after the guitar passes, render bass and drums.
9. Render the full instrumental.
10. Require a final human authenticity review before promotion.

This prevents another full-length render from hiding a broken guitar or broken groove behind a successful pipeline status.

## 13. Tests and acceptance criteria

The implementation is complete only when all of the following are automated.

### Data/model tests

- genre profiles deserialize deterministically;
- all probabilities/ranges are bounded;
- distributions reject invalid values;
- provenance is retained;
- feature extraction is deterministic for a fixed input.

### Musical feature tests

- known synthetic thrash fixture produces high pedal/downpick/palm-mute features;
- known synthetic black-metal fixture produces high tremolo and low palm-mute features;
- known doom fixture produces low density/high sustain;
- known prog fixture detects odd grouping/meter changes;
- motif repetition and mutation are distinguishable.

### Coupling tests

- kick/riff lock is measured from actual event timing;
- bass/guitar and bass/kick relationships are measured separately;
- unrelated dense drum patterns cannot pass simply because event counts are high.

### Production truth tests

- distorted metal guitar profile can require amp-stage and cabinet evidence;
- `cabinet_ir=None` fails a profile that declares cabinet mandatory;
- pure input gain + generic soft clip cannot satisfy amp truth;
- palm-mute and sustain routes must be measurably distinct or rendering is refused;
- L/R performance identity must differ while preserving riff identity.

### Chainsaw acceptance

For the first thrash reference host:

- composition must pass `THRASH_CLASSIC` DNA or return explicit mutation reasons;
- no fixed three-bar repetition loop across a long section;
- hook recurrence and phrase-end mutation both exceed configured minimums;
- kick/riff coupling is inside the thrash profile band;
- palm-muted and sustained rhythm events are audibly/non-trivially different at the render level;
- production manifest proves amp/cabinet topology when required;
- isolated rhythm-guitar render is reviewed before full-mix render;
- full suite remains green.

## 14. Observability

Every generated host gets a `music-dna-report.json` alongside the production manifest.

Minimum fields:

```json
{
  "genre_profile": "THRASH_CLASSIC",
  "feature_vector": {},
  "coupling": {},
  "hook_score": {},
  "production_truth": {},
  "decision": "ALLOW|MUTATE|REJECT",
  "reasons": []
}
```

This report is deterministic and suitable for regression testing.

## 15. Rollout order

Implementation proceeds in this order:

1. core data model and distributions;
2. feature extraction from current `HostComposition` / `NoteEvent` structures;
3. seven seed genre profiles;
4. coupling metrics;
5. hook/motif metrics;
6. validator and explainable decisions;
7. genre blending;
8. production-truth validator;
9. richer performance event model and conversion adapters;
10. Chainsaw thrash integration;
11. isolated guitar acceptance path;
12. full render integration.

The first useful milestone is reached at step 6: existing compositions can already be classified and rejected/mutated according to whole-band genre DNA before changing the renderer.

## 16. Success condition

The subsystem succeeds when Polly can explain, numerically and reproducibly, why two superficially similar fast metal compositions belong to different genre regions, and can use those distinctions to create and validate new whole-band material.

For Chainsaw Diplomacy specifically, success means the system no longer accepts a render merely because it is 192 BPM, contains notes labeled `PALM_MUTE`, and has a parameter named `distortion`. It must demonstrate the rhythmic, harmonic, cross-instrument, performance, and production traits of thrash before the render is promoted.
