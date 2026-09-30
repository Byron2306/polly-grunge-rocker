import test from 'node:test';
import assert from 'node:assert/strict';
import type { PatternMap } from '../src/music/patternMap/types.js';
import { alignmentsAt, eventsAt, positionAt } from '../src/music/patternMap/query.js';

const map=():PatternMap=>({
  schema:'polly.pattern-map.v1',trackId:'query-reference',durationMs:8000,
  tempoRegions:[{startMs:0,endMs:4000,bpm:120},{startMs:4000,endMs:8000,bpm:60}],
  meterRegions:[{startMs:0,endMs:8000,numerator:4,denominator:4}],
  sections:[{id:'a',label:'A',startMs:0,endMs:4000},{id:'b',label:'B',startMs:4000,endMs:8000}],
  layers:{
    DRUMS:{role:'DRUMS',events:[{id:'d1',role:'DRUMS',kind:'ACCENT',startMs:950,endMs:1050,strength:1}]},
    BASS:{role:'BASS',events:[]},RHYTHM_GUITAR:{role:'RHYTHM_GUITAR',events:[]},LEAD_KEYS:{role:'LEAD_KEYS',events:[]},VOCALS:{role:'VOCALS',events:[]},
  },
  alignments:[{id:'lock',startMs:980,endMs:1020,eventIds:['d1']}],
});

test('musical position resolves deterministic beat and section state',()=>{
  const m=map();
  assert.equal(positionAt(m,0).beatIndex,0);
  assert.equal(positionAt(m,500).beatIndex,1);
  assert.equal(positionAt(m,500).beatPhase,0);
  assert.equal(positionAt(m,3999).tempoBpm,120);
  assert.equal(positionAt(m,4000).tempoBpm,60);
  assert.equal(positionAt(m,4000).sectionId,'b');
  assert.equal(positionAt(m,4000).beatPhase,0);
});

test('positionAt rejects time outside the track',()=>{
  const m=map();
  assert.throws(()=>positionAt(m,-1));
  assert.throws(()=>positionAt(m,8001));
});

test('sparse role queries return empty arrays',()=>{assert.deepEqual(eventsAt(map(),'BASS',1000,50),[]);});

test('event query uses inclusive tolerance without unrelated events',()=>{
  const m=map();
  assert.deepEqual(eventsAt(m,'DRUMS',900,50).map(x=>x.id),['d1']);
  assert.deepEqual(eventsAt(m,'DRUMS',899,50),[]);
});

test('alignment query returns only nearby alignment windows',()=>{
  const m=map();
  assert.deepEqual(alignmentsAt(m,950,30).map(x=>x.id),['lock']);
  assert.deepEqual(alignmentsAt(m,900,30),[]);
});
