import test from 'node:test';
import assert from 'node:assert/strict';
import { createWorld } from '../src/sim/world.js';
import { createEnemy } from '../src/sim/enemies.js';
import { blockDescriptors } from '../src/render/blockRenderer.js';

test('block renderer gives each archetype distinct color/label and derives depth from ground anchor without mutation', () => {
  const w=createWorld(); w.enemies=[createEnemy('GLAM'),createEnemy('PROG'),createEnemy('PUNK')];
  w.polly.position.y=330; w.enemies[0].position.y=300; w.enemies[1].position.y=340; w.enemies[2].position.y=320;
  const before=JSON.stringify({p:w.polly.position,es:w.enemies.map(e=>e.position)});
  const blocks=blockDescriptors(w);
  assert.deepEqual(blocks.map(b=>b.label),['POLLY','GLAM','PROG','PUNK']);
  assert.equal(new Set(blocks.map(b=>b.color)).size,4);
  assert.deepEqual(blocks.map(b=>b.depth),[330,300,340,320]);
  assert.equal(JSON.stringify({p:w.polly.position,es:w.enemies.map(e=>e.position)}),before);
});
