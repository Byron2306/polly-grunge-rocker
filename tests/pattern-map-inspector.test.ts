import test from 'node:test';
import assert from 'node:assert/strict';
import { REFERENCE_GRUNGE_PATTERN_MAP } from '../src/music/patternMap/fixtures.js';
import { validatePatternMap } from '../src/music/patternMap/validate.js';
import { formatPatternMapInspection } from '../src/music/patternMap/inspect.js';


test('reference grunge fixture covers all five roles and validates',()=>{
  const map=REFERENCE_GRUNGE_PATTERN_MAP;
  assert.equal(validatePatternMap(map).ok,true);
  assert.equal(Object.values(map.layers).every(layer=>layer.events.length>0),true);
  assert.equal(Object.values(map.layers).flatMap(layer=>layer.events).some(event=>event.kind==='RESOLUTION'),true);
  assert.equal(map.alignments.some(a=>a.eventIds.length>=3),true);
  assert.equal(map.sections.length>=2,true);
  assert.equal(map.durationMs>=8000,true);
});

test('inspector renders musical position, role events and alignments',()=>{
  const text=formatPatternMapInspection(REFERENCE_GRUNGE_PATTERN_MAP,2000);
  assert.match(text,/rat-hole-grunge-reference-v1/);
  assert.match(text,/bpm: 120/);
  assert.match(text,/meter: 4\/4/);
  assert.match(text,/section: verse/);
  assert.match(text,/beatIndex: 4/);
  assert.match(text,/DRUMS: drums-accent-1/);
  assert.match(text,/BASS: bass-cell-1/);
  assert.match(text,/RHYTHM_GUITAR: rhythm-cell-1/);
  assert.match(text,/LEAD_KEYS: lead-phrase-1/);
  assert.match(text,/VOCALS: vocals-call-1/);
  assert.match(text,/alignments: full-band-lock-1/);
});
