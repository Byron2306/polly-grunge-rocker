import test from 'node:test';
import assert from 'node:assert/strict';
import type { PatternMap } from '../src/music/patternMap/types.js';
import { validatePatternMap } from '../src/music/patternMap/validate.js';

const base=():PatternMap=>({
  schema:'polly.pattern-map.v1',
  trackId:'validation-reference',
  durationMs:8000,
  tempoRegions:[{startMs:0,endMs:8000,bpm:120}],
  meterRegions:[{startMs:0,endMs:8000,numerator:4,denominator:4}],
  sections:[{id:'whole',label:'Whole',startMs:0,endMs:8000}],
  layers:{
    DRUMS:{role:'DRUMS',events:[{id:'d1',role:'DRUMS',kind:'ACCENT',startMs:1000,endMs:1100,strength:1}]},
    BASS:{role:'BASS',events:[{id:'b1',role:'BASS',kind:'CELL',startMs:1000,endMs:1200,strength:.7}]},
    RHYTHM_GUITAR:{role:'RHYTHM_GUITAR',events:[]},
    LEAD_KEYS:{role:'LEAD_KEYS',events:[]},
    VOCALS:{role:'VOCALS',events:[]},
  },
  alignments:[{id:'a1',startMs:1000,endMs:1100,eventIds:['d1','b1']}],
});

function codes(map:PatternMap):string[]{return validatePatternMap(map).issues.map(x=>x.code);}

test('valid minimal pattern map is accepted',()=>{assert.equal(validatePatternMap(base()).ok,true);});
test('negative time is refused',()=>{const m=base();m.sections[0].startMs=-1;assert.ok(codes(m).includes('NEGATIVE_TIME'));});
test('invalid range is refused',()=>{const m=base();m.sections[0].endMs=0;assert.ok(codes(m).includes('INVALID_RANGE'));});
test('non-positive bpm is refused',()=>{const m=base();m.tempoRegions[0].bpm=0;assert.ok(codes(m).includes('INVALID_BPM'));});
test('invalid meter is refused',()=>{const m=base();m.meterRegions[0].denominator=0;assert.ok(codes(m).includes('INVALID_METER'));});
test('strength outside zero to one is refused',()=>{const m=base();m.layers.DRUMS.events[0].strength=1.1;assert.ok(codes(m).includes('INVALID_STRENGTH'));});
test('duplicate event ids across layers are refused',()=>{const m=base();m.layers.BASS.events[0].id='d1';assert.ok(codes(m).includes('DUPLICATE_ID'));});
test('missing canonical layer is refused',()=>{const m=base();delete (m.layers as any).VOCALS;assert.ok(codes(m).includes('MISSING_LAYER'));});
test('overlapping tempo regions are refused but touching boundaries are valid',()=>{
  const bad=base();bad.tempoRegions=[{startMs:0,endMs:5000,bpm:120},{startMs:4000,endMs:8000,bpm:90}];assert.ok(codes(bad).includes('OVERLAPPING_REGION'));
  const good=base();good.tempoRegions=[{startMs:0,endMs:4000,bpm:120},{startMs:4000,endMs:8000,bpm:90}];assert.equal(validatePatternMap(good).issues.some(x=>x.code==='OVERLAPPING_REGION'),false);
});
test('unknown alignment event is refused',()=>{const m=base();m.alignments[0].eventIds.push('ghost');assert.ok(codes(m).includes('UNKNOWN_EVENT'));});
test('temporally incompatible alignment is refused',()=>{const m=base();m.alignments[0]={id:'a1',startMs:3000,endMs:3100,eventIds:['d1','b1']};assert.ok(codes(m).includes('INCOMPATIBLE_ALIGNMENT'));});
