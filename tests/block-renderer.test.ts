import test from 'node:test';
import assert from 'node:assert/strict';
import { createWorld } from '../src/sim/world.js';
import { createEnemy } from '../src/sim/enemies.js';
import { blockDescriptors, strikeDescriptors } from '../src/render/blockRenderer.js';
import { startHeavy } from '../src/sim/player.js';

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

test('Polly heavy has ghosted guitar geometry during startup and solid segmented geometry when active', () => {
  const w=createWorld();
  startHeavy(w.polly);
  let shapes=strikeDescriptors(w);
  assert.equal(shapes.length,3);
  assert.ok(shapes.every(s=>s.phase==='TELEGRAPH'));
  w.polly.attack!.phase='ACTIVE';
  shapes=strikeDescriptors(w);
  assert.equal(shapes.length,3);
  assert.ok(shapes.every(s=>s.phase==='ACTIVE'));
  assert.ok(shapes.every(s=>s.shape==='GUITAR'));
});

test('enemy archetypes expose distinct telegraph geometry and live attack geometry', () => {
  const w=createWorld();
  const glam=createEnemy('GLAM'), prog=createEnemy('PROG'), punk=createEnemy('PUNK');
  glam.state='THREATEN'; prog.state='THREATEN'; punk.state='THREATEN';
  w.enemies=[glam,prog,punk];
  const telegraphs=strikeDescriptors(w);
  assert.ok(telegraphs.some(s=>s.actorId===glam.id && s.shape==='STRIKE' && s.phase==='TELEGRAPH'));
  assert.ok(telegraphs.some(s=>s.actorId===prog.id && s.shape==='WAVE' && s.phase==='TELEGRAPH'));
  assert.ok(telegraphs.some(s=>s.actorId===punk.id && s.shape==='RAM' && s.phase==='TELEGRAPH'));
  glam.state='ATTACK'; prog.state='ATTACK'; punk.state='ATTACK';
  const active=strikeDescriptors(w);
  assert.ok(active.filter(s=>s.phase==='ACTIVE').length>=3);
});
