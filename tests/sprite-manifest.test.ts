import test from 'node:test';
import assert from 'node:assert/strict';
import { PHASE2_SPRITE_MANIFEST, framesForVisualState } from '../src/render/spriteManifest.js';

const required=['polly.idle','polly.walk','polly.sprint','polly.light1','polly.light2','polly.light3','polly.heavy.startup','polly.heavy.active','polly.hurt','polly.getup','polly.ko','glam.idle','glam.walk','glam.threaten','glam.attack','glam.hurt','glam.ko','prog.idle','prog.walk','prog.threaten','prog.attack','prog.hurt','prog.ko','punk.idle','punk.walk','punk.threaten','punk.attack','punk.hurt','punk.ko'];

test('sprite manifest gives every approved Phase 2 state exactly two frame slots',()=>{for(const key of required){const def=PHASE2_SPRITE_MANIFEST[key]; assert.ok(def,key); assert.equal(def.frames.length,2,key);}});

test('sprite manifest falls back safely for missing keys',()=>{const d=framesForVisualState('unknown.state'); assert.equal(d.key,'fallback'); assert.equal(d.frames.length,2);});
