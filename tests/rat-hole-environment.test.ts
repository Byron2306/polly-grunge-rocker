import test from 'node:test';
import assert from 'node:assert/strict';
import { RAT_HOLE_MODULES, environmentDescriptors } from '../src/render/ratHoleEnvironment.js';

test('Rat Hole environment exposes modular far middle ground and foreground layers',()=>{const layers=new Set(RAT_HOLE_MODULES.map(m=>m.layer));assert.deepEqual([...layers].sort(),['far','foreground','ground','middle']);assert.ok(RAT_HOLE_MODULES.some(m=>m.kind==='NEON'));assert.ok(RAT_HOLE_MODULES.some(m=>m.kind==='DUMPSTER'));assert.ok(RAT_HOLE_MODULES.some(m=>m.kind==='PUDDLE'));});

test('Rat Hole environment applies deterministic parallax without defining gameplay collision',()=>{const a=environmentDescriptors(0),b=environmentDescriptors(100);const skylineA=a.find(x=>x.id==='skyline')!,skylineB=b.find(x=>x.id==='skyline')!,groundA=a.find(x=>x.id==='asphalt')!,groundB=b.find(x=>x.id==='asphalt')!;assert.equal(skylineA.screenX-skylineB.screenX,20);assert.equal(groundA.screenX-groundB.screenX,100);assert.equal('collision' in groundA,false);});
