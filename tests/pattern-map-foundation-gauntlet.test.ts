import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parsePatternMapJson } from '../src/music/patternMap/load.js';
import { alignmentsAt, eventsAt, positionAt } from '../src/music/patternMap/query.js';
import type { MusicalRole } from '../src/music/patternMap/types.js';

const ROLES:readonly MusicalRole[]=['DRUMS','BASS','RHYTHM_GUITAR','LEAD_KEYS','VOCALS'];
const MODULES=[
  'src/music/patternMap/types.ts',
  'src/music/patternMap/validate.ts',
  'src/music/patternMap/query.ts',
  'src/music/patternMap/load.ts',
  'src/music/patternMap/fixtures.ts',
  'src/music/patternMap/inspect.ts',
];

test('Pattern Map foundation stays deterministic pure and queryable',()=>{
  const json=readFileSync('data/pattern-maps/reference-grunge-v1.json','utf8');
  const map=parsePatternMapJson(json);

  const before=positionAt(map,3999);
  const after=positionAt(map,4000);
  assert.equal(before.tempoBpm,120);
  assert.equal(after.tempoBpm,60);

  for(const role of ROLES){
    const events=eventsAt(map,role,2000,0);
    assert.ok(events.length>=1,`expected ${role} event at 2000ms`);
  }

  const alignments=alignmentsAt(map,2000,0);
  assert.equal(alignments.some(x=>x.id==='full-band-lock-1'),true);

  for(const path of MODULES){
    const source=readFileSync(path,'utf8');
    assert.equal(source.includes('Phaser'),false,`${path} must not depend on Phaser`);
    assert.equal(source.includes('Date.now'),false,`${path} must not use wall clock time`);
    assert.equal(source.includes('AudioContext'),false,`${path} must not depend on WebAudio`);
  }

  const bad=JSON.parse(json) as {alignments:Array<{eventIds:string[]}>};
  bad.alignments[0].eventIds=['definitely-not-an-event'];
  assert.throws(
    ()=>parsePatternMapJson(JSON.stringify(bad)),
    /PATTERN_MAP_VALIDATION:.*UNKNOWN_EVENT/,
  );
});
