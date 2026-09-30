import test from 'node:test';
import assert from 'node:assert/strict';
import type { Actor } from '../src/sim/types.js';
import { presentationForActor } from '../src/render/actorPresenter.js';

function enemy(kind:'GLAM'|'PROG'|'PUNK',facing:1|-1):Actor{
  return {
    id:kind.toLowerCase(),kind,state:'ATTACK',
    position:{x:500,y:360},velocity:{x:0,y:0},facing,
    hp:6,maxHp:6,stagger:0,staggerResistance:4,
    body:{x:-14,y:-10,width:28,height:20},
    hurtbox:{x:-16,y:-82,width:32,height:82},
    attack:null,hitstopMs:0,hitstunMs:0,invulnerableMs:0,
    heldPickupId:null,comboIndex:0,comboResetMs:0,queuedLight:false,
    archetypeTimerMs:0,tokenOwned:false
  };
}

test('production enemies visually face right when sim faces right',()=>{
  for(const kind of ['GLAM','PROG','PUNK'] as const){
    assert.equal(presentationForActor(enemy(kind,1),0,true).flipX,false,kind);
  }
});

test('production enemies visually flip when sim faces left',()=>{
  for(const kind of ['GLAM','PROG','PUNK'] as const){
    assert.equal(presentationForActor(enemy(kind,-1),0,true).flipX,true,kind);
  }
});
