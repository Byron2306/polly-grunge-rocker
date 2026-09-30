import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { detectOnsetCandidates } from '../src/music/authoring/onsets.js';
import { inferTempoCandidates } from '../src/music/authoring/tempo.js';
import { findAlignmentCandidates } from '../src/music/authoring/align.js';
import { exportPatternMap } from '../src/music/authoring/export.js';
import { formatAuthoringReport } from '../src/music/authoring/inspect.js';
import type { AnalysisCandidate, AuthoringSession } from '../src/music/authoring/types.js';
import type { PcmWav } from '../src/music/authoring/wav.js';
import type { PatternMap } from '../src/music/patternMap/types.js';
import { parsePatternMapJson } from '../src/music/patternMap/load.js';

function pulseWav():PcmWav{
  const mono=new Float32Array(3000);
  for(const t of [500,1000,1500,2000,2500]) for(let i=t;i<t+20;i++) mono[i]=1;
  return {sampleRate:1000,channels:1,bitsPerSample:16,frames:mono.length,durationMs:3000,mono};
}

function skeleton():PatternMap{
  return {
    schema:'polly.pattern-map.v1',trackId:'gauntlet',durationMs:3000,
    tempoRegions:[{startMs:0,endMs:3000,bpm:120}],meterRegions:[{startMs:0,endMs:3000,numerator:4,denominator:4}],
    sections:[{id:'all',label:'All',startMs:0,endMs:3000}],
    layers:{DRUMS:{role:'DRUMS',events:[]},BASS:{role:'BASS',events:[]},RHYTHM_GUITAR:{role:'RHYTHM_GUITAR',events:[]},LEAD_KEYS:{role:'LEAD_KEYS',events:[]},VOCALS:{role:'VOCALS',events:[]}},alignments:[],
  };
}

test('Pattern Map authoring stays advisory until human review and exports validated truth',()=>{
  const drumOnsets=detectOnsetCandidates(pulseWav(),'drums','DRUMS');
  const tempos=inferTempoCandidates(drumOnsets,'drums');
  assert.ok(drumOnsets.length>=5);
  assert.ok(tempos.some(x=>Math.abs((x.bpm??0)-120)<1));

  const events:AnalysisCandidate[]=[
    {id:'d',kind:'ONSET',confidence:.9,sourceId:'drums',role:'DRUMS',startMs:1000,endMs:1050,eventKind:'ONSET'},
    {id:'b',kind:'ONSET',confidence:.8,sourceId:'bass',role:'BASS',startMs:1010,endMs:1060,eventKind:'ONSET'},
    {id:'r',kind:'REPEATED_CELL',confidence:.8,sourceId:'rhythm',role:'RHYTHM_GUITAR',startMs:1020,endMs:1080,eventKind:'CELL'},
    {id:'l',kind:'PHRASE',confidence:.7,sourceId:'lead',role:'LEAD_KEYS',startMs:1005,endMs:1070,eventKind:'PHRASE_START'},
    {id:'v',kind:'ONSET',confidence:.75,sourceId:'vocals',role:'VOCALS',startMs:995,endMs:1060,eventKind:'ONSET'},
  ];
  const alignment=findAlignmentCandidates(events,40,3)[0];
  assert.ok(alignment);
  const unreviewed:AuthoringSession={schema:'polly.authoring-session.v1',sessionId:'g',trackId:'gauntlet',durationMs:3000,inputs:[],candidates:[...events,alignment],corrections:[]};
  const report=formatAuthoringReport(unreviewed);
  assert.match(report,/confidence=/);
  assert.match(report,/DRUMS/);
  assert.match(report,/UNREVIEWED/);
  assert.equal(exportPatternMap(unreviewed,skeleton()).layers.DRUMS.events.length,0);

  const reviewed:AuthoringSession={...unreviewed,corrections:[
    ...events.map(x=>({candidateId:x.id,decision:'ACCEPT' as const})),
    {candidateId:alignment.id,decision:'ACCEPT' as const},
  ]};
  const exported=exportPatternMap(reviewed,skeleton());
  assert.equal(exported.layers.DRUMS.events.length,1);
  assert.equal(exported.layers.VOCALS.events.length,1);
  assert.equal(exported.alignments.length,1);
  assert.equal(exported.alignments[0].eventIds.length>=3,true);
  const loaded=parsePatternMapJson(JSON.stringify(exported));
  assert.equal(loaded.schema,'polly.pattern-map.v1');

  const modules=['types.ts','wav.ts','onsets.ts','tempo.ts','align.ts','session.ts','export.ts','inspect.ts'];
  for(const file of modules){
    const source=readFileSync(`src/music/authoring/${file}`,'utf8');
    assert.equal(source.includes('Phaser'),false,`${file} must not import Phaser`);
    assert.equal(source.includes('fetch('),false,`${file} must not call network fetch`);
    assert.equal(source.includes('http://'),false,`${file} must not contain network endpoints`);
    assert.equal(source.includes('https://'),false,`${file} must not contain network endpoints`);
  }
});
