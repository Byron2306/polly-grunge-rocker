import type { MusicalRole, PatternEventKind } from '../patternMap/types.js';

export type AnalysisCandidateKind=
  | 'BPM'
  | 'DOWNBEAT'
  | 'METER'
  | 'ONSET'
  | 'REPEATED_CELL'
  | 'PHRASE'
  | 'SECTION_BOUNDARY'
  | 'ALIGNMENT';

export interface AnalysisCandidate {
  id:string;
  kind:AnalysisCandidateKind;
  confidence:number;
  sourceId:string;
  role?:MusicalRole;
  startMs?:number;
  endMs?:number;
  bpm?:number;
  meterNumerator?:number;
  meterDenominator?:number;
  eventKind?:PatternEventKind;
  relatedCandidateIds?:string[];
  label?:string;
}

export interface AuthoringInput {
  id:string;
  kind:'WAV'|'MIDI_HINTS'|'EVENT_HINTS';
  role?:MusicalRole;
  path?:string;
  durationMs?:number;
}

export type CorrectionDecision='ACCEPT'|'REJECT'|'ADJUST';

export interface CandidateCorrection {
  candidateId:string;
  decision:CorrectionDecision;
  startMs?:number;
  endMs?:number;
  bpm?:number;
  meterNumerator?:number;
  meterDenominator?:number;
  eventKind?:PatternEventKind;
  role?:MusicalRole;
  label?:string;
  relatedCandidateIds?:string[];
  targetRegionIndex?:number;
  note?:string;
}

export interface AuthoringSession {
  schema:'polly.authoring-session.v1';
  sessionId:string;
  trackId:string;
  durationMs:number;
  inputs:AuthoringInput[];
  candidates:AnalysisCandidate[];
  corrections:CandidateCorrection[];
}
