import { FixedStepClock } from '../../sim/fixedStep.js';
import { createWorld, stepWorld } from '../../sim/world.js';
import { createRatHoleEncounter, updateEncounter } from '../../sim/encounters.js';
import { createPickup } from '../../sim/pickups.js';
import { blockDescriptors, cameraOffsetX } from '../../render/blockRenderer.js';
import { readKeyboardIntent } from '../../input/keyboard.js';

interface SceneRuntime { world:ReturnType<typeof createWorld>; encounter:ReturnType<typeof createRatHoleEncounter>; clock:FixedStepClock; currentKeys:Set<string>; previousKeys:Set<string>; graphics:any; text:any; hpText:any; }
function runtime(scene:any):SceneRuntime { return scene.__pollyRuntime as SceneRuntime; }
function render(scene:any):void {
  const r=runtime(scene), g=r.graphics, w=r.world, offset=cameraOffsetX(w.polly.position.x);
  g.clear();
  g.fillStyle(0x17171c,1); g.fillRect(0,0,960,540);
  g.fillStyle(0x24242b,1); g.fillRect(0,250,960,250);
  g.lineStyle(2,0x55555d,1); g.strokeRect(40,270,880,210);
  g.fillStyle(0x3b3030,1); g.fillRect(70-offset,210,150,60);
  for(const b of blockDescriptors(w).sort((a,b)=>a.depth-b.depth)){
    const sx=b.x-offset, sy=b.y;
    g.fillStyle(0x000000,.35); g.fillEllipse(sx-20,sy-8,40,12);
    g.fillStyle(b.color,1); g.fillRect(sx-b.width/2,sy-b.height,b.width,b.height);
    g.fillStyle(0x111111,1); g.fillRect(sx-24,sy-b.height-12,48,6);
    g.fillStyle(0x7bd36d,1); g.fillRect(sx-24,sy-b.height-12,48*(Math.max(0,b.hp)/b.maxHp),6);
  }
  for(const p of w.pickups.filter(p=>!p.heldBy&&!p.broken)){g.fillStyle(p.kind==='BOTTLE'?0x55aa77:0xaaaaaa,1);g.fillRect(p.x-offset-5,p.y-24,10,24);}
  r.text.setText(`STATE ${w.polly.state}  COMBO ${w.polly.comboIndex}  WAVE ${r.encounter.stage}\nJ light  K guitar  L pickup/drop  SHIFT sprint`);
  r.hpText.setText(`POLLY HP ${w.polly.hp.toFixed(1)} / ${w.polly.maxHp}`);
  if(w.sliceComplete) r.text.setText('SLICE COMPLETE\nRECTANGLES HAVE PREVAILED.');
}
function combatStep(scene:any,dt:number):void {
  const r=runtime(scene), intent=readKeyboardIntent(r.currentKeys,r.previousKeys);
  stepWorld(r.world,intent,dt);
  updateEncounter(r.world,r.encounter,dt);
  r.previousKeys=new Set(r.currentKeys);
}
export const RatHoleScene = {
  key:'RatHoleScene',
  create(this:any){
    const world=createWorld();
    world.pickups=[createPickup('BOTTLE',230,340),createPickup('MIC_STAND',1320,320)];
    const currentKeys=new Set<string>();
    this.__pollyRuntime={world,encounter:createRatHoleEncounter(),clock:new FixedStepClock(),currentKeys,previousKeys:new Set<string>(),graphics:this.add.graphics(),text:this.add.text(18,18,'',{fontFamily:'monospace',fontSize:'15px',color:'#eeeeee'}).setScrollFactor(0),hpText:this.add.text(18,500,'',{fontFamily:'monospace',fontSize:'16px',color:'#ffffff'}).setScrollFactor(0)} as SceneRuntime;
    this.input.keyboard.on('keydown',(ev:KeyboardEvent)=>currentKeys.add(ev.code));
    this.input.keyboard.on('keyup',(ev:KeyboardEvent)=>currentKeys.delete(ev.code));
    render(this);
  },
  update(this:any,_time:number,delta:number){ const r=runtime(this); r.clock.advance(delta,dt=>combatStep(this,dt)); render(this); },
};
