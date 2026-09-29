import type { PlayerIntent } from '../sim/types.js';

const clampAxis = (value:number):number => Math.max(-1, Math.min(1, value));
const neutral = ():PlayerIntent => ({moveX:0,moveY:0,sprint:false,lightPressed:false,heavyPressed:false,interactPressed:false});

export class TouchController {
  private moveX = 0;
  private moveY = 0;
  private sprint = false;
  private light = false;
  private heavy = false;
  private interact = false;

  setMove(x:number,y:number):void { this.moveX=clampAxis(x); this.moveY=clampAxis(y); }
  setSprint(held:boolean):void { this.sprint=held; }
  pressLight():void { this.light=true; }
  pressHeavy():void { this.heavy=true; }
  pressInteract():void { this.interact=true; }
  resetMove():void { this.moveX=0; this.moveY=0; }

  consumeIntent():PlayerIntent {
    const intent:PlayerIntent={moveX:this.moveX,moveY:this.moveY,sprint:this.sprint,lightPressed:this.light,heavyPressed:this.heavy,interactPressed:this.interact};
    this.light=false; this.heavy=false; this.interact=false;
    return intent;
  }
}

export function mergePlayerIntents(...intents:PlayerIntent[]):PlayerIntent {
  const result=neutral();
  for(const intent of intents){
    result.moveX=clampAxis(result.moveX+intent.moveX);
    result.moveY=clampAxis(result.moveY+intent.moveY);
    result.sprint ||= intent.sprint;
    result.lightPressed ||= intent.lightPressed;
    result.heavyPressed ||= intent.heavyPressed;
    result.interactPressed ||= intent.interactPressed;
  }
  return result;
}
