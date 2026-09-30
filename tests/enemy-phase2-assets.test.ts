import test from 'node:test';
import assert from 'node:assert/strict';
import { PHASE2_SPRITE_MANIFEST } from '../src/render/spriteManifest.js';

const families=['glam','prog','punk'] as const;
const states=['idle','walk','threaten','attack','hurt','ko'];

test('enemy Phase 2 states resolve to two frames for every archetype',()=>{for(const family of families) for(const state of states){const d=PHASE2_SPRITE_MANIFEST[`${family}.${state}`];assert.ok(d,`${family}.${state}`);assert.equal(d.frames.length,2);assert.ok(d.frames.every(f=>f.path.startsWith(`assets/enemies/${family}/`)));}});

test('enemy Phase 2 manifest preserves distinct palette identities',()=>{const tags=families.map(f=>PHASE2_SPRITE_MANIFEST[`${f}.idle`].paletteTag);assert.equal(new Set(tags).size,3);});
