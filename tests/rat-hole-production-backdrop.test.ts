import test from 'node:test';
import assert from 'node:assert/strict';
import { RAT_HOLE_BACKDROPS, backdropScreenX } from '../src/render/ratHoleProductionBackdrop.js';

test('Rat Hole production pass provides three world-space zone plates',()=>{
  assert.equal(RAT_HOLE_BACKDROPS.length,3);
  assert.deepEqual(RAT_HOLE_BACKDROPS.map(x=>x.worldX),[0,850,1700]);
  assert.equal(RAT_HOLE_BACKDROPS.every(x=>x.width===960&&x.height===540),true);
});

test('backdrop positioning follows the same camera offset as combat space',()=>{
  assert.equal(backdropScreenX(850,300),550);
});
