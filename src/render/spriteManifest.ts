import type { VisualStateKey } from './visualState.js';

export interface SpriteFrameRef { assetKey:string; path:string; frameIndex:number; }
export interface SpriteAnimationDef { key:VisualStateKey; frames:readonly SpriteFrameRef[]; frameMs:number; loop:boolean; family:string; paletteTag:string; }
export interface SpriteSheetDef { assetKey:string; path:string; frameWidth:number; frameHeight:number; }

export const POLLY_HEAVY_FX_KEY='fx.guitar-arc';
const POLLY_MASTER:SpriteFrameRef={assetKey:'characters.polly.master',path:'assets/characters/polly/polly-master.png',frameIndex:0};
export const FALLBACK_SPRITE:SpriteAnimationDef={key:'fallback',frames:[],frameMs:250,loop:true,family:'fallback',paletteTag:'fallback'};

const POLLY_STATES=['idle','walk','sprint','light1','light2','light3','heavy.startup','heavy.active','heavy.recovery','hurt','knockdown','getup','carry','victory','ko'] as const;
const manifest:Record<string,SpriteAnimationDef>={};
for(const state of POLLY_STATES){
  const key=`polly.${state}`;
  manifest[key]={key,frames:[POLLY_MASTER],frameMs:250,loop:true,family:'characters.polly.production-master',paletteTag:'auburn-flannel-production'};
}

export const PHASE2_SPRITE_MANIFEST:Record<string,SpriteAnimationDef>=manifest;
export function framesForVisualState(key:VisualStateKey):SpriteAnimationDef { return PHASE2_SPRITE_MANIFEST[key] ?? FALLBACK_SPRITE; }
export function productionSpriteSheets():SpriteSheetDef[]{ return [{assetKey:POLLY_MASTER.assetKey,path:POLLY_MASTER.path,frameWidth:160,frameHeight:160}]; }
export const spriteSheetsForManifest=productionSpriteSheets;
