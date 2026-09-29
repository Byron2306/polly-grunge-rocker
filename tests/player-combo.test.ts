import test from 'node:test';
import assert from 'node:assert/strict';
import { createPolly, updatePolly } from '../src/sim/player.js';
import { readKeyboardIntent } from '../src/input/keyboard.js';
const idle = { moveX:0, moveY:0, sprint:false, lightPressed:false, heavyPressed:false, interactPressed:false };

test('edge-triggered J does not repeat while held', () => {
  const first = readKeyboardIntent(new Set(['KeyJ']), new Set());
  const held = readKeyboardIntent(new Set(['KeyJ']), new Set(['KeyJ']));
  assert.equal(first.lightPressed, true);
  assert.equal(held.lightPressed, false);
});

test('light chain uses L1 L2 L3 timings and only one queued action', () => {
  const p = createPolly();
  updatePolly(p, {...idle, lightPressed:true}, 1);
  assert.equal(p.comboIndex, 1);
  assert.equal(p.attack?.definition.startupMs, 90);
  updatePolly(p, {...idle, lightPressed:true}, 100);
  updatePolly(p, {...idle, lightPressed:true}, 1);
  assert.equal(p.queuedLight, true);
  updatePolly(p, idle, 220);
  assert.equal(p.comboIndex, 2);
  assert.equal(p.attack?.definition.startupMs, 110);
  updatePolly(p, {...idle, lightPressed:true}, 200);
  updatePolly(p, idle, 200);
  assert.equal(p.comboIndex, 3);
  assert.equal(p.attack?.definition.startupMs, 150);
});

test('combo resets after roughly 300ms idle window', () => {
  const p = createPolly();
  updatePolly(p, {...idle, lightPressed:true}, 1);
  updatePolly(p, idle, 400);
  updatePolly(p, idle, 301);
  assert.equal(p.comboIndex, 0);
});
