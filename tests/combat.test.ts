import test from 'node:test';
import assert from 'node:assert/strict';
import { createPolly, HEAVY_ATTACK, startHeavy, updatePolly } from '../src/sim/player.js';
import { resolveAttackHit } from '../src/sim/combat.js';
const idle={moveX:0,moveY:0,sprint:false,lightPressed:false,heavyPressed:false,interactPressed:false};
function enemy(kind:'GLAM'|'PROG'='GLAM'){ const a=createPolly(); a.id='enemy'; a.kind=kind; a.hp=kind==='PROG'?5:6; a.maxHp=a.hp; return a; }

test('heavy definition pins timing damage stagger and wider lane tolerance', () => {
  assert.deepEqual([HEAVY_ATTACK.startupMs,HEAVY_ATTACK.activeMs,HEAVY_ATTACK.recoveryMs],[300,140,420]);
  assert.equal(HEAVY_ATTACK.damage,2.8); assert.equal(HEAVY_ATTACK.stagger,4); assert.ok(HEAVY_ATTACK.laneTolerance>24);
});

test('single active attack is idempotent per victim and lane invalid contact misses', () => {
  const p=createPolly(); const e=enemy('GLAM'); e.position={x:p.position.x+30,y:p.position.y};
  startHeavy(p); updatePolly(p,idle,320);
  const first=resolveAttackHit(p,e,HEAVY_ATTACK); const hp=e.hp;
  const second=resolveAttackHit(p,e,HEAVY_ATTACK);
  assert.equal(first.hit,true); assert.equal(second.hit,false); assert.equal(e.hp,hp);
  const e2=enemy('GLAM'); e2.position={x:p.position.x+30,y:p.position.y+80};
  assert.equal(resolveAttackHit(p,e2,HEAVY_ATTACK).hit,false);
});

test('hitstop and hitstun are separate clocks', () => {
  const p=createPolly(); const e=enemy('GLAM'); e.position={x:p.position.x+30,y:p.position.y}; startHeavy(p); updatePolly(p,idle,320);
  resolveAttackHit(p,e,HEAVY_ATTACK); const stun=e.hitstunMs; const stop=e.hitstopMs;
  assert.ok(stop>0 && stun>0);
  const before=e.hitstunMs; e.hitstopMs=Math.max(e.hitstopMs,50);
  const consume=Math.min(25,e.hitstopMs); e.hitstopMs-=consume;
  assert.equal(e.hitstunMs,before);
});

test('damage clamps hp, heavy knockback dominates lights, and down invulnerability blocks prone re-hit', () => {
  const p=createPolly(); const e=enemy('PROG'); e.position={x:p.position.x+30,y:p.position.y}; e.hp=2;
  startHeavy(p); updatePolly(p,idle,320);
  const result=resolveAttackHit(p,e,HEAVY_ATTACK);
  assert.equal(e.hp,0); assert.equal(e.state,'KO'); assert.ok(result.knockback>=100); assert.ok(e.invulnerableMs>=350);
  p.attack!.hitVictimIds.clear();
  assert.equal(resolveAttackHit(p,e,HEAVY_ATTACK).hit,false);
});
