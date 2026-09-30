import test from 'node:test';
import assert from 'node:assert/strict';
import type { Actor } from '../src/sim/types.js';
import { combatFxForActor } from '../src/render/combatFx.js';

const actor=(kind:Actor['kind']):Actor=>({id:'x',kind,state:'IDLE',position:{x:100,y:300},velocity:{x:0,y:0},facing:1,hp:6,maxHp:6,stagger:0,staggerResistance:4,body:{x:0,y:0,width:28,height:20},hurtbox:{x:-16,y:-82,width:32,height:82},attack:null,hitstopMs:0,hitstunMs:0,invulnerableMs:0,heldPickupId:null,comboIndex:0,comboResetMs:0,queuedLight:false,archetypeTimerMs:0,tokenOwned:false});

test('combat FX maps Polly heavy to a separate guitar arc',()=>{const a=actor('POLLY');a.state='ATTACK';a.attack={definition:{id:'HEAVY',startupMs:300,activeMs:140,recoveryMs:420,damage:2.8,stagger:4,rangeX:86,laneTolerance:34,knockback:130,hitstopMs:105},phase:'ACTIVE',elapsedMs:320,hitVictimIds:new Set()};const fx=combatFxForActor(a);assert.ok(fx.some(x=>x.kind==='GUITAR_ARC'));assert.equal(fx.some(x=>('damage' in x)),false);});

test('combat FX gives Prog and Punk distinct signature geometry',()=>{const prog=actor('PROG');prog.state='THREATEN';const punk=actor('PUNK');punk.state='ATTACK';const pfx=combatFxForActor(prog),kfx=combatFxForActor(punk);assert.ok(pfx.some(x=>x.kind==='PROG_WAVE'));assert.ok(kfx.some(x=>x.kind==='PUNK_RUSH'));assert.notEqual(pfx[0].color,kfx[0].color);});

test('combat FX exposes hurt and KO impact bursts without mutating actor',()=>{const a=actor('GLAM');a.state='KO';const before=JSON.stringify(a);const fx=combatFxForActor(a);assert.ok(fx.some(x=>x.kind==='KO_BURST'));assert.equal(JSON.stringify(a),before);});
