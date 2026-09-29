import test from 'node:test';
import assert from 'node:assert/strict';
import { AttackTokenPool } from '../src/sim/tokens.js';

test('ordinary attack tokens cap at exactly two and release cleanly', () => {
  const pool=new AttackTokenPool(2);
  assert.equal(pool.acquire('a','NORMAL'),true); assert.equal(pool.acquire('b','NORMAL'),true); assert.equal(pool.acquire('c','NORMAL'),false);
  pool.release('a'); assert.equal(pool.acquire('c','NORMAL'),true); assert.equal(pool.ordinaryCount,2);
  pool.release('b'); pool.release('c'); assert.equal(pool.ordinaryCount,0);
});

test('only punk charge may use controlled bypass', () => {
  const pool=new AttackTokenPool(2); pool.acquire('a','NORMAL'); pool.acquire('b','NORMAL');
  assert.equal(pool.acquire('glam','GLAM_BACKHAND'),false);
  assert.equal(pool.acquire('punk','PUNK_CHARGE'),true);
  assert.equal(pool.has('punk'),true);
});
