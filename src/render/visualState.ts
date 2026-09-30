import type { Actor, Facing } from '../sim/types.js';

export type VisualStateKey = string;
export interface VisualStateDescriptor { key:VisualStateKey; facing:Facing; loop:boolean; }

const enemyPrefix=(kind:Actor['kind']):string => kind.toLowerCase();
export function visualStateForActor(actor:Actor):VisualStateDescriptor {
  const facing=actor.facing;
  if(actor.kind==='POLLY'){
    if(actor.state==='KO') return {key:'polly.ko',facing,loop:false};
    if(actor.state==='HURT'||actor.state==='KNOCKBACK'||actor.state==='DOWN') return {key:'polly.hurt',facing,loop:false};
    if(actor.state==='GETUP') return {key:'polly.getup',facing,loop:false};
    if(actor.state==='ATTACK'&&actor.attack){
      const id=actor.attack.definition.id;
      if(id==='HEAVY') return {key:`polly.heavy.${actor.attack.phase.toLowerCase()}`,facing,loop:false};
      if(/^L[123]$/.test(id)) return {key:`polly.light${id[1]}`,facing,loop:false};
    }
    const speed=Math.hypot(actor.velocity.x,actor.velocity.y);
    if(speed>=180) return {key:'polly.sprint',facing,loop:true};
    if(speed>1) return {key:'polly.walk',facing,loop:true};
    return {key:'polly.idle',facing,loop:true};
  }
  const prefix=enemyPrefix(actor.kind);
  if(actor.state==='THREATEN') return {key:`${prefix}.threaten`,facing,loop:true};
  if(actor.state==='ATTACK') return {key:`${prefix}.attack`,facing,loop:false};
  if(actor.state==='HURT'||actor.state==='KNOCKBACK') return {key:`${prefix}.hurt`,facing,loop:false};
  if(actor.state==='DOWN'||actor.state==='KO') return {key:`${prefix}.ko`,facing,loop:false};
  if(actor.state==='APPROACH'||actor.state==='ALIGN') return {key:`${prefix}.walk`,facing,loop:true};
  return {key:`${prefix}.idle`,facing,loop:true};
}
