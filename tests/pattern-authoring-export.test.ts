import test from 'node:test';
import assert from 'node:assert/strict';
import { exportPatternMap } from '../src/music/authoring/export.js';
import type { AuthoringSession } from '../src/music/authoring/types.js';
import type { PatternMap } from '../src/music/patternMap/types.js';
import { validatePatternMap } from '../src/music/patternMap/validate.js';

const skeleton=():PatternMap=>({
  schema:'polly.pattern-map.v1',trackId:'authoring-test',durationMs:8000,
  tempoRegions:[{startMs:0,endMs:8000,bpm:120}],
  meterRegions:[{startMs:0,endMs:8000,numerator:4,denominator:4}],
  sections:[{id:'all',label:'All',startMs:0,endMs:8000}],
  layers:{
    DRUMS:{role:'DRUMS',events:[]},BASS:{role:'BASS',events:[]},RHYTHM_GUITAR:{role:'RHYTHM_GUITAR',events:[]},LEAD_KEYS:{role:'LEAD_KEYS',events:[]},VOCALS:{role:'VOCALS',events:[]},
  },alignments:[],
});

const session=():AuthoringSession=>({
  schema:'polly.authoring-session.v1',sessionId:'s',trackId:'authoring-test',durationMs:8000,inputs:[],
  candidates:[
    {id:'tempo',kind:'BPM',confidence:.8,sourceId:'mix',bpm:90},
    {id:'d',kind:'ONSET',confidence:.9,sourceId:'d',role:'DRUMS',startMs:2000,endMs:2050,eventKind:'ONSET'},
    {id:'b',kind:'ONSET',confidence:.8,sourceId:'b',role:'BASS',startMs:2005,endMs:2055,eventKind:'ONSET'},
    {id:'r',kind:'REPEATED_CELL',confidence:.7,sourceId:'r',role:'RHYTHM_GUITAR',startMs:2010,endMs:2060,eventKind:'CELL'},
    {id:'unreviewed',kind:'ONSET',confidence:1,sourceId:'v',role:'VOCALS',startMs:2100,endMs:2150,eventKind:'ONSET'},
    {id:'alignment',kind:'ALIGNMENT',confidence:.85,sourceId:'analysis',startMs:2000,endMs:2060,relatedCandidateIds:['d','b','r']},
  ],
  corrections:[
    {candidateId:'tempo',decision:'ACCEPT',targetRegionIndex:0},
    {candidateId:'d',decision:'ACCEPT'},
    {candidateId:'b',decision:'ADJUST',startMs:1995},
    {candidateId:'r',decision:'ACCEPT'},
    {candidateId:'alignment',decision:'ACCEPT'},
  ],
});

test('exports only reviewed events, mapped tempo, and reviewed alignment through Pattern Map validation',()=>{
  const map=exportPatternMap(session(),skeleton());
  assert.equal(map.tempoRegions[0].bpm,90);
  assert.equal(map.layers.DRUMS.events.some(x=>x.id==='d'),true);
  assert.equal(map.layers.BASS.events.find(x=>x.id==='b')?.startMs,1995);
  assert.equal(map.layers.VOCALS.events.some(x=>x.id==='unreviewed'),false);
  assert.deepEqual(map.alignments[0].eventIds,['d','b','r']);
  assert.equal(validatePatternMap(map).ok,true);
});

test('accepted BPM without explicit target mapping does not rewrite tempo truth',()=>{
  const s=session();
  s.corrections[0]={candidateId:'tempo',decision:'ACCEPT'};
  assert.equal(exportPatternMap(s,skeleton()).tempoRegions[0].bpm,120);
});

test('rejected candidates do not enter export',()=>{
  const s=session();
  s.corrections=s.corrections.map(x=>x.candidateId==='d'?{candidateId:'d',decision:'REJECT' as const}:x).filter(x=>x.candidateId!=='alignment');
  assert.equal(exportPatternMap(s,skeleton()).layers.DRUMS.events.length,0);
});

test('out-of-range human adjustment is refused by existing Pattern Map validator',()=>{
  const s=session();
  s.corrections=s.corrections.map(x=>x.candidateId==='d'?{candidateId:'d',decision:'ADJUST' as const,startMs:-5}:x).filter(x=>x.candidateId!=='alignment');
  assert.throws(()=>exportPatternMap(s,skeleton()),/NEGATIVE_TIME|INVALID_RANGE/);
});

test('duplicate exported IDs are refused',()=>{
  const s=session();
  s.candidates.push({...s.candidates.find(x=>x.id==='d')!});
  assert.throws(()=>exportPatternMap(s,skeleton()),/DUPLICATE_ID/);
});
