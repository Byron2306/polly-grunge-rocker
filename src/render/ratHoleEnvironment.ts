export type RatHoleLayer='far'|'middle'|'ground'|'foreground';
export type RatHoleKind='SKYLINE'|'BRICK'|'CLUB_DOOR'|'NEON'|'FENCE'|'DUMPSTER'|'ASPHALT'|'PUDDLE'|'POSTERS'|'BAGS'|'CRATE';
export interface RatHoleModule { id:string; layer:RatHoleLayer; kind:RatHoleKind; worldX:number; y:number; width:number; height:number; color:number; accent?:number; parallax:number; }
export interface RatHoleDescriptor extends RatHoleModule { screenX:number; }
export const RAT_HOLE_MODULES:RatHoleModule[]=[
  {id:'skyline',layer:'far',kind:'SKYLINE',worldX:0,y:80,width:2600,height:150,color:0x10131a,accent:0x292538,parallax:.2},
  {id:'brick-a',layer:'middle',kind:'BRICK',worldX:0,y:150,width:900,height:180,color:0x38292d,accent:0x5a3940,parallax:.55},
  {id:'club-door',layer:'middle',kind:'CLUB_DOOR',worldX:190,y:190,width:90,height:140,color:0x18181e,accent:0x711d34,parallax:.55},
  {id:'neon-rat-hole',layer:'middle',kind:'NEON',worldX:125,y:170,width:150,height:44,color:0xd44b78,accent:0xffd2df,parallax:.55},
  {id:'posters',layer:'middle',kind:'POSTERS',worldX:360,y:210,width:150,height:86,color:0xbda56e,accent:0x8b3142,parallax:.55},
  {id:'fence',layer:'middle',kind:'FENCE',worldX:970,y:185,width:390,height:145,color:0x343943,accent:0x646a74,parallax:.72},
  {id:'dumpster',layer:'ground',kind:'DUMPSTER',worldX:1120,y:356,width:130,height:76,color:0x34514b,accent:0x527970,parallax:1},
  {id:'asphalt',layer:'ground',kind:'ASPHALT',worldX:0,y:250,width:2600,height:290,color:0x24242b,accent:0x303039,parallax:1},
  {id:'puddle-1',layer:'ground',kind:'PUDDLE',worldX:520,y:405,width:180,height:26,color:0x263c4e,accent:0x668295,parallax:1},
  {id:'puddle-2',layer:'ground',kind:'PUDDLE',worldX:1570,y:370,width:210,height:24,color:0x263c4e,accent:0x668295,parallax:1},
  {id:'bags',layer:'foreground',kind:'BAGS',worldX:820,y:455,width:82,height:54,color:0x101014,accent:0x282830,parallax:1.08},
  {id:'crate',layer:'foreground',kind:'CRATE',worldX:1760,y:445,width:70,height:60,color:0x5b3c2c,accent:0x8b6045,parallax:1.08},
];
export function environmentDescriptors(cameraOffsetX:number):RatHoleDescriptor[]{ return RAT_HOLE_MODULES.map(m=>({...m,screenX:m.worldX-cameraOffsetX*m.parallax})); }
