import test from 'node:test';
import assert from 'node:assert/strict';
import type {
  MusicalRole,
  PatternMap,
} from '../src/music/patternMap/types.js';

const ROLES:MusicalRole[]=['DRUMS','BASS','RHYTHM_GUITAR','LEAD_KEYS','VOCALS'];

test('pattern map fixture uses the canonical five-role grammar',()=>{
  const map:PatternMap={
    schema:'polly.pattern-map.v1',
    trackId:'rat-hole-reference',
    durationMs:8000,
    tempoRegions:[{startMs:0,endMs:8000,bpm:120}],
    meterRegions:[{startMs:0,endMs:8000,numerator:4,denominator:4}],
    sections:[{id:'intro',label:'Intro',startMs:0,endMs:8000}],
    layers:{
      DRUMS:{role:'DRUMS',events:[{id:'drum-1',role:'DRUMS',kind:'ACCENT',startMs:1000,endMs:1100,strength:0.8}]},
      BASS:{role:'BASS',events:[]},
      RHYTHM_GUITAR:{role:'RHYTHM_GUITAR',events:[]},
      LEAD_KEYS:{role:'LEAD_KEYS',events:[{id:'lead-1',role:'LEAD_KEYS',kind:'PHRASE_START',startMs:1000,endMs:1200,strength:0.7}]},
      VOCALS:{role:'VOCALS',events:[]},
    },
    alignments:[{id:'align-1',startMs:1000,endMs:1100,eventIds:['drum-1','lead-1'],label:'opening lock'}],
  };

  assert.deepEqual(ROLES,['DRUMS','BASS','RHYTHM_GUITAR','LEAD_KEYS','VOCALS']);
  assert.equal(map.layers.DRUMS.events[0].kind,'ACCENT');
  assert.deepEqual(map.alignments[0].eventIds,['drum-1','lead-1']);
});
