import { readFileSync, writeFileSync } from 'node:fs';
import { parsePcmWav } from '../dist/music/authoring/wav.js';
import { detectOnsetCandidates } from '../dist/music/authoring/onsets.js';
import { inferTempoCandidates } from '../dist/music/authoring/tempo.js';
import { formatAuthoringReport } from '../dist/music/authoring/inspect.js';
import { exportPatternMap } from '../dist/music/authoring/export.js';
import { parsePatternMapJson } from '../dist/music/patternMap/load.js';

const roles=new Set(['DRUMS','BASS','RHYTHM_GUITAR','LEAD_KEYS','VOCALS']);
const [mode,...args]=process.argv.slice(2);

function fail(message){ console.error(message); process.exitCode=1; }

try{
  if(mode==='analyze-wav'){
    const [role,wavFile,outFile]=args;
    if(!roles.has(role)||!wavFile||!outFile) throw new Error('usage: analyze-wav <role> <wav-file> <session-json-out>');
    const raw=readFileSync(wavFile);
    const bytes=new Uint8Array(raw.buffer,raw.byteOffset,raw.byteLength);
    const wav=parsePcmWav(bytes);
    const sourceId=`wav:${role}`;
    const onsets=detectOnsetCandidates(wav,sourceId,role);
    const tempos=inferTempoCandidates(onsets,sourceId);
    const session={
      schema:'polly.authoring-session.v1',
      sessionId:`authoring:${role}`,
      trackId:'UNSET',
      durationMs:wav.durationMs,
      inputs:[{id:sourceId,kind:'WAV',role,path:wavFile,durationMs:wav.durationMs}],
      candidates:[...tempos,...onsets],
      corrections:[],
    };
    writeFileSync(outFile,JSON.stringify(session,null,2)+'\n','utf8');
    console.log(formatAuthoringReport(session));
  } else if(mode==='inspect'){
    const [sessionFile]=args;
    if(!sessionFile) throw new Error('usage: inspect <session-json>');
    const session=JSON.parse(readFileSync(sessionFile,'utf8'));
    console.log(formatAuthoringReport(session));
  } else if(mode==='export'){
    const [sessionFile,skeletonFile,outFile]=args;
    if(!sessionFile||!skeletonFile||!outFile) throw new Error('usage: export <session-json> <skeleton-pattern-map-json> <pattern-map-out>');
    const session=JSON.parse(readFileSync(sessionFile,'utf8'));
    const skeleton=parsePatternMapJson(readFileSync(skeletonFile,'utf8'));
    const map=exportPatternMap(session,skeleton);
    writeFileSync(outFile,JSON.stringify(map,null,2)+'\n','utf8');
    console.log(`exported ${outFile}`);
  } else {
    throw new Error('usage: analyze-pattern-map.mjs <analyze-wav|inspect|export> ...');
  }
}catch(error){
  fail(error instanceof Error?error.message:String(error));
}
