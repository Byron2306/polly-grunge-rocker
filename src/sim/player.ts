import type { Actor, AttackDefinition, PlayerIntent } from './types.js';
import { COMBO_RESET_MS, HEAVY_LANE_TOLERANCE, SPRINT_RATIO, STANDARD_LANE_TOLERANCE, VERTICAL_SPEED_RATIO, WALK_SPEED } from './constants.js';

const LIGHTS: AttackDefinition[] = [
  {id:'L1',startupMs:90,activeMs:80,recoveryMs:150,damage:1,stagger:1,rangeX:48,laneTolerance:STANDARD_LANE_TOLERANCE,knockback:25,hitstopMs:45},
  {id:'L2',startupMs:110,activeMs:90,recoveryMs:170,damage:1.1,stagger:1,rangeX:52,laneTolerance:STANDARD_LANE_TOLERANCE,knockback:35,hitstopMs:50},
  {id:'L3',startupMs:150,activeMs:110,recoveryMs:260,damage:1.5,stagger:2,rangeX:58,laneTolerance:STANDARD_LANE_TOLERANCE,knockback:70,hitstopMs:65},
];
export const HEAVY_ATTACK: AttackDefinition = {id:'HEAVY',startupMs:300,activeMs:140,recoveryMs:420,damage:2.8,stagger:4,rangeX:86,laneTolerance:HEAVY_LANE_TOLERANCE,knockback:130,hitstopMs:105};

export function createPolly(): Actor {
  return { id:'polly', kind:'POLLY', state:'IDLE', position:{x:120,y:320}, velocity:{x:0,y:0}, facing:1, hp:12,maxHp:12, stagger:0,staggerResistance:4,
    body:{x:-14,y:-10,width:28,height:20},hurtbox:{x:-16,y:-86,width:32,height:86},attack:null,hitstopMs:0,hitstunMs:0,invulnerableMs:0,heldPickupId:null,
    comboIndex:0,comboResetMs:0,queuedLight:false,archetypeTimerMs:0,tokenOwned:false };
}
function approach(current:number,target:number,maxDelta:number):number { return current < target ? Math.min(target,current+maxDelta) : Math.max(target,current-maxDelta); }
function startLight(actor:Actor,index:1|2|3):void {
  actor.comboIndex=index; actor.comboResetMs=COMBO_RESET_MS; actor.queuedLight=false; actor.state='ATTACK';
  actor.attack={definition:LIGHTS[index-1],phase:'STARTUP',elapsedMs:0,hitVictimIds:new Set()};
}
export function startHeavy(actor: Actor): void {
  actor.state='ATTACK'; actor.attack={definition:HEAVY_ATTACK,phase:'STARTUP',elapsedMs:0,hitVictimIds:new Set()}; actor.queuedLight=false;
}
function advanceAttack(actor:Actor,dtMs:number):void {
  const a=actor.attack; if(!a) return;
  a.elapsedMs += dtMs;
  const start=a.definition.startupMs, activeEnd=start+a.definition.activeMs, total=activeEnd+a.definition.recoveryMs;
  if(a.elapsedMs < start) a.phase='STARTUP';
  else if(a.elapsedMs < activeEnd) a.phase='ACTIVE';
  else if(a.elapsedMs < total) a.phase='RECOVERY';
  else {
    const canChain=a.definition.id.startsWith('L') && actor.queuedLight && actor.comboIndex < 3;
    actor.attack=null; actor.state='IDLE';
    if(canChain) startLight(actor,(actor.comboIndex+1) as 1|2|3);
    else actor.comboResetMs=COMBO_RESET_MS;
  }
}
export function updatePolly(actor:Actor,intent:PlayerIntent,dtMs:number):void {
  if(actor.hitstopMs>0){ actor.hitstopMs=Math.max(0,actor.hitstopMs-dtMs); return; }
  if(actor.invulnerableMs>0) actor.invulnerableMs=Math.max(0,actor.invulnerableMs-dtMs);
  if(actor.hitstunMs>0){ actor.hitstunMs=Math.max(0,actor.hitstunMs-dtMs); return; }
  if(actor.attack){
    if(intent.lightPressed && actor.attack.definition.id.startsWith('L') && actor.comboIndex<3) actor.queuedLight=true;
    advanceAttack(actor,dtMs);
    return;
  }
  if(actor.comboIndex>0){ actor.comboResetMs=Math.max(0,actor.comboResetMs-dtMs); if(actor.comboResetMs===0) actor.comboIndex=0; }
  if(intent.lightPressed){ startLight(actor,1); return; }
  if(intent.heavyPressed){ startHeavy(actor); return; }
  const sprint=intent.sprint?SPRINT_RATIO:1;
  const targetX=intent.moveX*WALK_SPEED*sprint;
  const targetY=intent.moveY*WALK_SPEED*VERTICAL_SPEED_RATIO*sprint;
  const accel=1200*(dtMs/1000), decel=1500*(dtMs/1000);
  actor.velocity.x=approach(actor.velocity.x,targetX,intent.moveX?accel:decel);
  actor.velocity.y=approach(actor.velocity.y,targetY,intent.moveY?accel:decel);
  actor.position.x += actor.velocity.x*(dtMs/1000); actor.position.y += actor.velocity.y*(dtMs/1000);
  if(intent.moveX>0) actor.facing=1; else if(intent.moveX<0) actor.facing=-1;
}
