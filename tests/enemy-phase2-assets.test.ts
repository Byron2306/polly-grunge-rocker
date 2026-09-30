import test from 'node:test';
import assert from 'node:assert/strict';
import { framesForVisualState } from '../src/render/spriteManifest.js';

const states=['idle','walk','threaten','attack','hurt','ko'];

test('all three enemy archetypes use approved single production masters',()=>{
  const expected={
    glam:'assets/enemies/glam/glam-master.png',
    prog:'assets/enemies/prog/prog-master.png',
    punk:'assets/enemies/punk/punk-master.png',
  } as const;
  for(const family of ['glam','prog','punk'] as const){
    for(const state of states){
      const d=framesForVisualState(`${family}.${state}`);
      assert.equal(d.frames.length,1,`${family}.${state}`);
      assert.equal(d.frames[0].path,expected[family],`${family}.${state}`);
      assert.equal(d.frames[0].authoredFacing,1,`${family}.${state}`);
    }
  }
});
