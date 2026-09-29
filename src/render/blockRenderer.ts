import type { Actor } from '../sim/types.js';
import type { WorldState } from '../sim/world.js';

export interface BlockDescriptor { id:string; label:string; color:number; x:number; y:number; width:number; height:number; depth:number; hp:number; maxHp:number; state:string; }
export interface StrikeDescriptor { actorId:string; attackId:string; color:number; x:number; y:number; width:number; height:number; depth:number; }

const COLORS:Record<string,number>={POLLY:0xd14b4b,GLAM:0xff4fd8,PROG:0x6dbb68,PUNK:0xe23b2f};
const actorWidth=(actor:Actor):number => actor.kind==='POLLY'?34:32;
const actorHeight=(actor:Actor):number => actor.kind==='POLLY'?86:80;

export function blockDescriptors(world:WorldState):BlockDescriptor[]{
  return [world.polly,...world.enemies].map(actor=>({
    id:actor.id,
    label:actor.kind,
    color:COLORS[actor.kind],
    x:actor.position.x,
    y:actor.position.y,
    width:actorWidth(actor),
    height:actorHeight(actor),
    depth:actor.position.y,
    hp:actor.hp,
    maxHp:actor.maxHp,
    state:actor.state,
  }));
}

export function strikeDescriptors(world:WorldState):StrikeDescriptor[]{
  return [world.polly,...world.enemies].flatMap(actor=>{
    const attack=actor.attack;
    if(!attack || attack.phase!=='ACTIVE') return [];
    const bodyHalf=actorWidth(actor)/2;
    const width=Math.max(12,attack.definition.rangeX);
    const height=attack.definition.id==='HEAVY'?18:10;
    const x=actor.position.x + actor.facing*(bodyHalf + width/2);
    const y=actor.position.y - actorHeight(actor)*0.58;
    return [{
      actorId:actor.id,
      attackId:attack.definition.id,
      color:actor.kind==='POLLY'?0xffe276:0xff9b66,
      x,
      y,
      width,
      height,
      depth:actor.position.y+0.1,
    }];
  });
}

export function cameraOffsetX(pollyX:number,viewportWidth=960,worldWidth=2600):number {
  const deadLeft=viewportWidth*.38, deadRight=viewportWidth*.62;
  let target=0;
  if(pollyX>deadRight) target=pollyX-deadRight;
  else if(pollyX<deadLeft) target=pollyX-deadLeft;
  return Math.max(0,Math.min(worldWidth-viewportWidth,target));
}
