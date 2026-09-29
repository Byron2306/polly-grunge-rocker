export type TokenReason = 'NORMAL'|'GLAM_BACKHAND'|'PROG_POKE'|'PUNK_CHARGE';
export class AttackTokenPool {
  private ordinary = new Set<string>();
  private bypass = new Set<string>();
  constructor(public readonly maxOrdinary = 2) {}
  acquire(actorId:string, reason:TokenReason):boolean {
    if(this.has(actorId)) return true;
    if(reason==='PUNK_CHARGE'){ this.bypass.add(actorId); return true; }
    if(this.ordinary.size>=this.maxOrdinary) return false;
    this.ordinary.add(actorId); return true;
  }
  release(actorId:string):void { this.ordinary.delete(actorId); this.bypass.delete(actorId); }
  clear():void { this.ordinary.clear(); this.bypass.clear(); }
  has(actorId:string):boolean { return this.ordinary.has(actorId)||this.bypass.has(actorId); }
  get ordinaryCount():number { return this.ordinary.size; }
  get totalCount():number { return this.ordinary.size+this.bypass.size; }
}
