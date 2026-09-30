import test from 'node:test';
import assert from 'node:assert/strict';
import type { AuthoringSession } from '../src/music/authoring/types.js';

test('authoring session represents advisory candidates and explicit human corrections',()=>{
  const session:AuthoringSession={
    schema:'polly.authoring-session.v1',
    sessionId:'rat-hole-authoring',
    trackId:'rat-hole-grunge-reference-v1',
    durationMs:8000,
    inputs:[{id:'drums-wav',kind:'WAV',role:'DRUMS',path:'drums.wav'}],
    candidates:[
      {id:'tempo-120',kind:'BPM',confidence:.8,sourceId:'drums-wav',bpm:120},
      {id:'drums-onset-1',kind:'ONSET',confidence:.9,sourceId:'drums-wav',role:'DRUMS',startMs:2000,endMs:2050,eventKind:'ONSET'},
    ],
    corrections:[
      {candidateId:'drums-onset-1',decision:'ADJUST',startMs:1985},
      {candidateId:'tempo-120',decision:'REJECT',note:'human review prefers another pulse interpretation'},
    ],
  };

  assert.equal(session.inputs[0].role,'DRUMS');
  assert.equal(session.candidates[0].bpm,120);
  assert.equal(session.candidates[0].confidence,.8);
  assert.equal(session.corrections[0].decision,'ADJUST');
  assert.equal(session.corrections[0].startMs,1985);
  assert.equal(session.corrections[1].decision,'REJECT');
});
