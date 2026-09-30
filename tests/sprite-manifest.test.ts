import test from 'node:test';
import assert from 'node:assert/strict';
import { framesForVisualState, productionSpriteSheets } from '../src/render/spriteManifest.js';

const pollyStates=['polly.idle','polly.walk','polly.sprint','polly.light1','polly.light2','polly.light3','polly.heavy.startup','polly.heavy.active','polly.heavy.recovery','polly.hurt','polly.knockdown','polly.getup','polly.carry','polly.victory','polly.ko'];

test('sprite manifest maps every Polly state to one shared production master',()=>{
  const defs=pollyStates.map(framesForVisualState);
  assert.equal(defs.every(d=>d.frames.length===1),true);
  const refs=defs.map(d=>d.frames[0]);
  assert.equal(new Set(refs.map(r=>`${r.assetKey}:${r.path}:${r.frameIndex}`)).size,1);
  assert.equal(refs[0].path,'assets/characters/polly/polly-master.png');
});

test('sprite manifest falls back safely when no production master exists',()=>{
  const d=framesForVisualState('glam.attack');
  assert.equal(d.key,'fallback');
  assert.equal(d.frames.length,0);
});

test('only Polly production master is preloaded in the production-master slice',()=>{
  const sheets=productionSpriteSheets();
  assert.equal(sheets.length,1);
  assert.equal(sheets[0].assetKey,'characters.polly.master');
  assert.equal(sheets[0].frameWidth,160);
  assert.equal(sheets[0].frameHeight,160);
});
