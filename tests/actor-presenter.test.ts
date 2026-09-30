import test from 'node:test';
import assert from 'node:assert/strict';
import type { Actor } from '../src/sim/types.js';
import { ActorPresenter, presentationForActor } from '../src/render/actorPresenter.js';

const actor=():Actor=>({id:'p',kind:'POLLY',state:'IDLE',position:{x:120,y:320},velocity:{x:0,y:0},facing:1,hp:12,maxHp:12,stagger:0,staggerResistance:4,body:{x:0,y:0,width:1,height:1},hurtbox:{x:0,y:0,width:1,height:1},attack:null,hitstopMs:0,hitstunMs:0,invulnerableMs:0,heldPickupId:null,comboIndex:0,comboResetMs:0,queuedLight:false,archetypeTimerMs:0,tokenOwned:false});

test('actor presenter placement uses foot anchor and facing without mutating actor',()=>{const a=actor(),before=JSON.stringify(a); let p=presentationForActor(a,20,true); assert.equal(p.x,100); assert.equal(p.y,320); assert.equal(p.flipX,false); a.facing=-1; p=presentationForActor(a,20,true); assert.equal(p.x,100); assert.equal(p.y,320); assert.equal(p.flipX,true); assert.equal(JSON.stringify({...a,facing:1}),before);});

test('actor presenter selects block fallback when asset unavailable',()=>{const p=presentationForActor(actor(),0,false); assert.equal(p.fallback,true);});

test('ActorPresenter sync does not mutate simulation fields',()=>{const scene:any={textures:{exists:()=>false},add:{sprite:()=>{throw new Error('should not create sprite');}}}; const a=actor(),before=JSON.stringify(a); const presenter=new ActorPresenter(scene); presenter.syncActor(a,0); assert.equal(JSON.stringify(a),before); presenter.destroy();});
