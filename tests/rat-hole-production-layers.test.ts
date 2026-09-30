import test from 'node:test';
import assert from 'node:assert/strict';
import { RAT_HOLE_LAYERS, ratHoleLayerScreenX } from '../src/render/ratHoleProductionBackdrop.js';

test('Rat Hole exposes exactly three production layers per zone',()=>{
  assert.equal(RAT_HOLE_LAYERS.length,9);
  for(const zone of [1,2,3] as const){
    const kinds=RAT_HOLE_LAYERS.filter(x=>x.zone===zone).map(x=>x.kind).sort();
    assert.deepEqual(kinds,['FAR','MID','NEAR']);
  }
});

test('Rat Hole production layers preserve anchors dimensions and depth families',()=>{
  for(const kind of ['FAR','MID','NEAR'] as const){
    const family=RAT_HOLE_LAYERS.filter(x=>x.kind===kind);
    assert.deepEqual(family.map(x=>x.worldX),[0,850,1700]);
  }
  assert.equal(RAT_HOLE_LAYERS.every(x=>x.width===960&&x.height===540),true);
  assert.equal(RAT_HOLE_LAYERS.filter(x=>x.kind!=='NEAR').every(x=>x.depth<0),true);
  assert.equal(RAT_HOLE_LAYERS.filter(x=>x.kind==='NEAR').every(x=>x.depth>0),true);
});

test('Rat Hole parallax is deterministic and does not mutate descriptors',()=>{
  const layer=RAT_HOLE_LAYERS.find(x=>x.zone===2&&x.kind==='NEAR')!;
  const before=JSON.stringify(layer);
  const a=ratHoleLayerScreenX(layer,300);
  const b=ratHoleLayerScreenX(layer,300);
  assert.equal(a,b);
  assert.equal(JSON.stringify(layer),before);
});
