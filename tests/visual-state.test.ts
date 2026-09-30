import test from 'node:test';
import assert from 'node:assert/strict';
import type { Actor, AttackPhase } from '../src/sim/types.js';
import { visualStateForActor } from '../src/render/visualState.js';

const actor=(kind:Actor['kind'],state:Actor['state']='IDLE'):Actor=>({id:'x',kind,state,position:{x:0,y:0},velocity:{x:0,y:0},facing:1,hp:6,maxHp:6,stagger:0,staggerResistance:4,body:{x:0,y:0,width:1,height:1},hurtbox:{x:0,y:0,width:1,height:1},attack:null,hitstopMs:0,hitstunMs:0,invulnerableMs:0,heldPickupId:null,comboIndex:0,comboResetMs:0,queuedLight:false,archetypeTimerMs:0,tokenOwned:false});
const attack=(a:Actor,id:string,phase:AttackPhase)=>{a.state='ATTACK';a.attack={definition:{id,startupMs:1,activeMs:1,recoveryMs:1,damage:1,stagger:1,rangeX:1,laneTolerance:1,knockback:1,hitstopMs:1},phase,elapsedMs:0,hitVictimIds:new Set()};return a;};

test('visual state maps Polly locomotion and combat without mutation',()=>{const p=actor('POLLY'); assert.equal(visualStateForActor(p).key,'polly.idle'); p.velocity.x=20; assert.equal(visualStateForActor(p).key,'polly.walk'); p.velocity.x=220; assert.equal(visualStateForActor(p).key,'polly.sprint'); for(const id of ['L1','L2','L3']) assert.equal(visualStateForActor(attack(actor('POLLY'),id,'ACTIVE')).key,`polly.light${id[1]}`); assert.equal(visualStateForActor(attack(actor('POLLY'),'HEAVY','STARTUP')).key,'polly.heavy.startup'); assert.equal(visualStateForActor(attack(actor('POLLY'),'HEAVY','ACTIVE')).key,'polly.heavy.active');});

test('visual state maps enemy threat and attacks distinctly',()=>{for(const [kind,prefix] of [['GLAM','glam'],['PROG','prog'],['PUNK','punk']] as const){const t=actor(kind,'THREATEN'); assert.equal(visualStateForActor(t).key,`${prefix}.threaten`); const a=actor(kind,'ATTACK'); assert.equal(visualStateForActor(a).key,`${prefix}.attack`);}});

test('visual state exposes facing loop policy and stable fallback',()=>{const p=actor('POLLY','HURT'); p.facing=-1; const d=visualStateForActor(p); assert.equal(d.facing,-1); assert.equal(d.loop,false); const weird=actor('POLLY'); (weird as any).state='WAT'; assert.equal(visualStateForActor(weird).key,'polly.idle');});
