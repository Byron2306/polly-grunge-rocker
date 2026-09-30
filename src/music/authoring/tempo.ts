import type { AnalysisCandidate } from './types.js';

export interface TempoConfig {
  minBpm?:number;
  maxBpm?:number;
  bucketBpm?:number;
}

export function inferTempoCandidates(
  onsets:readonly AnalysisCandidate[],
  sourceId:string,
  config:TempoConfig={},
):AnalysisCandidate[]{
  const minBpm=config.minBpm??40;
  const maxBpm=config.maxBpm??240;
  const bucket=config.bucketBpm??.5;
  const times=onsets
    .filter(x=>x.kind==='ONSET'&&typeof x.startMs==='number')
    .map(x=>x.startMs as number)
    .sort((a,b)=>a-b);
  if(times.length<2) return [];

  const scores=new Map<number,number>();
  const add=(bpm:number,weight:number)=>{
    if(bpm<minBpm||bpm>maxBpm) return;
    const key=Math.round(bpm/bucket)*bucket;
    scores.set(key,(scores.get(key)??0)+weight);
  };
  for(let i=1;i<times.length;i++){
    const dt=times[i]-times[i-1];
    if(dt<=0) continue;
    const bpm=60000/dt;
    add(bpm,1);
    add(bpm/2,.6);
    add(bpm*2,.6);
  }
  const maxScore=Math.max(...scores.values(),0);
  return [...scores.entries()]
    .map(([bpm,score])=>({
      id:`${sourceId}:tempo:${Math.round(bpm*100)}`,
      kind:'BPM' as const,
      confidence:maxScore===0?0:Math.max(0,Math.min(1,score/maxScore)),
      sourceId,
      bpm,
      label:'tempo candidate',
    }))
    .sort((a,b)=>b.confidence-a.confidence||(a.bpm??0)-(b.bpm??0));
}
