import type { WorldState } from './world.js';
import { createEnemy } from './enemies.js';

export type EncounterStage = 'OPENING'|'E1'|'E2'|'E3'|'COMPLETE';
export interface EncounterState { stage:EncounterStage; stageMs:number; spawnedE1:boolean; spawnedE2Prog:boolean; spawnedE2Glam:boolean; spawnedE3:boolean; completionEmitted:boolean; }
export type EncounterEvent = {type:'SPAWN'; kind:'GLAM'|'PROG'|'PUNK'} | {type:'SLICE_COMPLETE'};
export function createRatHoleEncounter():EncounterState { return {stage:'OPENING',stageMs:0,spawnedE1:false,spawnedE2Prog:false,spawnedE2Glam:false,spawnedE3:false,completionEmitted:false}; }
function living(world:WorldState){ return world.enemies.filter(e=>e.state!=='KO'); }
function clearEnemies(world:WorldState){ for(const e of world.enemies) world.tokens.release(e.id); world.enemies=[]; }
function spawn(world:WorldState,kind:'GLAM'|'PROG'|'PUNK',x:number,y:number,events:EncounterEvent[]){ const e=createEnemy(kind);e.position={x,y};world.enemies.push(e);events.push({type:'SPAWN',kind}); }
export function updateEncounter(world:WorldState, encounter:EncounterState, dtMs:number):EncounterEvent[] {
  const events:EncounterEvent[]=[]; encounter.stageMs+=dtMs;
  if(encounter.stage==='OPENING' && encounter.stageMs>=1000){ encounter.stage='E1';encounter.stageMs=0; }
  if(encounter.stage==='E1'){
    if(!encounter.spawnedE1){spawn(world,'GLAM',620,320,events);encounter.spawnedE1=true;}
    else if(living(world).length===0){clearEnemies(world);encounter.stage='E2';encounter.stageMs=0;}
  }
  if(encounter.stage==='E2'){
    if(!encounter.spawnedE2Prog){spawn(world,'PROG',680,300,events);encounter.spawnedE2Prog=true;encounter.stageMs=0;}
    const prog=world.enemies.find(e=>e.kind==='PROG'&&e.state!=='KO');
    if(!encounter.spawnedE2Glam && encounter.spawnedE2Prog && (encounter.stageMs>=1200 || (!!prog && prog.hp<=3))){spawn(world,'GLAM',760,350,events);encounter.spawnedE2Glam=true;}
    if(encounter.spawnedE2Glam && living(world).length===0){clearEnemies(world);encounter.stage='E3';encounter.stageMs=0;}
  }
  if(encounter.stage==='E3'){
    if(!encounter.spawnedE3){spawn(world,'PUNK',720,320,events);spawn(world,'GLAM',790,280,events);spawn(world,'PROG',850,360,events);encounter.spawnedE3=true;}
    else if(living(world).length===0){clearEnemies(world);encounter.stage='COMPLETE';world.sliceComplete=true;if(!encounter.completionEmitted){events.push({type:'SLICE_COMPLETE'});encounter.completionEmitted=true;}}
  }
  return events;
}
