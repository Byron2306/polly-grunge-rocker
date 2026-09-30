import test from 'node:test';
import assert from 'node:assert/strict';
import { createWorld } from '../src/sim/world.js';
import { createRatHoleEncounter, updateEncounter } from '../src/sim/encounters.js';

test('one world progresses opening through all three encounters within caps to slice complete', () => {
  const w=createWorld(), enc=createRatHoleEncounter();
  updateEncounter(w,enc,1000); assert.equal(enc.stage,'E1'); assert.ok(w.enemies.length<=3);
  for(const e of w.enemies){e.state='KO';e.hp=0;} updateEncounter(w,enc,16); assert.equal(enc.stage,'MOVE1'); w.polly.position.x=900; updateEncounter(w,enc,16); assert.equal(enc.stage,'E2');
  updateEncounter(w,enc,1); updateEncounter(w,enc,1300); assert.ok(w.enemies.length<=2);
  for(const e of w.enemies){e.state='KO';e.hp=0;} updateEncounter(w,enc,16); assert.equal(enc.stage,'MOVE2'); w.polly.position.x=1650; updateEncounter(w,enc,16); assert.equal(enc.stage,'E3');
  updateEncounter(w,enc,1); assert.equal(w.enemies.length,3); assert.ok(w.tokens.ordinaryCount<=2);
  for(const e of w.enemies){e.state='KO';e.hp=0;} updateEncounter(w,enc,16);
  assert.equal(w.sliceComplete,true); assert.equal(enc.stage,'COMPLETE'); assert.ok(w.tokens.ordinaryCount<=2);
});
