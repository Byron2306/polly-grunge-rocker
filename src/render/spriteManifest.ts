import type { VisualStateKey } from './visualState.js';

export interface SpriteFrameRef { assetKey:string; path:string; }
export interface SpriteAnimationDef { key:VisualStateKey; frames:[SpriteFrameRef,SpriteFrameRef]; frameMs:number; loop:boolean; family:string; }
const frame=(family:string,state:string,index:1|2):SpriteFrameRef=>({assetKey:`${family}.${state}.${index}`,path:`assets/${family.replaceAll('.','/')}/${state}-${index}.png`});
const def=(key:string,family:string,state:string,loop:boolean,frameMs=180):SpriteAnimationDef=>({key,frames:[frame(family,state,1),frame(family,state,2)],frameMs,loop,family});
export const FALLBACK_SPRITE:SpriteAnimationDef={key:'fallback',frames:[{assetKey:'fallback.1',path:''},{assetKey:'fallback.2',path:''}],frameMs:250,loop:true,family:'fallback'};
export const PHASE2_SPRITE_MANIFEST:Record<string,SpriteAnimationDef>={
  'polly.idle':def('polly.idle','characters.polly','idle',true,260),
  'polly.walk':def('polly.walk','characters.polly','walk',true,150),
  'polly.sprint':def('polly.sprint','characters.polly','sprint',true,110),
  'polly.light1':def('polly.light1','characters.polly','light1',false,90),
  'polly.light2':def('polly.light2','characters.polly','light2',false,100),
  'polly.light3':def('polly.light3','characters.polly','light3',false,120),
  'polly.heavy.startup':def('polly.heavy.startup','characters.polly','heavy-startup',false,150),
  'polly.heavy.active':def('polly.heavy.active','characters.polly','heavy-active',false,90),
  'polly.heavy.recovery':def('polly.heavy.recovery','characters.polly','heavy-recovery',false,180),
  'polly.hurt':def('polly.hurt','characters.polly','hurt',false,120),
  'polly.getup':def('polly.getup','characters.polly','getup',false,180),
  'polly.ko':def('polly.ko','characters.polly','ko',false,240),
};
for(const family of ['glam','prog','punk'] as const){
  for(const [state,loop,ms] of [['idle',true,260],['walk',true,160],['threaten',true,140],['attack',false,100],['hurt',false,120],['ko',false,240]] as const){
    const key=`${family}.${state}`; PHASE2_SPRITE_MANIFEST[key]=def(key,`enemies.${family}`,state,loop,ms);
  }
}
export function framesForVisualState(key:VisualStateKey):SpriteAnimationDef { return PHASE2_SPRITE_MANIFEST[key] ?? FALLBACK_SPRITE; }
