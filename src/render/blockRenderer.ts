import type { Actor } from '../sim/types.js';
import type { WorldState } from '../sim/world.js';

export interface BlockDescriptor { id:string; label:string; color:number; x:number; y:number; width:number; height:number; depth:number; hp:number; maxHp:number; state:string; }
export type StrikePhase = 'TELEGRAPH'|'ACTIVE';
export type StrikeShape = 'STRIKE'|'GUITAR'|'WAVE'|'RAM';
export interface StrikeDescriptor { actorId:string; attackId:string; shape:StrikeShape; phase:StrikePhase; color:number; x:number; y:number; width:number; height:number; depth:number; }

const COLORS:Record<string,number>={POLLY:0xd14b4b,GLAM:0xff4fd8,PROG:0x6dbb68,PUNK:0xe23b2f};
const actorWidth=(actor:Actor):number => actor.kind==='POLLY'?34:32;
const actorHeight=(actor:Actor):number => actor.kind==='POLLY'?86:80;

export function blockDescriptors(world:WorldState):BlockDescriptor[]{
  return [world.polly,...world.enemies].map(actor=>({
    id:actor.id,label:actor.kind,color:COLORS[actor.kind],x:actor.position.x,y:actor.position.y,
    width:actorWidth(actor),height:actorHeight(actor),depth:actor.position.y,hp:actor.hp,maxHp:actor.maxHp,state:actor.state,
  }));
}

function frontX(actor:Actor,width:number,extra=0):number {
  return actor.position.x + actor.facing*(actorWidth(actor)/2 + extra + width/2);
}
function simple(actor:Actor,width:number,height:number,color:number,shape:StrikeShape,phase:StrikePhase,attackId:string,vertical=0):StrikeDescriptor {
  return {actorId:actor.id,attackId,shape,phase,color,x:frontX(actor,width),y:actor.position.y-actorHeight(actor)*0.58+vertical,width,height,depth:actor.position.y+0.1};
}
function guitar(actor:Actor,phase:StrikePhase):StrikeDescriptor[]{
  const solid=phase==='ACTIVE';
  const color=solid?0xffe276:0xffd86a;
  const dir=actor.facing;
  return [
    {...simple(actor,46,12,color,'GUITAR',phase,'HEAVY',-16),x:actor.position.x+dir*38},
    {...simple(actor,60,15,color,'GUITAR',phase,'HEAVY',-2),x:actor.position.x+dir*58},
    {...simple(actor,72,18,color,'GUITAR',phase,'HEAVY',14),x:actor.position.x+dir*78},
  ];
}
function enemyGeometry(actor:Actor):StrikeDescriptor[]{
  const phase:StrikePhase=actor.state==='ATTACK'?'ACTIVE':'TELEGRAPH';
  if(actor.state!=='ATTACK'&&actor.state!=='THREATEN') return [];
  if(actor.kind==='GLAM') return [simple(actor,actor.state==='ATTACK'?64:50,10,0xff70df,'STRIKE',phase,'GLAM_BACKHAND')];
  if(actor.kind==='PUNK') return [simple(actor,actor.state==='ATTACK'?126:112,28,0xff633d,'RAM',phase,'PUNK_CHARGE')];
  if(actor.kind==='PROG') {
    const color=0x8dff83;
    const widths=actor.state==='ATTACK'?[30,26,22]:[24,20,16];
    return widths.map((w,i)=>({
      ...simple(actor,w,8,color,'WAVE',phase,'PROG_PULSE',(i-1)*12),
      x:actor.position.x+actor.facing*(34+i*26),
    }));
  }
  return [];
}

export function strikeDescriptors(world:WorldState):StrikeDescriptor[]{
  const out:StrikeDescriptor[]=[];
  const polly=world.polly;
  const attack=polly.attack;
  if(attack){
    if(attack.definition.id==='HEAVY' && (attack.phase==='STARTUP'||attack.phase==='ACTIVE')) out.push(...guitar(polly,attack.phase==='ACTIVE'?'ACTIVE':'TELEGRAPH'));
    else if(attack.phase==='ACTIVE') out.push(simple(polly,Math.max(12,attack.definition.rangeX),10,0xffe276,'STRIKE','ACTIVE',attack.definition.id));
  }
  for(const enemy of world.enemies) out.push(...enemyGeometry(enemy));
  return out;
}

export function cameraOffsetX(pollyX:number,viewportWidth=960,worldWidth=2600):number {
  const deadLeft=viewportWidth*.38, deadRight=viewportWidth*.62;
  let target=0;
  if(pollyX>deadRight) target=pollyX-deadRight;
  else if(pollyX<deadLeft) target=pollyX-deadLeft;
  return Math.max(0,Math.min(worldWidth-viewportWidth,target));
}
