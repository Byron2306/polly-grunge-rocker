import test from 'node:test';
import assert from 'node:assert/strict';
import { createPolly, updatePolly } from '../src/sim/player.js';
import { SPRINT_RATIO, VERTICAL_SPEED_RATIO, WALK_SPEED } from '../src/sim/constants.js';
const idle = { moveX:0, moveY:0, sprint:false, lightPressed:false, heavyPressed:false,interactPressed:false };

test('Polly movement preserves spec ratios and vertical-only motion preserves facing', () => {
  const p = createPolly();
  updatePolly(p, {...idle, moveX:1}, 1000);
  assert.ok(p.velocity.x > 0 && p.velocity.x <= WALK_SPEED);
  const walk = p.velocity.x;
  updatePolly(p, {...idle, moveX:1, sprint:true}, 1000);
  assert.equal(Math.round(p.velocity.x), Math.round(WALK_SPEED * SPRINT_RATIO));
  p.velocity.x = 0; p.velocity.y = 0; p.facing = -1;
  updatePolly(p, {...idle, moveY:1}, 1000);
  assert.equal(Math.round(p.velocity.y), Math.round(WALK_SPEED * VERTICAL_SPEED_RATIO));
  assert.equal(p.facing, -1);
  assert.ok(walk <= WALK_SPEED);
});

test('movement acceleration and deceleration are bounded rather than teleporting velocity', () => {
  const p = createPolly();
  updatePolly(p, {...idle, moveX:1}, 16);
  assert.ok(p.velocity.x > 0 && p.velocity.x < WALK_SPEED);
  const before = p.velocity.x;
  updatePolly(p, idle, 16);
  assert.ok(p.velocity.x >= 0 && p.velocity.x < before);
});
