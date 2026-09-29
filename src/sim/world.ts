import type { Actor, PlayerIntent } from './types.js';
import { createPolly, updatePolly } from './player.js';
import { updateEnemy } from './enemies.js';
import { AttackTokenPool } from './tokens.js';
import type { PickupState } from './pickups.js';
import { usePickup } from './pickups.js';
import { resolveAttackHit } from './combat.js';

export interface WorldState { polly:Actor; enemies:Actor[]; pickups:PickupState[]; tokens:AttackTokenPool; elapsedMs:number; sliceComplete:boolean; }
export function createWorld():WorldState { return {polly:createPolly(),enemies:[],pickups:[],tokens:new AttackTokenPool(2),elapsedMs:0,sliceComplete:false}; }

export function separateBodies(actors:Actor[]):void {
  for(let i=0;i<actors.length;i++) for(let j=i+1;j<actors.length;j++) {
    const a=actors[i],b=actors[j]; if(a.state==='KO'||b.state==='KO') continue;
    const dx=b.position.x-a.position.x, dy=b.position.y-a.position.y;
    const minX=26,minY=14;
    if(Math.abs(dx)<minX && Math.abs(dy)<minY){
      const push=(minX-Math.abs(dx))/2;
      const sign=dx===0?(a.id<b.id?1:-1):Math.sign(dx);
      a.position.x-=sign*push; b.position.x+=sign*push;
    }
  }
}
function handleInteraction(world:WorldState):void {
  const p=world.polly;
  if(p.heldPickupId){
    const held=world.pickups.find(x=>x.id===p.heldPickupId);
    if(held){held.heldBy=null;held.x=p.position.x+20*p.facing;held.y=p.position.y;}
    p.heldPickupId=null; return;
  }
  let best:PickupState|undefined, bestDist=Infinity;
  for(const item of world.pickups){ if(item.broken||item.heldBy) continue; const d=Math.hypot(item.x-p.position.x,item.y-p.position.y); if(d<=48&&d<bestDist){best=item;bestDist=d;} }
  if(best){best.heldBy=p.id;p.heldPickupId=best.id;}
}
function resolvePlayerCombat(world:WorldState):void {
  const runtime=world.polly.attack;
  if(!runtime || runtime.phase!=='ACTIVE') return;
  const held=world.pickups.find(p=>p.id===world.polly.heldPickupId && !p.broken);
  const attack = held && runtime.definition.id.startsWith('L')
    ? { ...runtime.definition, rangeX: held.rangeX, damage: runtime.definition.damage + (held.kind==='BOTTLE'?0.4:0.25) }
    : runtime.definition;
  let pickupConsumed=false;
  for(const enemy of world.enemies){
    const result=resolveAttackHit(world.polly,enemy,attack);
    if(result.hit && held && !pickupConsumed){ usePickup(held); pickupConsumed=true; if(held.broken) world.polly.heldPickupId=null; }
  }
}
function resolveEnemyCombat(world:WorldState,dtMs:number):void {
  for(const enemy of world.enemies){
    if(enemy.state==='ATTACK' && enemy.archetypeTimerMs<=dtMs+1 && Math.abs(enemy.position.x-world.polly.position.x)<70 && Math.abs(enemy.position.y-world.polly.position.y)<28 && world.polly.state!=='KO'){
      world.polly.hp=Math.max(0,world.polly.hp-0.7); world.polly.state=world.polly.hp<=0?'KO':'HURT'; world.polly.hitstunMs=180;
    }
  }
}
export function stepWorld(world:WorldState,intent:PlayerIntent,dtMs:number):void {
  world.elapsedMs+=dtMs;
  if(intent.interactPressed) handleInteraction(world);
  updatePolly(world.polly,intent,dtMs);
  resolvePlayerCombat(world);
  for(const enemy of world.enemies) updateEnemy(enemy,{polly:world.polly,tokens:world.tokens,seed01:.5},dtMs);
  resolveEnemyCombat(world,dtMs);
  separateBodies([world.polly,...world.enemies]);
  const held=world.pickups.find(p=>p.id===world.polly.heldPickupId); if(held){held.x=world.polly.position.x;held.y=world.polly.position.y;}
}
