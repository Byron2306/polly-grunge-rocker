import test from 'node:test';
import assert from 'node:assert/strict';
import { framesForVisualState, POLLY_HEAVY_FX_KEY } from '../src/render/spriteManifest.js';

const keys=['polly.idle','polly.walk','polly.sprint','polly.light1','polly.light2','polly.light3','polly.heavy.startup','polly.heavy.active','polly.heavy.recovery','polly.hurt','polly.knockdown','polly.getup','polly.carry','polly.victory','polly.ko'];

test('Polly production-master slice reuses exactly one body frame for every state',()=>{
  const refs=keys.map(k=>framesForVisualState(k).frames[0]);
  assert.equal(refs.every(Boolean),true);
  assert.equal(new Set(refs.map(f=>`${f.assetKey}:${f.path}:${f.frameIndex}`)).size,1);
  assert.equal(refs[0].path,'assets/characters/polly/polly-master.png');
});

test('Polly guitar arc remains separate from the production master body sprite',()=>{
  assert.equal(POLLY_HEAVY_FX_KEY,'fx.guitar-arc');
  for(const key of ['polly.heavy.startup','polly.heavy.active','polly.heavy.recovery']) assert.equal(framesForVisualState(key).frames[0].path.includes('arc'),false);
});
