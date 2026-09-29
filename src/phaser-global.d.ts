declare const Phaser: {
  AUTO:number;
  Scale:{ FIT:number; CENTER_BOTH:number; };
  Game:new(config:GameConfig)=>unknown;
};
interface GameConfig {
  type?:number;
  width:number;
  height:number;
  pixelArt:boolean;
  backgroundColor?:string;
  scene:unknown[];
  physics?:unknown;
  parent?:string;
  scale?:{ mode:number; autoCenter:number; width:number; height:number; };
}
