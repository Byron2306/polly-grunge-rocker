import test from 'node:test';
import assert from 'node:assert/strict';
import { RAT_HOLE_LAYERS, ratHoleLayerScreenX } from '../src/render/ratHoleProductionBackdrop.js';

test('Rat Hole production art is descriptor driven across three continuous zones',()=>{
  assert.equal(RAT_HOLE_LAYERS.length,9);
  assert.deepEqual(
    RAT_HOLE_LAYERS.filter(x=>x.kind==='MID').map(x=>x.worldX),
    [0,850,1700]
  );
  assert.equal(
    RAT_HOLE_LAYERS.every(x=>x.path.startsWith('assets/environment/rat-hole/production/')),
    true
  );
});

test('production layer positioning applies the layer parallax',()=>{
  const mid=RAT_HOLE_LAYERS.find(x=>x.zone===2&&x.kind==='MID')!;
  const near=RAT_HOLE_LAYERS.find(x=>x.zone===2&&x.kind==='NEAR')!;
  assert.equal(ratHoleLayerScreenX(mid,300),550);
  assert.equal(ratHoleLayerScreenX(near,300),526);
});
