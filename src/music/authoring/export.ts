import type { PatternEventKind, PatternMap } from '../patternMap/types.js';
import { assertValidPatternMap } from '../patternMap/validate.js';
import type { AuthoringSession } from './types.js';
import { resolvedCandidates, type ResolvedCandidate } from './session.js';

function defaultEventKind(candidate:ResolvedCandidate):PatternEventKind|undefined{
  if(candidate.eventKind) return candidate.eventKind;
  if(candidate.kind==='ONSET') return 'ONSET';
  if(candidate.kind==='REPEATED_CELL') return 'CELL';
  if(candidate.kind==='PHRASE') return 'PHRASE_START';
  if(candidate.kind==='DOWNBEAT') return 'ACCENT';
  return undefined;
}

export function exportPatternMap(session:AuthoringSession,skeleton:PatternMap):PatternMap{
  const map:PatternMap=JSON.parse(JSON.stringify(skeleton)) as PatternMap;
  map.trackId=session.trackId;
  map.durationMs=session.durationMs;
  const resolved=resolvedCandidates(session);
  const exportedEventIds=new Set<string>();

  for(const candidate of resolved){
    if(candidate.kind==='BPM'){
      if(candidate.targetRegionIndex===undefined) continue;
      const region=map.tempoRegions[candidate.targetRegionIndex];
      if(!region) throw new Error(`AUTHORING_TEMPO_TARGET: no tempo region ${candidate.targetRegionIndex}`);
      if(candidate.bpm===undefined) throw new Error(`AUTHORING_TEMPO_VALUE: ${candidate.id} has no bpm`);
      region.bpm=candidate.bpm;
      continue;
    }
    if(candidate.kind==='METER'){
      if(candidate.targetRegionIndex===undefined) continue;
      const region=map.meterRegions[candidate.targetRegionIndex];
      if(!region) throw new Error(`AUTHORING_METER_TARGET: no meter region ${candidate.targetRegionIndex}`);
      if(candidate.meterNumerator===undefined||candidate.meterDenominator===undefined) throw new Error(`AUTHORING_METER_VALUE: ${candidate.id} is incomplete`);
      region.numerator=candidate.meterNumerator;
      region.denominator=candidate.meterDenominator;
      continue;
    }
    if(candidate.kind==='ALIGNMENT'||candidate.kind==='SECTION_BOUNDARY') continue;
    const eventKind=defaultEventKind(candidate);
    if(!candidate.role||candidate.startMs===undefined||!eventKind) continue;
    const endMs=candidate.endMs??candidate.startMs+1;
    map.layers[candidate.role].events.push({
      id:candidate.id,
      role:candidate.role,
      kind:eventKind,
      startMs:candidate.startMs,
      endMs,
      strength:1,
    });
    exportedEventIds.add(candidate.id);
  }

  for(const candidate of resolved.filter(x=>x.kind==='ALIGNMENT')){
    if(candidate.startMs===undefined) throw new Error(`AUTHORING_ALIGNMENT_TIME: ${candidate.id} has no startMs`);
    const eventIds=candidate.relatedCandidateIds??[];
    const missing=eventIds.filter(id=>!exportedEventIds.has(id));
    if(missing.length) throw new Error(`AUTHORING_ALIGNMENT_UNRESOLVED: ${candidate.id} references ${missing.join(',')}`);
    map.alignments.push({
      id:candidate.id,
      startMs:candidate.startMs,
      endMs:candidate.endMs??candidate.startMs+1,
      eventIds:[...eventIds],
      label:candidate.label,
    });
  }

  assertValidPatternMap(map);
  return map;
}
