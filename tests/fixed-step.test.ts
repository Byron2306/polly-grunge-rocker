import test from 'node:test';
import assert from 'node:assert/strict';
import { FixedStepClock } from '../src/sim/fixedStep.js';

test('fixed step preserves remainder and caps catch-up work', () => {
  const clock = new FixedStepClock(1000 / 60, 5);
  let ticks = 0;
  const first = clock.advance(10, () => ticks++);
  assert.equal(first, 0);
  assert.equal(ticks, 0);
  const second = clock.advance(10, () => ticks++);
  assert.equal(second, 1);
  assert.equal(ticks, 1);
  const stalled = clock.advance(1000, () => ticks++);
  assert.equal(stalled, 5);
  assert.equal(ticks, 6);
  assert.ok(clock.remainderMs >= 0 && clock.remainderMs < clock.stepMs);
});
