import test from 'node:test';
import assert from 'node:assert/strict';
import { enterLandscapeMode, isPortraitViewport } from '../src/platform/mobileShell.js';

test('portrait gate follows viewport geometry', () => {
  assert.equal(isPortraitViewport(412, 915), true);
  assert.equal(isPortraitViewport(915, 412), false);
  assert.equal(isPortraitViewport(540, 540), false);
});

test('landscape entry requests fullscreen before orientation lock and degrades safely', async () => {
  const calls:string[] = [];
  const result = await enterLandscapeMode({
    requestFullscreen: async () => { calls.push('fullscreen'); },
    lockLandscape: async () => { calls.push('lock'); },
  });
  assert.deepEqual(calls, ['fullscreen', 'lock']);
  assert.equal(result, 'locked');
  const failed = await enterLandscapeMode({
    requestFullscreen: async () => { throw new Error('blocked'); },
    lockLandscape: async () => { calls.push('never'); },
  });
  assert.equal(failed, 'failed');
});
