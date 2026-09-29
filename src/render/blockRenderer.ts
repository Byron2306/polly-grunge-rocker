import type { WorldState } from '../sim/world.js';
export interface BlockDescriptor { id:string; label:string; color:number; x:number; y:number; width:number; height:number; depth:number; hp:number; maxHp:number; state:string; }
const COLORS:Record<string,number>={POLLY:0xd14b4b,GLAM:0xff4fd8,PROG:0x6dbb68,PUNK:0xe23b2f};
export function blockDescriptors(world:WorldState):BlockDescriptor[]{
  return [world.polly,...world.enemies].map(a=>({id:a.id,label:a.kind,color:COLORS[a.kind],x:a.position.x,y:a.position.y,width:a.kind==='POLLY'?34:32,height:a.kind==='POLLY'?86:80,depth:a.position.y,hp:a.hp,maxHp:a.maxHp,state:a.state}));
}
export function cameraOffsetX(pollyX:number,viewportWidth=960,worldWidth=2600):number {
  const deadLeft=viewportWidth*.38, deadRight=viewportWidth*.62;
  let target=0;
  if(pollyX>deadRight) target=pollyX-deadRight;
  else if(pollyX<deadLeft) target=pollyX-deadLeft;
  return Math.max(0,Math.min(worldWidth-viewportWidth,target));
}
