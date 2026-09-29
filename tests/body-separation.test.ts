import test from 'node:test';
import assert from 'node:assert/strict';
import { createPolly } from '../src/sim/player.js';
import { createEnemy } from '../src/sim/enemies.js';
import { separateBodies } from '../src/sim/world.js';

test('body separation resolves overlap softly and preserves lane anchors', () => {
  const p=createPolly(); const e=createEnemy('GLAM');
  p.position={x:100,y:300}; e.position={x:100,y:300};
  separateBodies([p,e]);
  assert.ok(Math.abs(p.position.x-e.position.x)>0 || Math.abs(p.position.y-e.position.y)>0);
  assert.ok(Math.abs(p.position.x-100)<40); assert.ok(Math.abs(e.position.x-100)<40);
  assert.ok(Number.isFinite(p.position.y)&&Number.isFinite(e.position.y));
});
