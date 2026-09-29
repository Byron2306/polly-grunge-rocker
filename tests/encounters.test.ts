import test from 'node:test';
import assert from 'node:assert/strict';
import { createWorld } from '../src/sim/world.js';
import { createRatHoleEncounter, updateEncounter } from '../src/sim/encounters.js';

function koAll(w:ReturnType<typeof createWorld>){ for(const e of w.enemies){e.hp=0;e.state='KO';} }

test('opening free movement precedes encounter one and zone clear enters MOVE1', () => {
  const w=createWorld(), enc=createRatHoleEncounter();
  updateEncounter(w,enc,500); assert.equal(w.enemies.length,0); assert.equal(enc.stage,'OPENING');
  updateEncounter(w,enc,600); assert.equal(enc.stage,'E1'); assert.equal(w.enemies.length,1); assert.equal(w.enemies[0].kind,'GLAM');
  koAll(w); updateEncounter(w,enc,16); assert.equal(enc.stage,'MOVE1'); assert.equal(w.enemies.length,0);
});

test('MOVE1 requires Polly to travel right before encounter two spawns', () => {
  const w=createWorld(), enc=createRatHoleEncounter(); enc.stage='MOVE1'; enc.stageMs=0;
  w.polly.position.x=899; updateEncounter(w,enc,16); assert.equal(enc.stage,'MOVE1'); assert.equal(w.enemies.length,0);
  w.polly.position.x=900; updateEncounter(w,enc,16); assert.equal(enc.stage,'E2'); assert.equal(w.enemies.length,1); assert.equal(w.enemies[0].kind,'PROG');
});

test('encounter two spawns Prog first then Glam and clears into MOVE2', () => {
  const w=createWorld(), enc=createRatHoleEncounter(); enc.stage='E2'; enc.stageMs=0;
  updateEncounter(w,enc,16); assert.equal(w.enemies.length,1); assert.equal(w.enemies[0].kind,'PROG');
  updateEncounter(w,enc,1300); assert.equal(w.enemies.length,2); assert.deepEqual(w.enemies.map(e=>e.kind),['PROG','GLAM']);
  assert.ok(w.enemies.filter(e=>e.state!=='KO').length<=2);
  koAll(w); updateEncounter(w,enc,16); assert.equal(enc.stage,'MOVE2');
});

test('MOVE2 gates the final arena and final KO completes exactly once', () => {
  const w=createWorld(), enc=createRatHoleEncounter(); enc.stage='MOVE2'; enc.stageMs=0;
  w.polly.position.x=1649; updateEncounter(w,enc,16); assert.equal(enc.stage,'MOVE2');
  w.polly.position.x=1650; updateEncounter(w,enc,16); assert.equal(enc.stage,'E3');
  assert.deepEqual(w.enemies.map(e=>e.kind),['PUNK','GLAM','PROG']);
  w.enemies[0].state='DOWN'; w.enemies[1].state='KO'; w.enemies[2].state='KO';
  assert.equal(updateEncounter(w,enc,16).some(e=>e.type==='SLICE_COMPLETE'),false); assert.equal(w.sliceComplete,false);
  w.enemies[0].state='KO'; w.enemies[0].hp=0;
  const events=updateEncounter(w,enc,16); assert.equal(w.sliceComplete,true); assert.equal(events.filter(e=>e.type==='SLICE_COMPLETE').length,1);
  assert.equal(updateEncounter(w,enc,16).filter(e=>e.type==='SLICE_COMPLETE').length,0);
});
