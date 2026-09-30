export interface PcmWav {
  sampleRate:number;
  channels:number;
  bitsPerSample:16|24|32;
  frames:number;
  durationMs:number;
  mono:Float32Array;
}

const ascii=(bytes:Uint8Array,off:number,len:number):string=>String.fromCharCode(...bytes.slice(off,off+len));

export function parsePcmWav(bytes:Uint8Array):PcmWav {
  if(bytes.length<12||ascii(bytes,0,4)!=='RIFF'||ascii(bytes,8,4)!=='WAVE') throw new Error('WAV_HEADER: expected RIFF/WAVE');
  const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
  const declaredEnd=8+view.getUint32(4,true);
  if(declaredEnd>bytes.length) throw new Error('WAV_TRUNCATED: RIFF size exceeds available bytes');

  let format:number|undefined,channels:number|undefined,sampleRate:number|undefined,bits:number|undefined,blockAlign:number|undefined;
  let dataOffset:number|undefined,dataSize:number|undefined;
  let off=12;
  while(off+8<=declaredEnd){
    const id=ascii(bytes,off,4);
    const size=view.getUint32(off+4,true);
    const start=off+8;
    const end=start+size;
    if(end>declaredEnd||end>bytes.length) throw new Error(`WAV_TRUNCATED: chunk ${id} exceeds RIFF bounds`);
    if(id==='fmt '){
      if(size<16) throw new Error('WAV_TRUNCATED: fmt chunk too short');
      format=view.getUint16(start,true);
      channels=view.getUint16(start+2,true);
      sampleRate=view.getUint32(start+4,true);
      blockAlign=view.getUint16(start+12,true);
      bits=view.getUint16(start+14,true);
    } else if(id==='data'){
      dataOffset=start;
      dataSize=size;
    }
    off=end+(size&1);
  }

  if(format===undefined||dataOffset===undefined||dataSize===undefined) throw new Error('WAV_HEADER: fmt and data chunks are required');
  if(format!==1) throw new Error(`WAV_FORMAT: only PCM format 1 is supported, got ${format}`);
  if(channels===undefined||channels<=0||sampleRate===undefined||sampleRate<=0||blockAlign===undefined||blockAlign<=0) throw new Error('WAV_METADATA: channels, sampleRate and blockAlign must be positive');
  if(bits!==16&&bits!==24&&bits!==32) throw new Error(`WAV_BIT_DEPTH: unsupported PCM bit depth ${bits}`);
  const bytesPerSample=bits/8;
  const expectedAlign=channels*bytesPerSample;
  if(blockAlign!==expectedAlign||dataSize%blockAlign!==0) throw new Error('WAV_METADATA: inconsistent block alignment or data size');

  const frames=dataSize/blockAlign;
  const mono=new Float32Array(frames);
  const scale=bits===16?32768:bits===24?8388608:2147483648;
  for(let frame=0;frame<frames;frame++){
    let sum=0;
    for(let channel=0;channel<channels;channel++){
      const p=dataOffset+frame*blockAlign+channel*bytesPerSample;
      let sample:number;
      if(bits===16) sample=view.getInt16(p,true);
      else if(bits===24){
        let raw=bytes[p]|(bytes[p+1]<<8)|(bytes[p+2]<<16);
        if(raw&0x800000) raw|=0xff000000;
        sample=raw;
      } else sample=view.getInt32(p,true);
      sum+=sample/scale;
    }
    mono[frame]=sum/channels;
  }

  return {sampleRate,channels,bitsPerSample:bits,frames,durationMs:frames/sampleRate*1000,mono};
}
