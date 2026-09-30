import test from 'node:test';
import assert from 'node:assert/strict';
import { parsePcmWav } from '../src/music/authoring/wav.js';

function wav16(channels:number,sampleRate:number,frames:number[][],audioFormat=1,bitsPerSample=16):Uint8Array{
  const bytesPerSample=bitsPerSample/8;
  const dataSize=frames.length*channels*bytesPerSample;
  const out=new Uint8Array(44+dataSize);
  const v=new DataView(out.buffer);
  const text=(off:number,s:string)=>{for(let i=0;i<s.length;i++)out[off+i]=s.charCodeAt(i);};
  text(0,'RIFF'); v.setUint32(4,36+dataSize,true); text(8,'WAVE');
  text(12,'fmt '); v.setUint32(16,16,true); v.setUint16(20,audioFormat,true); v.setUint16(22,channels,true);
  v.setUint32(24,sampleRate,true); v.setUint32(28,sampleRate*channels*bytesPerSample,true);
  v.setUint16(32,channels*bytesPerSample,true); v.setUint16(34,bitsPerSample,true);
  text(36,'data'); v.setUint32(40,dataSize,true);
  let o=44;
  for(const frame of frames) for(let c=0;c<channels;c++){v.setInt16(o,frame[c]??0,true);o+=2;}
  return out;
}

test('parses mono 16-bit PCM deterministically',()=>{
  const wav=parsePcmWav(wav16(1,1000,[[0],[16384],[-16384]]));
  assert.equal(wav.sampleRate,1000);
  assert.equal(wav.channels,1);
  assert.equal(wav.bitsPerSample,16);
  assert.equal(wav.frames,3);
  assert.equal(wav.durationMs,3);
  assert.ok(Math.abs(wav.mono[1]-.5)<.001);
});

test('downmixes stereo PCM to mono',()=>{
  const wav=parsePcmWav(wav16(2,1000,[[16384,-16384],[16384,16384]]));
  assert.ok(Math.abs(wav.mono[0])<.001);
  assert.ok(Math.abs(wav.mono[1]-.5)<.001);
});

test('refuses truncated RIFF chunks',()=>{
  const bytes=wav16(1,1000,[[0],[1]]);
  assert.throws(()=>parsePcmWav(bytes.slice(0,43)),/WAV_TRUNCATED/);
});

test('refuses non-PCM format',()=>{
  assert.throws(()=>parsePcmWav(wav16(1,1000,[[0]],3)),/WAV_FORMAT/);
});

test('refuses unsupported bit depth',()=>{
  const bytes=wav16(1,1000,[[0]],1,16);
  new DataView(bytes.buffer).setUint16(34,8,true);
  assert.throws(()=>parsePcmWav(bytes),/WAV_BIT_DEPTH/);
});

test('refuses impossible channel or sample metadata',()=>{
  const zeroChannels=wav16(1,1000,[[0]]); new DataView(zeroChannels.buffer).setUint16(22,0,true);
  assert.throws(()=>parsePcmWav(zeroChannels),/WAV_METADATA/);
  const zeroRate=wav16(1,1000,[[0]]); new DataView(zeroRate.buffer).setUint32(24,0,true);
  assert.throws(()=>parsePcmWav(zeroRate),/WAV_METADATA/);
});
