export interface RatHoleBackdropDef {
  assetKey:string;
  path:string;
  worldX:number;
  width:number;
  height:number;
}
export const RAT_HOLE_BACKDROPS:readonly RatHoleBackdropDef[]=[
  {assetKey:'environment.rathole.zone1',path:'assets/environment/rat-hole/zone1.png',worldX:0,width:960,height:540},
  {assetKey:'environment.rathole.zone2',path:'assets/environment/rat-hole/zone2.png',worldX:850,width:960,height:540},
  {assetKey:'environment.rathole.zone3',path:'assets/environment/rat-hole/zone3.png',worldX:1700,width:960,height:540},
];
export function backdropScreenX(worldX:number,cameraOffsetX:number):number {
  return worldX-cameraOffsetX;
}
