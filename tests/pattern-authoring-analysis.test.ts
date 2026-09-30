import test from 'node:test';
import assert from 'node:assert/strict';
import { detectOnsetCandidates } from '../src/music/authoring/onsets.js';
import { inferTempoCandidates } from '../src/music/authoring/tempo.js';
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
