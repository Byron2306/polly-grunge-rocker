import test from 'node:test';
import assert from 'node:assert/strict';
import { createWorld } from '../src/sim/world.js';
import { strikeDescriptors } from '../src/render/blockRenderer.js';
import type { AttackDefinition } from '../src/sim/types.js';

const LIGHT: AttackDefinition = {
  id:'L1', startupMs:90, activeMs:80, recoveryMs:150,
  damage:1, stagger:1, rangeX:48, laneTolerance:24,
  knockback:25, hitstopMs:45,
};

test('active player attacks render a thin protruding strike bar in facing direction', () => {
  const world=createWorld();
  world.polly.position={x:200,y:320};
  world.polly.facing=1;
  world.polly.attack={definition:LIGHT,phase:'ACTIVE',elapsedMs:100,hitVictimIds:new Set()};
  let strikes=strikeDescriptors(world);
  assert.equal(strikes.length,1);
  assert.equal(strikes[0].attackId,'L1');
  assert.equal(strikes[0].width,48);
  assert.ok(strikes[0].height < 20);
  assert.ok(strikes[0].x > world.polly.position.x);

  world.polly.facing=-1;
  strikes=strikeDescriptors(world);
  assert.ok(strikes[0].x < world.polly.position.x);
});

test('startup and recovery frames do not show an active strike bar', () => {
  const world=createWorld();
  world.polly.attack={definition:LIGHT,phase:'STARTUP',elapsedMs:20,hitVictimIds:new Set()};
  assert.equal(strikeDescriptors(world).length,0);
  world.polly.attack.phase='RECOVERY';
  assert.equal(strikeDescriptors(world).length,0);
});
