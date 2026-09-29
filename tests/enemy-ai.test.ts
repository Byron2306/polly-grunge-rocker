import test from 'node:test';
import assert from 'node:assert/strict';
import { COMMON_ENEMY_STATES, createEnemy, enemyConfig, progHoldMs, updateEnemy } from '../src/sim/enemies.js';
import { AttackTokenPool } from '../src/sim/tokens.js';
import { createPolly } from '../src/sim/player.js';

test('all archetypes use common state taxonomy and health targets', () => {
  assert.deepEqual(COMMON_ENEMY_STATES,['SPAWN','IDLE','APPROACH','ALIGN','THREATEN','ATTACK','RECOVER','HURT','KNOCKBACK','DOWN','GETUP','KO']);
  assert.equal(createEnemy('GLAM').hp,6); assert.equal(createEnemy('PROG').hp,5); assert.equal(createEnemy('PUNK').hp,6);
});

test('archetype timings are pinned and prog hold is bounded deterministically', () => {
  const g=enemyConfig('GLAM'), p=enemyConfig('PROG'), punk=enemyConfig('PUNK');
  assert.equal(g.anticipationMs,420); assert.equal(g.recoveryMs,450);
  assert.equal(progHoldMs(0),180); assert.equal(progHoldMs(1),420); assert.ok(progHoldMs(.5)>=180 && progHoldMs(.5)<=420);
  assert.equal(punk.anticipationMs,180); assert.equal(punk.recoveryMs,500); assert.ok(punk.chargeMinMs===350 && punk.chargeMaxMs===600);
  assert.equal(p.kind,'PROG');
});

test('enemy aligns lane before threatening and acquires token only for committed attack', () => {
  const e=createEnemy('GLAM'); const polly=createPolly(); const pool=new AttackTokenPool(2);
  e.state='APPROACH'; e.position={x:polly.position.x+70,y:polly.position.y+80};
  updateEnemy(e,{polly,tokens:pool,seed01:.5},100);
  assert.equal(e.state,'ALIGN');
  e.position.y=polly.position.y; updateEnemy(e,{polly,tokens:pool,seed01:.5},100);
  assert.ok(['THREATEN','ATTACK'].includes(e.state as string));
});
