declare const Phaser: { AUTO:number; Game:new(config:GameConfig)=>unknown; };
interface GameConfig { type?:number;width:number;height:number;pixelArt:boolean;backgroundColor?:string;scene:unknown[];physics?:unknown; }
