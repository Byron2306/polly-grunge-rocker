import type { PickupKind } from './types.js';
export interface PickupState { id:string; kind:PickupKind; x:number; y:number; durability:number; rangeX:number; heldBy:string|null; broken:boolean; }
let nextPickupId=1;
export function createPickup(kind:PickupKind,x:number,y:number):PickupState {
  return {id:`pickup-${nextPickupId++}`,kind,x,y,durability:kind==='BOTTLE'?3:6,rangeX:kind==='BOTTLE'?55:92,heldBy:null,broken:false};
}
export function usePickup(pickup:PickupState):void {
  if(pickup.broken) return;
  pickup.durability=Math.max(0,pickup.durability-1);
  if(pickup.durability===0){pickup.broken=true;pickup.heldBy=null;}
}
