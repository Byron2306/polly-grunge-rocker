import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveCandidate, resolvedCandidates } from '../src/music/authoring/session.js';
import type { AuthoringSession } from '../src/music/authoring/types.js';

const base=():AuthoringSession=>({
  schema:'polly.authoring-session.v1',sessionId:'s',trackId:'t',durationMs:8000,
  inputs:[],
  candidates:[
    {id:'o1',kind:'ONSET',confidence:.99,sourceId:'drums',role:'DRUMS',startMs:2000,endMs:2050,eventKind:'ONSET'},
    {id:'b1',kind:'BPM',confidence:.95,sourceId:'mix',bpm:120},
  ],
  corrections:[],
});

test('unreviewed candidate remains advisory and cannot resolve authoritatively',()=>{
  const s=base();
  assert.equal(resolveCandidate(s,'o1'),null);
  assert.deepEqual(resolvedCandidates(s),[]);
});

test('ACCEPT preserves values, REJECT removes, and ADJUST replaces only explicit fields',()=>{
  const accepted=base(); accepted.corrections=[{candidateId:'o1',decision:'ACCEPT'}];
  assert.equal(resolveCandidate(accepted,'o1')?.startMs,2000);
  const rejected=base(); rejected.corrections=[{candidateId:'o1',decision:'REJECT'}];
  assert.equal(resolveCandidate(rejected,'o1'),null);
  const adjusted=base(); adjusted.corrections=[{candidateId:'o1',decision:'ADJUST',startMs:1985}];
  const r=resolveCandidate(adjusted,'o1');
  assert.equal(r?.startMs,1985);
  assert.equal(r?.endMs,2050);
  assert.equal(r?.confidence,.99);
});

test('duplicate corrections and unknown candidate corrections are refused',()=>{
  const duplicate=base(); duplicate.corrections=[{candidateId:'o1',decision:'ACCEPT'},{candidateId:'o1',decision:'REJECT'}];
  assert.throws(()=>resolvedCandidates(duplicate),/AUTHORING_CORRECTION_DUPLICATE/);
  const unknown=base(); unknown.corrections=[{candidateId:'ghost',decision:'ACCEPT'}];
  assert.throws(()=>resolvedCandidates(unknown),/AUTHORING_CORRECTION_UNKNOWN/);
});

test('negative adjusted time can be represented for later export validation',()=>{
  const s=base(); s.corrections=[{candidateId:'o1',decision:'ADJUST',startMs:-10}];
  assert.equal(resolveCandidate(s,'o1')?.startMs,-10);
});
