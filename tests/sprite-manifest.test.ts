import test from 'node:test';
import assert from 'node:assert/strict';
import { framesForVisualState, productionSpriteSheets } from '../src/render/spriteManifest.js';

const pollyStates=[
  'polly.idle','polly.walk','polly.sprint','polly.light1','polly.light2','polly.light3',
  'polly.heavy.startup','polly.heavy.active','polly.heavy.recovery',
  'polly.hurt','polly.knockdown','polly.getup','polly.carry','polly.victory','polly.ko'
];
const enemyStates=['idle','walk','threaten','attack','hurt','ko'];

test('Polly states share one production master',()=>{
  const defs=pollyStates.map(framesForVisualState);
  assert.equal(defs.every(d=>d.frames.length===1),true);
  assert.equal(new Set(defs.map(d=>d.frames[0].assetKey)).size,1);
  assert.equal(defs[0].frames[0].assetKey,'characters.polly.master');
});

test('Glam Prog and Punk each share one production master',()=>{
  for(const family of ['glam','prog','punk']){
    const defs=enemyStates.map(state=>framesForVisualState(`${family}.${state}`));
    assert.equal(defs.every(d=>d.frames.length===1),true,family);
    assert.equal(new Set(defs.map(d=>d.frames[0].assetKey)).size,1,family);
  }
});

test('Phase2B.1 preloads four 128px production masters',()=>{
  const sheets=productionSpriteSheets();
  assert.deepEqual(
    sheets.map(s=>s.assetKey),
    ['characters.polly.master','enemies.glam.master','enemies.prog.master','enemies.punk.master']
  );
  assert.equal(sheets.every(s=>s.frameWidth===128&&s.frameHeight===128),true);
});
