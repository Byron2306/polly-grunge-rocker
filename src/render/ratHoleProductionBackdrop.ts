export interface RatHoleBackdropDef {
  assetKey:string;
  path:string;
  worldX:number;
  width:number;
  height:number;
}

export type RatHoleLayerKind='FAR'|'MID'|'NEAR';

export interface RatHoleLayerDef {
  zone:1|2|3;
  kind:RatHoleLayerKind;
  assetKey:string;
  path:string;
  worldX:number;
  width:960;
  height:540;
  depth:number;
  parallax:number;
}

const anchors:[1|2|3,number][]=[[1,0],[2,850],[3,1700]];
const family=(kind:RatHoleLayerKind,depth:number,parallax:number):RatHoleLayerDef[]=>
  anchors.map(([zone,worldX])=>({
    zone,
    kind,
    assetKey:`environment.rathole.production.zone${zone}.${kind.toLowerCase()}`,
    path:`assets/environment/rat-hole/production/zone${zone}-${kind.toLowerCase()}.png`,
    worldX,
    width:960,
    height:540,
    depth,
    parallax,
  }));

export const RAT_HOLE_LAYERS:readonly RatHoleLayerDef[]=[
  ...family('FAR',-300,0.85),
  ...family('MID',-100,1),
  ...family('NEAR',9000,1.08),
];

export function ratHoleLayerScreenX(layer:RatHoleLayerDef,cameraOffsetX:number):number {
  return layer.worldX-cameraOffsetX*layer.parallax;
}

export const RAT_HOLE_BACKDROPS:readonly RatHoleBackdropDef[]=[
  {assetKey:'environment.rathole.zone1',path:'assets/environment/rat-hole/zone1.png',worldX:0,width:960,height:540},
  {assetKey:'environment.rathole.zone2',path:'assets/environment/rat-hole/zone2.png',worldX:850,width:960,height:540},
  {assetKey:'environment.rathole.zone3',path:'assets/environment/rat-hole/zone3.png',worldX:1700,width:960,height:540},
];
export function backdropScreenX(worldX:number,cameraOffsetX:number):number {
  return worldX-cameraOffsetX;
}
