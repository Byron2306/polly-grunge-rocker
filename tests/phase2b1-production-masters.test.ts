import test from 'node:test';
import assert from 'node:assert/strict';
import { framesForVisualState, productionSpriteSheets } from '../src/render/spriteManifest.js';

const enemyStates=['idle','walk','threaten','attack','hurt','ko'];

test('all four production families use one 128px master each',()=>{
  const sheets=productionSpriteSheets();
  assert.deepEqual(
    sheets.map(s=>s.assetKey),
    ['characters.polly.master','enemies.glam.master','enemies.prog.master','enemies.punk.master']
  );
  assert.equal(sheets.every(s=>s.frameWidth===128&&s.frameHeight===128),true);
});

test('Glam Prog and Punk all have a production master in every visual state',()=>{
  for(const family of ['glam','prog','punk']){
    for(const state of enemyStates){
      const d=framesForVisualState(`${family}.${state}`);
      assert.equal(d.frames.length,1,`${family}.${state}`);
      assert.equal(d.frames[0].authoredFacing,1,`${family}.${state}`);
    }
  }
});
