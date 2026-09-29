import test from 'node:test';
import assert from 'node:assert/strict';
import { WALK_SPEED, VERTICAL_SPEED_RATIO, SPRINT_RATIO, STANDARD_LANE_TOLERANCE } from '../src/sim/constants.js';
import { createPolly, HEAVY_ATTACK, updatePolly } from '../src/sim/player.js';
import { enemyConfig, progHoldMs } from '../src/sim/enemies.js';
import { AttackTokenPool } from '../src/sim/tokens.js';
import { meleeContact } from '../src/sim/geometry.js';
import { createWorld } from '../src/sim/world.js';
import { createRatHoleEncounter, updateEncounter } from '../src/sim/encounters.js';
const idle={moveX:0,moveY:0,sprint:false,lightPressed:false,heavyPressed:false,interactPressed:false};

test('PASS1 core combat contract holds together', () => {
  assert.equal(VERTICAL_SPEED_RATIO,.82); assert.equal(SPRINT_RATIO,1.55); assert.equal(STANDARD_LANE_TOLERANCE,24);
  const p=createPolly(); updatePolly(p,{...idle,moveX:1},1000); assert.ok(p.velocity.x<=WALK_SPEED);
  updatePolly(p,{...idle,lightPressed:true},1); assert.equal(p.attack?.definition.id,'L1');
  updatePolly(p,{...idle,lightPressed:true},100); updatePolly(p,idle,220); assert.equal(p.attack?.definition.id,'L2');
  updatePolly(p,{...idle,lightPressed:true},200); updatePolly(p,idle,200); assert.equal(p.attack?.definition.id,'L3');
  assert.deepEqual([HEAVY_ATTACK.startupMs,HEAVY_ATTACK.activeMs,HEAVY_ATTACK.recoveryMs],[300,140,420]);
  assert.equal(meleeContact({x:0,y:0,width:50,height:20},{x:10,y:0,width:20,height:20},100,140,24),false);
  assert.equal(enemyConfig('GLAM').anticipationMs,420); assert.ok(progHoldMs(.2)>=180&&progHoldMs(.2)<=420); assert.equal(enemyConfig('PUNK').anticipationMs,180);
  const pool=new AttackTokenPool(2); assert.equal(pool.acquire('a','NORMAL'),true); assert.equal(pool.acquire('b','NORMAL'),true); assert.equal(pool.acquire('c','NORMAL'),false); assert.equal(pool.acquire('punk','PUNK_CHARGE'),true);
});

test('PASS1 encounter contract reaches completion through two MOVE gates without active-enemy overflow', () => {
  const w=createWorld(), e=createRatHoleEncounter();
  const tick=(ms:number)=>{updateEncounter(w,e,ms);assert.ok(w.enemies.filter(x=>x.state!=='KO').length<=3);assert.ok(w.tokens.ordinaryCount<=2);};
  tick(1000); for(const x of w.enemies){x.state='KO';x.hp=0;} tick(16);
  assert.equal(e.stage,'MOVE1'); w.polly.position.x=900; tick(1);
  tick(1300);for(const x of w.enemies){x.state='KO';x.hp=0;}tick(16);
  assert.equal(e.stage,'MOVE2'); w.polly.position.x=1650; tick(1);
  for(const x of w.enemies){x.state='KO';x.hp=0;}tick(16);
  assert.equal(w.sliceComplete,true);
});
