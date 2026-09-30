import test from 'node:test';
import assert from 'node:assert/strict';
import { parsePatternMapJson } from '../src/music/patternMap/load.js';

const valid={
  schema:'polly.pattern-map.v1',trackId:'load-reference',durationMs:4000,
  tempoRegions:[{startMs:0,endMs:4000,bpm:120}],
  meterRegions:[{startMs:0,endMs:4000,numerator:4,denominator:4}],
  sections:[{id:'whole',label:'Whole',startMs:0,endMs:4000}],
  layers:{
    DRUMS:{role:'DRUMS',events:[]},BASS:{role:'BASS',events:[]},RHYTHM_GUITAR:{role:'RHYTHM_GUITAR',events:[]},LEAD_KEYS:{role:'LEAD_KEYS',events:[]},VOCALS:{role:'VOCALS',events:[]},
  },alignments:[],
};

test('valid JSON loads only after validation',()=>{assert.equal(parsePatternMapJson(JSON.stringify(valid)).trackId,'load-reference');});
test('malformed JSON uses PATTERN_MAP_JSON prefix',()=>{assert.throws(()=>parsePatternMapJson('{nope'),/PATTERN_MAP_JSON:/);});
test('wrong schema uses PATTERN_MAP_SCHEMA prefix',()=>{assert.throws(()=>parsePatternMapJson(JSON.stringify({...valid,schema:'wrong'})),/PATTERN_MAP_SCHEMA:/);});
test('structurally invalid map uses PATTERN_MAP_VALIDATION prefix',()=>{
  const bad={...valid,durationMs:-1};
  assert.throws(()=>parsePatternMapJson(JSON.stringify(bad)),/PATTERN_MAP_VALIDATION:/);
});
test('arbitrary object missing canonical layers is refused',()=>{assert.throws(()=>parsePatternMapJson(JSON.stringify({schema:'polly.pattern-map.v1'})),/PATTERN_MAP_VALIDATION:/);});
test('duplicate ids from imported JSON are refused',()=>{
  const bad=structuredClone(valid) as any;
  bad.layers.DRUMS.events=[{id:'dup',role:'DRUMS',kind:'ONSET',startMs:10,endMs:20,strength:1}];
  bad.layers.BASS.events=[{id:'dup',role:'BASS',kind:'ONSET',startMs:10,endMs:20,strength:1}];
  assert.throws(()=>parsePatternMapJson(JSON.stringify(bad)),/DUPLICATE_ID/);
});
