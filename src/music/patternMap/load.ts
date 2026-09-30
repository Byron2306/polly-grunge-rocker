import type { PatternMap } from './types.js';
import { assertValidPatternMap } from './validate.js';

function isObject(value:unknown):value is Record<string,unknown> {
  return typeof value==='object'&&value!==null&&!Array.isArray(value);
}

function hasArray(obj:Record<string,unknown>,key:string):boolean {
  return Array.isArray(obj[key]);
}

function preflight(value:unknown):asserts value is PatternMap {
  if(!isObject(value)) throw new Error('PATTERN_MAP_VALIDATION: root must be an object');
  if(typeof value.trackId!=='string') throw new Error('PATTERN_MAP_VALIDATION: trackId must be a string');
  if(typeof value.durationMs!=='number') throw new Error('PATTERN_MAP_VALIDATION: durationMs must be a number');
  if(!hasArray(value,'tempoRegions')) throw new Error('PATTERN_MAP_VALIDATION: tempoRegions must be an array');
  if(!hasArray(value,'meterRegions')) throw new Error('PATTERN_MAP_VALIDATION: meterRegions must be an array');
  if(!hasArray(value,'sections')) throw new Error('PATTERN_MAP_VALIDATION: sections must be an array');
  if(!hasArray(value,'alignments')) throw new Error('PATTERN_MAP_VALIDATION: alignments must be an array');
  if(!isObject(value.layers)) throw new Error('PATTERN_MAP_VALIDATION: layers must be an object');
}

export function parsePatternMapJson(json:string):PatternMap {
  let raw:unknown;
  try {
    raw=JSON.parse(json);
  } catch(error) {
    const message=error instanceof Error?error.message:String(error);
    throw new Error(`PATTERN_MAP_JSON: ${message}`);
  }

  if(!isObject(raw)||raw.schema!=='polly.pattern-map.v1') {
    throw new Error('PATTERN_MAP_SCHEMA: expected polly.pattern-map.v1');
  }

  preflight(raw);
  try {
    assertValidPatternMap(raw);
  } catch(error) {
    const message=error instanceof Error?error.message:String(error);
    throw new Error(`PATTERN_MAP_VALIDATION: ${message}`);
  }
  return raw;
}
