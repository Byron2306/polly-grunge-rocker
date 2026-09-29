import test from 'node:test';
import assert from 'node:assert/strict';
import { TouchController, mergePlayerIntents } from '../src/input/touch.js';

test('touch controller clamps movement and consumes combat edges once', () => {
  const touch = new TouchController();
  touch.setMove(2, -2);
  touch.setSprint(true);
  touch.pressLight();
  const first = touch.consumeIntent();
  assert.equal(first.moveX, 1);
  assert.equal(first.moveY, -1);
  assert.equal(first.sprint, true);
  assert.equal(first.lightPressed, true);
  const second = touch.consumeIntent();
  assert.equal(second.lightPressed, false);
  assert.equal(second.moveX, 1);
});

test('keyboard and touch intents merge into one player contract', () => {
  const merged = mergePlayerIntents(
    { moveX:-1, moveY:0, sprint:false, lightPressed:false, heavyPressed:true, interactPressed:false },
    { moveX:0.5, moveY:1, sprint:true, lightPressed:true, heavyPressed:false, interactPressed:true },
  );
  assert.equal(merged.moveX, -0.5);
  assert.equal(merged.moveY, 1);
  assert.equal(merged.sprint, true);
  assert.equal(merged.lightPressed, true);
  assert.equal(merged.heavyPressed, true);
  assert.equal(merged.interactPressed, true);
});
