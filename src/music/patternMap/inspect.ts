import type { MusicalRole, PatternMap } from './types.js';
import { alignmentsAt, eventsAt, positionAt } from './query.js';

const ROLES:readonly MusicalRole[]=['DRUMS','BASS','RHYTHM_GUITAR','LEAD_KEYS','VOCALS'];

export function formatPatternMapInspection(map:PatternMap,trackTimeMs:number):string {
  const pos=positionAt(map,trackTimeMs);
  const lines=[
    `track: ${map.trackId}`,
    `timeMs: ${trackTimeMs}`,
    `bpm: ${pos.tempoBpm}`,
    `meter: ${pos.meterNumerator}/${pos.meterDenominator}`,
    `section: ${pos.sectionId??'none'}`,
    `beatIndex: ${pos.beatIndex}`,
    `beatPhase: ${pos.beatPhase.toFixed(3)}`,
  ];
  for(const role of ROLES){
    const ids=eventsAt(map,role,trackTimeMs,150).map(e=>e.id);
    lines.push(`${role}: ${ids.length?ids.join(', '):'-'}`);
  }
  const alignmentIds=alignmentsAt(map,trackTimeMs,150).map(a=>a.id);
  lines.push(`alignments: ${alignmentIds.length?alignmentIds.join(', '):'-'}`);
  return lines.join('\n');
}
