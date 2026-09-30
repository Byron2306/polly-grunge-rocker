import type { Actor } from '../sim/types.js';
export type CombatFxKind='LIGHT_BURST'|'HEAVY_BURST'|'GUITAR_ARC'|'PROG_WAVE'|'PUNK_RUSH'|'KO_BURST'|'HURT_FLASH'|'DUST';
export interface CombatFxDescriptor { actorId:string; kind:CombatFxKind; x:number; y:number; width:number; height:number; color:number; alpha:number; facing:-1|1; }
export function combatFxForActor(actor:Actor):CombatFxDescriptor[]{
  const out:CombatFxDescriptor[]=[]; const base={actorId:actor.id,x:actor.position.x,y:actor.position.y-54,facing:actor.facing};
  if(actor.kind==='POLLY'&&actor.attack){
    if(actor.attack.definition.id==='HEAVY'&&(actor.attack.phase==='STARTUP'||actor.attack.phase==='ACTIVE')) out.push({...base,kind:'GUITAR_ARC',width:actor.attack.phase==='ACTIVE'?108:86,height:72,color:0xf5e6c8,alpha:actor.attack.phase==='ACTIVE'?.92:.42});
    else if(actor.attack.phase==='ACTIVE') out.push({...base,kind:'LIGHT_BURST',width:28,height:18,color:0xfff1cf,alpha:.9});
  }
  if(actor.kind==='PROG'&&(actor.state==='THREATEN'||actor.state==='ATTACK')) out.push({...base,kind:'PROG_WAVE',width:actor.state==='ATTACK'?100:70,height:22,color:0x8cdf78,alpha:actor.state==='ATTACK'?.9:.5});
  if(actor.kind==='PUNK'&&actor.state==='ATTACK') out.push({...base,kind:'PUNK_RUSH',width:120,height:42,color:0xe85b34,alpha:.78});
  if(actor.state==='HURT'||actor.state==='KNOCKBACK') out.push({...base,kind:'HURT_FLASH',width:46,height:50,color:0xfff1cf,alpha:.8});
  if(actor.state==='KO') out.push({...base,kind:'KO_BURST',width:90,height:84,color:0x9f1d2d,alpha:.88});
  if(actor.kind==='PUNK'&&Math.abs(actor.velocity.x)>180) out.push({...base,kind:'DUST',x:actor.position.x-actor.facing*18,y:actor.position.y-6,width:34,height:12,color:0xb8a78b,alpha:.5});
  return out;
}
