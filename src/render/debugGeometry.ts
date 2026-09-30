import type { Actor } from '../sim/types.js';

export type DebugGeometryMode='AESTHETIC'|'GEOMETRY';
export type DebugGeometryKind='BODY'|'HURT'|'ATTACK';
export interface DebugGeometryDescriptor { actorId:string; kind:DebugGeometryKind; x:number; y:number; width:number; height:number; anchorX:number; anchorY:number; }
export interface DebugWorldView { polly:Actor; enemies:Actor[]; }
export function toggleDebugGeometry(mode:DebugGeometryMode):DebugGeometryMode { return mode==='AESTHETIC'?'GEOMETRY':'AESTHETIC'; }
export function debugGeometryDescriptors(world:DebugWorldView):DebugGeometryDescriptor[]{
  const out:DebugGeometryDescriptor[]=[];
  for(const actor of [world.polly,...world.enemies]){
    out.push({actorId:actor.id,kind:'BODY',x:actor.position.x+actor.body.x,y:actor.position.y+actor.body.y,width:actor.body.width,height:actor.body.height,anchorX:actor.position.x,anchorY:actor.position.y});
    out.push({actorId:actor.id,kind:'HURT',x:actor.position.x+actor.hurtbox.x,y:actor.position.y+actor.hurtbox.y,width:actor.hurtbox.width,height:actor.hurtbox.height,anchorX:actor.position.x,anchorY:actor.position.y});
    const attack=actor.attack;
    if(attack && attack.phase==='ACTIVE'){
      const width=attack.definition.rangeX;
      const left=actor.facing>0 ? actor.position.x + actor.hurtbox.width/2 : actor.position.x - actor.hurtbox.width/2 - width;
      out.push({actorId:actor.id,kind:'ATTACK',x:left,y:actor.position.y-62,width,height:24,anchorX:actor.position.x,anchorY:actor.position.y});
    }
  }
  return out;
}
