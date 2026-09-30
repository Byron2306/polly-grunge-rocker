export type MusicalRole=
  | 'DRUMS'
  | 'BASS'
  | 'RHYTHM_GUITAR'
  | 'LEAD_KEYS'
  | 'VOCALS';

export interface TempoRegion {
  startMs:number;
  endMs:number;
  bpm:number;
}

export interface MeterRegion {
  startMs:number;
  endMs:number;
  numerator:number;
  denominator:number;
}

export interface Section {
  id:string;
  label:string;
  startMs:number;
  endMs:number;
}

export type PatternEventKind=
  | 'ONSET'
  | 'ACCENT'
  | 'CELL'
  | 'PHRASE_START'
  | 'PHRASE_END'
  | 'FILL'
  | 'REST'
  | 'TENSION'
  | 'RESOLUTION';

export interface PatternEvent {
  id:string;
  role:MusicalRole;
  kind:PatternEventKind;
  startMs:number;
  endMs:number;
  strength:number;
  patternId?:string;
}

export interface LayerMap {
  role:MusicalRole;
  events:PatternEvent[];
}

export interface AlignmentEvent {
  id:string;
  startMs:number;
  endMs:number;
  eventIds:string[];
  label?:string;
}

export interface PatternMap {
  schema:'polly.pattern-map.v1';
  trackId:string;
  durationMs:number;
  tempoRegions:TempoRegion[];
  meterRegions:MeterRegion[];
  sections:Section[];
  layers:Record<MusicalRole,LayerMap>;
  alignments:AlignmentEvent[];
}
