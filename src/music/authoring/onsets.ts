import type { MusicalRole } from '../patternMap/types.js';
import type { AnalysisCandidate } from './types.js';
import type { PcmWav } from './wav.js';

export interface OnsetConfig {
  windowMs?:number;
  minGapMs?:number;
  threshold?:number;
}

export function detectOnsetCandidates(
  wav:PcmWav,
  sourceId:string,
  role:MusicalRole,
  config:OnsetConfig={},
):AnalysisCandidate[]{
  const windowMs=config.windowMs??20;
  const minGapMs=config.minGapMs??80;
  const threshold=config.threshold??0.08;
  const window=Math.max(1,Math.round(wav.sampleRate*windowMs/1000));
  if(wav.mono.length===0) return [];

  const energies:number[]=[];
  for(let start=0;start<wav.mono.length;start+=window){
    let sum=0;
    const end=Math.min(start+window,wav.mono.length);
    for(let i=start;i<end;i++) sum+=Math.abs(wav.mono[i]);
    energies.push(sum/Math.max(1,end-start));
  }
  const peak=Math.max(...energies,0);
  if(peak<threshold) return [];

  const out:AnalysisCandidate[]=[];
  let lastMs=-Infinity;
  for(let i=0;i<energies.length;i++){
    const energy=energies[i];
    const previous=i===0?0:energies[i-1];
    const baseline=i<4
      ? energies.slice(0,i).reduce((a,b)=>a+b,0)/Math.max(1,i)
      : energies.slice(i-4,i).reduce((a,b)=>a+b,0)/4;
    const rises=energy>=threshold&&energy>previous+threshold*.5&&energy>baseline+threshold*.35;
    if(!rises) continue;
    const startMs=i*window/wav.sampleRate*1000;
    if(startMs-lastMs<minGapMs) continue;
    const confidence=Math.max(0,Math.min(1,energy/Math.max(peak,threshold)));
    out.push({
      id:`${sourceId}:onset:${Math.round(startMs)}`,
      kind:'ONSET',
      confidence,
      sourceId,
      role,
      startMs,
      endMs:Math.min(wav.durationMs,startMs+windowMs),
      eventKind:'ONSET',
    });
    lastMs=startMs;
  }
  return out;
}
