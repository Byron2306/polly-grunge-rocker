import type { AlignmentEvent, MeterRegion, MusicalRole, PatternEvent, PatternMap, TempoRegion } from './types.js';

export interface MusicalPosition {
  trackTimeMs:number;
  tempoBpm:number;
  meterNumerator:number;
  meterDenominator:number;
  beatIndex:number;
  beatPhase:number;
  sectionId:string|null;
}

function assertTrackTime(map:PatternMap,trackTimeMs:number):void {
  if(trackTimeMs<0||trackTimeMs>map.durationMs) throw new RangeError(`trackTimeMs must be within 0..${map.durationMs}`);
}

function regionAt<T extends {startMs:number;endMs:number}>(regions:readonly T[],timeMs:number,durationMs:number,label:string):T {
  const found=regions.find(r=>timeMs>=r.startMs&&(timeMs<r.endMs||(timeMs===durationMs&&r.endMs===durationMs)));
  if(!found) throw new Error(`PATTERN_MAP_QUERY: no ${label} region at ${timeMs}ms`);
  return found;
}

function beatsBefore(map:PatternMap,region:TempoRegion):number {
  let beats=0;
  for(const r of map.tempoRegions){
    if(r===region) break;
    beats+=(r.endMs-r.startMs)/(60000/r.bpm);
  }
  return beats;
}

export function positionAt(map:PatternMap,trackTimeMs:number):MusicalPosition {
  assertTrackTime(map,trackTimeMs);
  const tempo=regionAt<TempoRegion>(map.tempoRegions,trackTimeMs,map.durationMs,'tempo');
  const meter=regionAt<MeterRegion>(map.meterRegions,trackTimeMs,map.durationMs,'meter');
  const beatMs=60000/tempo.bpm;
  const elapsedInRegion=trackTimeMs-tempo.startMs;
  const localBeats=elapsedInRegion/beatMs;
  const totalBeats=beatsBefore(map,tempo)+localBeats;
  const rounded=Math.round(totalBeats);
  const stable=Math.abs(totalBeats-rounded)<1e-9?rounded:totalBeats;
  const beatIndex=Math.floor(stable);
  let beatPhase=stable-beatIndex;
  if(trackTimeMs===map.durationMs||Math.abs(beatPhase)<1e-9||Math.abs(beatPhase-1)<1e-9) beatPhase=0;
  const section=map.sections.find(s=>trackTimeMs>=s.startMs&&(trackTimeMs<s.endMs||(trackTimeMs===map.durationMs&&s.endMs===map.durationMs)))??null;
  return {
    trackTimeMs,
    tempoBpm:tempo.bpm,
    meterNumerator:meter.numerator,
    meterDenominator:meter.denominator,
    beatIndex,
    beatPhase,
    sectionId:section?.id??null,
  };
}

function intersectsWindow(startMs:number,endMs:number,timeMs:number,toleranceMs:number):boolean {
  if(toleranceMs<0) throw new RangeError('toleranceMs must be non-negative');
  const windowStart=timeMs-toleranceMs;
  const windowEnd=timeMs+toleranceMs;
  return endMs>=windowStart&&startMs<=windowEnd;
}

export function eventsAt(map:PatternMap,role:MusicalRole,trackTimeMs:number,toleranceMs:number):PatternEvent[] {
  assertTrackTime(map,trackTimeMs);
  const layer=map.layers[role];
  return layer.events.filter(e=>intersectsWindow(e.startMs,e.endMs,trackTimeMs,toleranceMs));
}

export function alignmentsAt(map:PatternMap,trackTimeMs:number,toleranceMs:number):AlignmentEvent[] {
  assertTrackTime(map,trackTimeMs);
  return map.alignments.filter(a=>intersectsWindow(a.startMs,a.endMs,trackTimeMs,toleranceMs));
}
