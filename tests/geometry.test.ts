import test from 'node:test';
import assert from 'node:assert/strict';
import { overlaps, withinLane, meleeContact } from '../src/sim/geometry.js';
import { STANDARD_LANE_TOLERANCE } from '../src/sim/constants.js';

test('rectangles overlap at touching edges and geometry is explicit', () => {
  const a = { x: 0, y: 0, width: 10, height: 10 };
  const b = { x: 10, y: 2, width: 4, height: 4 };
  assert.equal(overlaps(a, b), true);
});

test('lane tolerance is inclusive at 24 and rejects beyond it', () => {
  assert.equal(STANDARD_LANE_TOLERANCE, 24);
  assert.equal(withinLane(100, 124, STANDARD_LANE_TOLERANCE), true);
  assert.equal(withinLane(100, 124.01, STANDARD_LANE_TOLERANCE), false);
});

test('x overlap alone cannot produce melee contact across lanes', () => {
  const hit = { x: 0, y: 0, width: 40, height: 20 };
  const hurt = { x: 10, y: 0, width: 20, height: 20 };
  assert.equal(meleeContact(hit, hurt, 100, 140, 24), false);
  assert.equal(meleeContact(hit, hurt, 100, 120, 24), true);
});
