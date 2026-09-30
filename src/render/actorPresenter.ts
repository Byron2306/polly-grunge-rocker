import type { Actor } from '../sim/types.js';
import { visualStateForActor } from './visualState.js';
import { framesForVisualState } from './spriteManifest.js';

export interface ActorPresentation { id:string; x:number; y:number; depth:number; flipX:boolean; fallback:boolean; assetKey:string|null; visualKey:string; }
export function presentationForActor(actor:Actor,cameraOffsetX:number,assetAvailable:boolean):ActorPresentation {
  const visual=visualStateForActor(actor);
  const frame=framesForVisualState(visual.key).frames[0];
  const hasFrame=!!frame?.path;
  const useSprite=hasFrame && assetAvailable;
  return {id:actor.id,x:actor.position.x-cameraOffsetX,y:actor.position.y,depth:actor.position.y,flipX:actor.facing<0,fallback:!useSprite,assetKey:useSprite?frame.assetKey:null,visualKey:visual.key};
}

export class ActorPresenter {
  private sprites=new Map<string,any>();
  private debugGeometry=false;
  constructor(private readonly scene:any){}
  syncActor(actor:Actor,cameraOffsetX:number):ActorPresentation {
    const visual=visualStateForActor(actor);
    const anim=framesForVisualState(visual.key);
    const desired=anim.frames.length?anim.frames[Math.floor(Date.now()/Math.max(1,anim.frameMs))%anim.frames.length]:undefined;
    const available=!!desired?.path && !!this.scene?.textures?.exists?.(desired.assetKey);
    const presentation=presentationForActor(actor,cameraOffsetX,available);
    if(!desired || !available){ const old=this.sprites.get(actor.id); old?.setVisible?.(false); return presentation; }
    let sprite=this.sprites.get(actor.id);
    if(!sprite){ sprite=this.scene.add.sprite(presentation.x,presentation.y,desired.assetKey); sprite.setOrigin?.(.5,1); this.sprites.set(actor.id,sprite); }
    sprite.setVisible?.(true); sprite.setPosition?.(presentation.x,presentation.y); sprite.setDepth?.(presentation.depth); sprite.setFlipX?.(presentation.flipX);
    if(sprite.texture?.key!==desired.assetKey) sprite.setTexture?.(desired.assetKey);
    sprite.setFrame?.(desired.frameIndex);
    return presentation;
  }
  removeMissing(actorIds:Iterable<string>):void { const keep=new Set(actorIds); for(const [id,s] of this.sprites){ if(!keep.has(id)){s.destroy?.();this.sprites.delete(id);} } }
  setDebugGeometry(enabled:boolean):void { this.debugGeometry=enabled; }
  isDebugGeometryEnabled():boolean { return this.debugGeometry; }
  destroy():void { for(const s of this.sprites.values()) s.destroy?.(); this.sprites.clear(); }
}
