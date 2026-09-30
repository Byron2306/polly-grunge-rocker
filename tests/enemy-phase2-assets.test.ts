import test from 'node:test';
import assert from 'node:assert/strict';
import { framesForVisualState } from '../src/render/spriteManifest.js';

const families=['glam','prog','punk'] as const;
const states=['idle','walk','threaten','attack','hurt','ko'];

test('enemy archetypes stay on proven block fallback until production masters are approved',()=>{
  for(const family of families) for(const state of states){
    const d=framesForVisualState(`${family}.${state}`);
    assert.equal(d.key,'fallback',`${family}.${state}`);
    assert.equal(d.frames.length,0,`${family}.${state}`);
  }
});
