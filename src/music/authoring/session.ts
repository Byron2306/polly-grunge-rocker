import type { AnalysisCandidate, AuthoringSession, CandidateCorrection } from './types.js';

export interface ResolvedCandidate extends AnalysisCandidate {
  authoritative:true;
  correctionDecision:'ACCEPT'|'ADJUST';
  targetRegionIndex?:number;
  correctionNote?:string;
}

function correctionIndex(session:AuthoringSession):Map<string,CandidateCorrection>{
  const known=new Set(session.candidates.map(x=>x.id));
  const map=new Map<string,CandidateCorrection>();
  for(const correction of session.corrections){
    if(!known.has(correction.candidateId)) throw new Error(`AUTHORING_CORRECTION_UNKNOWN: ${correction.candidateId}`);
    if(map.has(correction.candidateId)) throw new Error(`AUTHORING_CORRECTION_DUPLICATE: ${correction.candidateId}`);
    map.set(correction.candidateId,correction);
  }
  return map;
}

export function resolveCandidate(session:AuthoringSession,candidateId:string):ResolvedCandidate|null{
  const candidate=session.candidates.find(x=>x.id===candidateId);
  if(!candidate) throw new Error(`AUTHORING_CANDIDATE_UNKNOWN: ${candidateId}`);
  const correction=correctionIndex(session).get(candidateId);
  if(!correction||correction.decision==='REJECT') return null;
  const adjusted:AnalysisCandidate={...candidate};
  const mutable=adjusted as unknown as Record<string,unknown>;
  const fields=['startMs','endMs','bpm','meterNumerator','meterDenominator','eventKind','role','label','relatedCandidateIds'] as const;
  if(correction.decision==='ADJUST') for(const field of fields){
    const value=correction[field];
    if(value!==undefined) mutable[field]=value;
  }
  return {
    ...adjusted,
    authoritative:true,
    correctionDecision:correction.decision,
    targetRegionIndex:correction.targetRegionIndex,
    correctionNote:correction.note,
  };
}

export function resolvedCandidates(session:AuthoringSession):ResolvedCandidate[]{
  correctionIndex(session);
  const out:ResolvedCandidate[]=[];
  for(const candidate of session.candidates){
    const resolved=resolveCandidate(session,candidate.id);
    if(resolved) out.push(resolved);
  }
  return out;
}
