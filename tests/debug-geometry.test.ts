import test from 'node:test';
import assert from 'node:assert/strict';
import type { Actor } from '../src/sim/types.js';
import { debugGeometryDescriptors, toggleDebugGeometry } from '../src/render/debugGeometry.js';

const actor=():Actor=>({id:'p',kind:'POLLY',state:'IDLE',position:{x:100,y:300},velocity:{x:0,y:0},facing:1,hp:12,maxHp:12,stagger:0,staggerResistance:4,body:{x:-14,y:-10,width:28,height:20},hurtbox:{x:-16,y:-86,width:32,height:86},attack:null,hitstopMs:0,hitstunMs:0,invulnerableMs:0,heldPickupId:null,comboIndex:0,comboResetMs:0,queuedLight:false,archetypeTimerMs:0,tokenOwned:false});

test('debug geometry defaults aesthetic and toggles explicitly',()=>{assert.equal(toggleDebugGeometry('AESTHETIC'),'GEOMETRY'); assert.equal(toggleDebugGeometry('GEOMETRY'),'AESTHETIC');});

test('debug geometry follows actor world coordinates',()=>{const a=actor(); const first=debugGeometryDescriptors({polly:a,enemies:[]}); const body=first.find(x=>x.kind==='BODY')!; assert.equal(body.x,86); assert.equal(body.y,290); a.position.x=140; const moved=debugGeometryDescriptors({polly:a,enemies:[]}).find(x=>x.kind==='BODY')!; assert.equal(moved.x,126);});

test('debug attack descriptor mirrors with facing while preserving anchor',()=>{const a=actor(); a.state='ATTACK';a.attack={definition:{id:'L1',startupMs:1,activeMs:1,recoveryMs:1,damage:1,stagger:1,rangeX:48,laneTolerance:24,knockback:1,hitstopMs:1},phase:'ACTIVE',elapsedMs:0,hitVictimIds:new Set()}; const right=debugGeometryDescriptors({polly:a,enemies:[]}).find(x=>x.kind==='ATTACK')!; a.facing=-1; const left=debugGeometryDescriptors({polly:a,enemies:[]}).find(x=>x.kind==='ATTACK')!; assert.ok(right.x>100); assert.ok(left.x<100); assert.equal(right.anchorX,left.anchorX);});
