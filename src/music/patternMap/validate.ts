import type { MusicalRole, PatternMap, PatternEvent } from './types.js';

export interface PatternMapValidationIssue { code:string; path:string; message:string }
export interface PatternMapValidationResult { ok:boolean; issues:PatternMapValidationIssue[] }

const ROLES:readonly MusicalRole[]=['DRUMS','BASS','RHYTHM_GUITAR','LEAD_KEYS','VOCALS'];

function issue(issues:PatternMapValidationIssue[],code:string,path:string,message:string):void {
  issues.push({code,path,message});
}

function validateRange(
  issues:PatternMapValidationIssue[],
  path:string,
  startMs:number,
  endMs:number,
  durationMs:number,
):void {
  if(startMs<0||endMs<0) issue(issues,'NEGATIVE_TIME',path,'time values must be non-negative');
  if(endMs<=startMs||startMs>durationMs||endMs>durationMs) issue(issues,'INVALID_RANGE',path,`range must satisfy 0 <= startMs < endMs <= ${durationMs}`);
}

function validateRegions(
  issues:PatternMapValidationIssue[],
  regions:readonly {startMs:number;endMs:number}[],
  path:string,
  durationMs:number,
):void {
  for(let i=0;i<regions.length;i++){
    validateRange(issues,`${path}[${i}]`,regions[i].startMs,regions[i].endMs,durationMs);
    if(i>0&&regions[i].startMs<regions[i-1].endMs){
      issue(issues,'OVERLAPPING_REGION',`${path}[${i}]`,'region overlaps previous region');
    }
  }
}

export function validatePatternMap(map:PatternMap):PatternMapValidationResult {
  const issues:PatternMapValidationIssue[]=[];
  const durationMs=map.durationMs;

  if(durationMs<=0) issue(issues,'INVALID_RANGE','durationMs','durationMs must be greater than zero');

  validateRegions(issues,map.tempoRegions,'tempoRegions',durationMs);
  for(let i=0;i<map.tempoRegions.length;i++) if(map.tempoRegions[i].bpm<=0) issue(issues,'INVALID_BPM',`tempoRegions[${i}].bpm`,'bpm must be greater than zero');

  validateRegions(issues,map.meterRegions,'meterRegions',durationMs);
  for(let i=0;i<map.meterRegions.length;i++){
    const r=map.meterRegions[i];
    if(r.numerator<1||r.denominator<1) issue(issues,'INVALID_METER',`meterRegions[${i}]`,'meter numerator and denominator must be at least one');
  }

  for(let i=0;i<map.sections.length;i++) validateRange(issues,`sections[${i}]`,map.sections[i].startMs,map.sections[i].endMs,durationMs);

  const eventsById=new Map<string,PatternEvent>();
  for(const role of ROLES){
    const layer=(map.layers as Partial<Record<MusicalRole,typeof map.layers[MusicalRole]>>)[role];
    if(!layer){
      issue(issues,'MISSING_LAYER',`layers.${role}`,`missing canonical layer ${role}`);
      continue;
    }
    if(layer.role!==role) issue(issues,'MISSING_LAYER',`layers.${role}.role`,`layer role must be ${role}`);
    for(let i=0;i<layer.events.length;i++){
      const event=layer.events[i];
      const path=`layers.${role}.events[${i}]`;
      validateRange(issues,path,event.startMs,event.endMs,durationMs);
      if(event.strength<0||event.strength>1) issue(issues,'INVALID_STRENGTH',`${path}.strength`,'strength must be within 0..1');
      if(event.role!==role) issue(issues,'MISSING_LAYER',`${path}.role`,`event role must match layer ${role}`);
      if(eventsById.has(event.id)) issue(issues,'DUPLICATE_ID',`${path}.id`,`duplicate event id ${event.id}`);
      else eventsById.set(event.id,event);
    }
  }

  for(let i=0;i<map.alignments.length;i++){
    const alignment=map.alignments[i];
    const path=`alignments[${i}]`;
    validateRange(issues,path,alignment.startMs,alignment.endMs,durationMs);
    for(let j=0;j<alignment.eventIds.length;j++){
      const eventId=alignment.eventIds[j];
      const event=eventsById.get(eventId);
      if(!event){
        issue(issues,'UNKNOWN_EVENT',`${path}.eventIds[${j}]`,`unknown event id ${eventId}`);
        continue;
      }
      const intersects=event.startMs<alignment.endMs&&event.endMs>alignment.startMs;
      if(!intersects) issue(issues,'INCOMPATIBLE_ALIGNMENT',`${path}.eventIds[${j}]`,`event ${eventId} does not intersect alignment window`);
    }
  }

  return {ok:issues.length===0,issues};
}

export function assertValidPatternMap(map:PatternMap):void {
  const result=validatePatternMap(map);
  if(result.ok) return;
  throw new Error(result.issues.map(x=>`${x.code} ${x.path}: ${x.message}`).join('\n'));
}
