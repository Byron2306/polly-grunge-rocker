import type { MusicalRole } from '../patternMap/types.js';
import type { AnalysisCandidate } from './types.js';

const ROLES:readonly MusicalRole[]=['DRUMS','BASS','RHYTHM_GUITAR','LEAD_KEYS','VOCALS'];

export function findAlignmentCandidates(
  candidates:readonly AnalysisCandidate[],
  toleranceMs:number,
  minRoles:number,
):AnalysisCandidate[]{
  if(toleranceMs<0) throw new Error('ALIGNMENT_CONFIG: toleranceMs must be non-negative');
  if(minRoles<2||minRoles>ROLES.length) throw new Error('ALIGNMENT_CONFIG: minRoles must be within 2..5');
  const timed=candidates
    .filter(x=>x.role&&typeof x.startMs==='number'&&x.kind!=='BPM'&&x.kind!=='METER'&&x.kind!=='ALIGNMENT')
    .slice()
    .sort((a,b)=>(a.startMs as number)-(b.startMs as number)||a.id.localeCompare(b.id));

  const seen=new Set<string>();
  const out:AnalysisCandidate[]=[];
  for(const seed of timed){
    const nearby=timed.filter(x=>Math.abs((x.startMs as number)-(seed.startMs as number))<=toleranceMs);
    const byRole=new Map<MusicalRole,AnalysisCandidate[]>();
    for(const item of nearby){
      const role=item.role as MusicalRole;
      const bucket=byRole.get(role)??[];
      bucket.push(item);
      byRole.set(role,bucket);
    }
    if(byRole.size<minRoles) continue;
    const chosen=[...byRole.entries()]
      .sort((a,b)=>ROLES.indexOf(a[0])-ROLES.indexOf(b[0]))
      .map(([,items])=>items.slice().sort((a,b)=>b.confidence-a.confidence||(a.startMs as number)-(b.startMs as number)||a.id.localeCompare(b.id))[0]);
    const ids=chosen.map(x=>x.id);
    const key=ids.slice().sort().join('|');
    if(seen.has(key)) continue;
    seen.add(key);
    const starts=chosen.map(x=>x.startMs as number);
    const ends=chosen.map(x=>x.endMs??x.startMs as number);
    const spread=Math.max(...starts)-Math.min(...starts);
    const roleFactor=chosen.length/ROLES.length;
    const timingFactor=toleranceMs===0?(spread===0?1:0):Math.max(0,1-spread/(toleranceMs*2));
    const memberConfidence=chosen.reduce((sum,x)=>sum+x.confidence,0)/chosen.length;
    const confidence=Math.max(0,Math.min(1,.35*roleFactor+.35*timingFactor+.3*memberConfidence));
    const center=Math.round(starts.reduce((a,b)=>a+b,0)/starts.length);
    out.push({
      id:`alignment:${center}:${ids.join('+')}`,
      kind:'ALIGNMENT',
      confidence,
      sourceId:'alignment-analysis',
      startMs:Math.min(...starts),
      endMs:Math.max(...ends),
      relatedCandidateIds:ids,
      label:`${chosen.length}-role convergence`,
    });
  }
  return out.sort((a,b)=>(a.startMs??0)-(b.startMs??0)||a.id.localeCompare(b.id));
}
