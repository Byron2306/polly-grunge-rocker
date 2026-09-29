import test from 'node:test';
import assert from 'node:assert/strict';
import { createGameConfig } from '../src/game/config.js';
import { RatHoleScene } from '../src/game/scenes/RatHoleScene.js';

test('bootstrap config is fixed-size pixel art and registers Rat Hole without creating a game', () => {
  const config = createGameConfig();
  assert.equal(config.width, 960);
  assert.equal(config.height, 540);
  assert.equal(config.pixelArt, true);
  assert.deepEqual(config.scene, [RatHoleScene]);
  assert.equal((globalThis as { __pollyGameCreated?: boolean }).__pollyGameCreated, undefined);
});
