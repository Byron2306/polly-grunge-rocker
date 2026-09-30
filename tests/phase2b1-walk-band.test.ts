import test from 'node:test';
import assert from 'node:assert/strict';
import type { Actor } from '../src/sim/types.js';
import { clampActorsToWalkBand } from '../src/sim/world.js';
import { WALKABLE_Y_MIN, WALKABLE_Y_MAX } from '../src/sim/constants.js';

function actor(y:number,vy:number):Actor{
  return {
    id:'a',kind:'POLLY',state:'IDLE',
    position:{x:100,y},velocity:{x:0,y:vy},facing:1,
    hp:12,maxHp:12,stagger:0,staggerResistance:4,
    body:{x:-14,y:-10,width:28,height:20},
    hurtbox:{x:-16,y:-86,width:32,height:86},
    attack:null,hitstopMs:0,hitstunMs:0,invulnerableMs:0,
    heldPickupId:null,comboIndex:0,comboResetMs:0,queuedLight:false,
    archetypeTimerMs:0,tokenOwned:false
  };
}

test('walk band clamps actors out of wall and sky',()=>{
  const a=actor(WALKABLE_Y_MIN-200,-100);
  clampActorsToWalkBand([a]);
  assert.equal(a.position.y,WALKABLE_Y_MIN);
  assert.equal(a.velocity.y,0);
});

test('walk band clamps actors below the combat floor',()=>{
  const a=actor(WALKABLE_Y_MAX+200,100);
  clampActorsToWalkBand([a]);
  assert.equal(a.position.y,WALKABLE_Y_MAX);
  assert.equal(a.velocity.y,0);
});

test('walk band leaves valid depth positions untouched',()=>{
  const mid=(WALKABLE_Y_MIN+WALKABLE_Y_MAX)/2;
  const a=actor(mid,12);
  clampActorsToWalkBand([a]);
  assert.equal(a.position.y,mid);
  assert.equal(a.velocity.y,12);
});
