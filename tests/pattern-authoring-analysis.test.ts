import test from 'node:test';
import assert from 'node:assert/strict';
import { detectOnsetCandidates } from '../src/music/authoring/onsets.js';
import { inferTempoCandidates } from '../src/music/authoring/tempo.js';
import { findAlignmentCandidates } from '../src/music/authoring/align.js';
import type { AnalysisCandidate } from '../src/music/authoring/types.js';
import type { PcmWav } from '../src/music/authoring/wav.js';

function pulseWav(timesMs:number[],durationMs=4000):PcmWav{
  const sampleRate=1000;
  const mono=new Float32Array(durationMs);
  for(const t of timesMs) for(let i=t;i<Math.min(t+20,mono.length);i++) mono[i]=1;
  return {sampleRate,channels:1,bitsPerSample:16,frames:mono.length,durationMs,mono};
}

test('detects deterministic onset candidates near synthetic pulses and silence stays silent',()=>{
  const wav=pulseWav([500,1000,1500,2000,2500,3000]);
  const a=detectOnsetCandidates(wav,'drums','DRUMS');
  const b=detectOnsetCandidates(wav,'drums','DRUMS');
  assert.deepEqual(a,b);
  assert.equal(a.length,6);
  for(let i=0;i<a.length;i++) assert.ok(Math.abs((a[i].startMs??-999)-[500,1000,1500,2000,2500,3000][i])<=20);
  assert.deepEqual(detectOnsetCandidates(pulseWav([]),'silence','DRUMS'),[]);
});

test('tempo inference keeps 120 plus half-time and double-time suggestions separate',()=>{
  const onsets=detectOnsetCandidates(pulseWav([500,1000,1500,2000,2500,3000]),'drums','DRUMS');
  const a=inferTempoCandidates(onsets,'drums');
  const b=inferTempoCandidates(onsets,'drums');
  assert.deepEqual(a,b);
  assert.ok(Math.abs((a[0].bpm??0)-120)<1);
  assert.ok(a.some(x=>Math.abs((x.bpm??0)-60)<1));
  assert.ok(a.some(x=>Math.abs((x.bpm??0)-240)<1));
  assert.ok((a[0].confidence??0)>=.7);
});

const c=(id:string,role:'DRUMS'|'BASS'|'RHYTHM_GUITAR',startMs:number,confidence=.8):AnalysisCandidate=>({
  id,kind:'ONSET',confidence,sourceId:role.toLowerCase(),role,startMs,endMs:startMs+20,eventKind:'ONSET',
});

test('alignment clustering counts unique roles inside tolerance and ignores same-role inflation',()=>{
  const candidates=[c('d1','DRUMS',1000),c('d2','DRUMS',1005),c('b1','BASS',1020),c('r1','RHYTHM_GUITAR',1035)];
  const out=findAlignmentCandidates(candidates,40,3);
  assert.equal(out.length,1);
  assert.equal(out[0].kind,'ALIGNMENT');
  assert.equal(out[0].relatedCandidateIds?.includes('d1'),true);
  assert.equal(out[0].relatedCandidateIds?.includes('d2'),false);
  assert.equal(out[0].relatedCandidateIds?.includes('b1'),true);
  assert.equal(out[0].relatedCandidateIds?.includes('r1'),true);
});

test('alignment clustering rejects outside tolerance and remains deterministic and bounded',()=>{
  const far=[c('d','DRUMS',1000),c('b','BASS',1100),c('r','RHYTHM_GUITAR',1200)];
  assert.deepEqual(findAlignmentCandidates(far,40,3),[]);
  const dense:AnalysisCandidate[]=[];
  for(let i=0;i<50;i++){
    const base=i*100;
    dense.push(c(`d${i}`,'DRUMS',base),c(`b${i}`,'BASS',base+10),c(`r${i}`,'RHYTHM_GUITAR',base+20));
  }
  const a=findAlignmentCandidates(dense,40,3);
  const b=findAlignmentCandidates(dense,40,3);
  assert.deepEqual(a,b);
  assert.ok(a.length<=50);
});
