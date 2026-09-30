import type { VisualStateKey } from './visualState.js';

export interface SpriteFrameRef { assetKey:string; path:string; frameIndex:number; }
export interface SpriteAnimationDef { key:VisualStateKey; frames:[SpriteFrameRef,SpriteFrameRef]; frameMs:number; loop:boolean; family:string; }
export interface SpriteSheetDef { assetKey:string; path:string; frameWidth:number; frameHeight:number; }
export const POLLY_HEAVY_FX_KEY='fx.guitar-arc';
export const FALLBACK_SPRITE:SpriteAnimationDef={key:'fallback',frames:[{assetKey:'fallback',path:'',frameIndex:0},{assetKey:'fallback',path:'',frameIndex:0}],frameMs:250,loop:true,family:'fallback'};

const manifest:Record<string,SpriteAnimationDef>={};
function registerFamily(prefix:string,family:string,path:string,states:readonly [string,boolean,number][]):void {
  states.forEach(([state,loop,frameMs],i)=>{
    const key=`${prefix}.${state}`;
    const assetKey=`${family}.sheet`;
    manifest[key]={key,frames:[{assetKey,path,frameIndex:i*2},{assetKey,path,frameIndex:i*2+1}],frameMs,loop,family};
  });
}
registerFamily('polly','characters.polly','assets/characters/polly/polly-phase2.png',[
  ['idle',true,260],['walk',true,150],['sprint',true,110],['light1',false,90],['light2',false,100],['light3',false,120],
  ['heavy.startup',false,150],['heavy.active',false,90],['heavy.recovery',false,180],['hurt',false,120],['knockdown',false,180],['getup',false,180],['carry',true,220],['victory',true,260],['ko',false,240],
] as const);
for(const family of ['glam','prog','punk'] as const){
  registerFamily(family,`enemies.${family}`,`assets/enemies/${family}/${family}-phase2.png`,[
    ['idle',true,260],['walk',true,160],['threaten',true,140],['attack',false,100],['hurt',false,120],['ko',false,240],
  ] as const);
}
export const PHASE2_SPRITE_MANIFEST:Record<string,SpriteAnimationDef>=manifest;
export function framesForVisualState(key:VisualStateKey):SpriteAnimationDef { return PHASE2_SPRITE_MANIFEST[key] ?? FALLBACK_SPRITE; }
export function spriteSheetsForManifest():SpriteSheetDef[]{
  const seen=new Map<string,SpriteSheetDef>();
  for(const def of Object.values(PHASE2_SPRITE_MANIFEST)) for(const frame of def.frames) if(frame.path&&!seen.has(frame.assetKey)) seen.set(frame.assetKey,{assetKey:frame.assetKey,path:frame.path,frameWidth:128,frameHeight:128});
  return [...seen.values()];
}
