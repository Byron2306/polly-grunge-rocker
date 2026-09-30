import test from 'node:test';
import assert from 'node:assert/strict';
import { PHASE2_SPRITE_MANIFEST, POLLY_HEAVY_FX_KEY } from '../src/render/spriteManifest.js';

const keys=['polly.idle','polly.walk','polly.sprint','polly.light1','polly.light2','polly.light3','polly.heavy.startup','polly.heavy.active','polly.heavy.recovery','polly.hurt','polly.knockdown','polly.getup','polly.carry','polly.victory','polly.ko'];

test('Polly Phase 2 has two frame references for every approved state',()=>{for(const key of keys){const d=PHASE2_SPRITE_MANIFEST[key];assert.ok(d,key);assert.equal(d.frames.length,2,key);assert.ok(d.frames.every(f=>f.path.startsWith('assets/characters/polly/')),key);}});

test('Polly Phase 2 Heavy keeps guitar arc separate from body frames',()=>{assert.equal(POLLY_HEAVY_FX_KEY,'fx.guitar-arc');for(const key of ['polly.heavy.startup','polly.heavy.active','polly.heavy.recovery']) assert.equal(PHASE2_SPRITE_MANIFEST[key].frames.some(f=>f.path.includes('arc')),false);});
