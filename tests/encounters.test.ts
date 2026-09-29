import test from 'node:test';
import assert from 'node:assert/strict';
import { createWorld } from '../src/sim/world.js';
import { createRatHoleEncounter, updateEncounter } from '../src/sim/encounters.js';

function koAll(w:ReturnType<typeof createWorld>){ for(const e of w.enemies){e.hp=0;e.state='KO';} }

test('opening free movement precedes encounter one and Glam gates progression until KO', () => {
  const w=createWorld(), enc=createRatHoleEncounter();
  updateEncounter(w,enc,500); assert.equal(w.enemies.length,0); assert.equal(enc.stage,'OPENING');
  updateEncounter(w,enc,600); assert.equal(enc.stage,'E1'); assert.equal(w.enemies.length,1); assert.equal(w.enemies[0].kind,'GLAM');
  updateEncounter(w,enc,1000); assert.equal(enc.stage,'E1');
  koAll(w); updateEncounter(w,enc,16); assert.equal(enc.stage,'E2');
});

test('encounter two spawns Prog first then Glam without exceeding two active enemies', () => {
  const w=createWorld(), enc=createRatHoleEncounter(); enc.stage='E2'; enc.stageMs=0;
  updateEncounter(w,enc,16); assert.equal(w.enemies.length,1); assert.equal(w.enemies[0].kind,'PROG');
  updateEncounter(w,enc,1300); assert.equal(w.enemies.length,2); assert.deepEqual(w.enemies.map(e=>e.kind),['PROG','GLAM']);
  assert.ok(w.enemies.filter(e=>e.state!=='KO').length<=2);
});

test('encounter three is Punk Glam Prog, down actors block completion, final KO completes exactly once', () => {
  const w=createWorld(), enc=createRatHoleEncounter(); enc.stage='E3'; enc.stageMs=0;
  updateEncounter(w,enc,16); assert.deepEqual(w.enemies.map(e=>e.kind),['PUNK','GLAM','PROG']); assert.equal(w.enemies.length,3);
  w.enemies[0].state='DOWN'; w.enemies[1].state='KO'; w.enemies[2].state='KO';
  assert.equal(updateEncounter(w,enc,16).some(e=>e.type==='SLICE_COMPLETE'),false); assert.equal(w.sliceComplete,false);
  w.enemies[0].state='KO'; w.enemies[0].hp=0;
  const events=updateEncounter(w,enc,16); assert.equal(w.sliceComplete,true); assert.equal(events.filter(e=>e.type==='SLICE_COMPLETE').length,1);
  assert.equal(updateEncounter(w,enc,16).filter(e=>e.type==='SLICE_COMPLETE').length,0);
});
