# Rat Hole Production Map

## Locked visual language

Rat Hole is Polly's Grunge home turf. The environment uses dense painterly pixel art:
wet asphalt, practical amber/red/cyan light, layered masonry, battered metal, posters,
pipes, fences, cases, bins, rain, steam and irregular reflections.

Flat vector-like walls, icon-like props, clean procedural rectangles and large dead
untextured areas are not production art.

## Zone progression

- Zone 1 — club entrance / home-scene arrival: red Rat Hole neon, warm practical light,
  dense posters, dumpster, crates and wet reflective street.
- Zone 2 — service/rehearsal alley: colder cyan service light, fencing, vents, pipes,
  utility architecture and deeper spatial recession.
- Zone 3 — backstage/loading threshold: red/violet intensity, shutters, flight cases,
  loading clutter and the densest final-arena silhouette.

## Runtime layers

Each zone owns three registered 960×540 layers:

- FAR: remote skyline / upper architecture / atmosphere, behind actors.
- MID: primary venue architecture and the main street/gameplay surface, behind actors.
- NEAR: transparent presentation-only framing elements above actors.

The NEAR layer must leave the active combat center mostly transparent. It never owns
collision and never changes the accepted walk band.

World anchors remain 0, 850 and 1700.
