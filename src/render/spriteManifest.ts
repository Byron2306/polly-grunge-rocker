import type { VisualStateKey } from './visualState.js';

export interface SpriteFrameRef {
  assetKey:string;
  path:string;
  frameIndex:number;
  authoredFacing:1|-1;
}
export interface SpriteAnimationDef {
  key:VisualStateKey;
  frames:readonly SpriteFrameRef[];
  frameMs:number;
  loop:boolean;
  family:string;
  paletteTag:string;
}
export interface SpriteSheetDef {
  assetKey:string;
  path:string;
  frameWidth:number;
  frameHeight:number;
}

export const POLLY_HEAVY_FX_KEY='fx.guitar-arc';

const POLLY_MASTER:SpriteFrameRef={
  assetKey:'characters.polly.master',
  path:'assets/characters/polly/polly-master.png',
  frameIndex:0,
  authoredFacing:1,
};
const GLAM_MASTER:SpriteFrameRef={
  assetKey:'enemies.glam.master',
  path:'assets/enemies/glam/glam-master.png',
  frameIndex:0,
  authoredFacing:1,
};
const PROG_MASTER:SpriteFrameRef={
  assetKey:'enemies.prog.master',
  path:'assets/enemies/prog/prog-master.png',
  frameIndex:0,
  authoredFacing:1,
};
const PUNK_MASTER:SpriteFrameRef={
  assetKey:'enemies.punk.master',
  path:'assets/enemies/punk/punk-master.png',
  frameIndex:0,
  authoredFacing:1,
};

export const FALLBACK_SPRITE:SpriteAnimationDef={
  key:'fallback',frames:[],frameMs:250,loop:true,family:'fallback',paletteTag:'fallback'
};

const POLLY_STATES=[
  'idle','walk','sprint','light1','light2','light3',
  'heavy.startup','heavy.active','heavy.recovery',
  'hurt','knockdown','getup','carry','victory','ko'
] as const;
const ENEMY_STATES=['idle','walk','threaten','attack','hurt','ko'] as const;

const manifest:Record<string,SpriteAnimationDef>={};

for(const state of POLLY_STATES){
  const key=`polly.${state}`;
  manifest[key]={
    key,frames:[POLLY_MASTER],frameMs:250,loop:true,
    family:'characters.polly.production-master',
    paletteTag:'auburn-flannel-production'
  };
}

for(const [family,master,palette] of [
  ['glam',GLAM_MASTER,'magenta-glam-production'],
  ['prog',PROG_MASTER,'scholarly-prog-production'],
  ['punk',PUNK_MASTER,'red-punk-production'],
] as const){
  for(const state of ENEMY_STATES){
    const key=`${family}.${state}`;
    manifest[key]={
      key,frames:[master],frameMs:250,loop:true,
      family:`enemies.${family}.production-master`,
      paletteTag:palette
    };
  }
}

export const PHASE2_SPRITE_MANIFEST:Record<string,SpriteAnimationDef>=manifest;

export function framesForVisualState(key:VisualStateKey):SpriteAnimationDef {
  return PHASE2_SPRITE_MANIFEST[key] ?? FALLBACK_SPRITE;
}

export function productionSpriteSheets():SpriteSheetDef[]{
  return [
    {assetKey:POLLY_MASTER.assetKey,path:POLLY_MASTER.path,frameWidth:128,frameHeight:128},
    {assetKey:GLAM_MASTER.assetKey,path:GLAM_MASTER.path,frameWidth:128,frameHeight:128},
    {assetKey:PROG_MASTER.assetKey,path:PROG_MASTER.path,frameWidth:128,frameHeight:128},
    {assetKey:PUNK_MASTER.assetKey,path:PUNK_MASTER.path,frameWidth:128,frameHeight:128},
  ];
}
export const spriteSheetsForManifest=productionSpriteSheets;
