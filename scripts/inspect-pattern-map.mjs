import { readFile } from 'node:fs/promises';
import { parsePatternMapJson } from '../dist/music/patternMap/load.js';
import { formatPatternMapInspection } from '../dist/music/patternMap/inspect.js';

const file=process.argv[2];
const timeArg=process.argv[3]??'0';
if(!file){
  console.error('usage: node scripts/inspect-pattern-map.mjs <file> [timeMs]');
  process.exitCode=2;
} else {
  try {
    const timeMs=Number(timeArg);
    if(!Number.isFinite(timeMs)) throw new Error(`invalid timeMs: ${timeArg}`);
    const json=await readFile(file,'utf8');
    const map=parsePatternMapJson(json);
    console.log(formatPatternMapInspection(map,timeMs));
  } catch(error) {
    console.error(error instanceof Error?error.message:String(error));
    process.exitCode=1;
  }
}
