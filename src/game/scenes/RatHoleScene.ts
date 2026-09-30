import { FixedStepClock } from '../../sim/fixedStep.js';
import { createWorld, stepWorld } from '../../sim/world.js';
import { createRatHoleEncounter, updateEncounter } from '../../sim/encounters.js';
import { createPickup } from '../../sim/pickups.js';
import { blockDescriptors, cameraOffsetX, strikeDescriptors } from '../../render/blockRenderer.js';
import { ActorPresenter } from '../../render/actorPresenter.js';
import { debugGeometryDescriptors, toggleDebugGeometry, type DebugGeometryMode } from '../../render/debugGeometry.js';
import { isDebugTogglePressed, readKeyboardIntent } from '../../input/keyboard.js';
import { TouchController, mergePlayerIntents } from '../../input/touch.js';
import { installTouchControls } from '../../input/touchUi.js';
import { isGameplayInputBlocked } from '../../platform/mobileShell.js';

interface SceneRuntime { world:ReturnType<typeof createWorld>; encounter:ReturnType<typeof createRatHoleEncounter>; clock:FixedStepClock; currentKeys:Set<string>; previousKeys:Set<string>; touchController:TouchController; disposeTouch:()=>void; graphics:any; text:any; hpText:any; moveText:any; presenter:ActorPresenter; debugMode:DebugGeometryMode; }
function runtime(scene:any):SceneRuntime { return scene.__pollyRuntime as SceneRuntime; }
function isMoveStage(stage:string):boolean { return stage==='MOVE1'||stage==='MOVE2'; }
function render(scene:any):void {
  const r=runtime(scene), g=r.graphics, w=r.world, offset=cameraOffsetX(w.polly.position.x);
  g.clear();
  g.fillStyle(0x17171c,1); g.fillRect(0,0,960,540);
  g.fillStyle(0x24242b,1); g.fillRect(0,250,960,250);
  g.lineStyle(2,0x55555d,1); g.strokeRect(40,270,880,210);
  g.fillStyle(0x3b3030,1); g.fillRect(70-offset,210,150,60);

  const actors=[w.polly,...w.enemies].sort((a,b)=>a.position.y-b.position.y);
  r.presenter.removeMissing(actors.map(a=>a.id));
  const fallbackIds=new Set<string>();
  for(const actor of actors){ if(r.presenter.syncActor(actor,offset).fallback) fallbackIds.add(actor.id); }

  for(const b of blockDescriptors(w).filter(b=>fallbackIds.has(b.id)).sort((a,b)=>a.depth-b.depth)){
    const sx=b.x-offset, sy=b.y;
    g.fillStyle(0x000000,.35); g.fillEllipse(sx-20,sy-8,40,12);
    g.fillStyle(b.color,1); g.fillRect(sx-b.width/2,sy-b.height,b.width,b.height);
    g.fillStyle(0x111111,1); g.fillRect(sx-24,sy-b.height-12,48,6);
    g.fillStyle(0x7bd36d,1); g.fillRect(sx-24,sy-b.height-12,48*(Math.max(0,b.hp)/b.maxHp),6);
  }

  for(const strike of strikeDescriptors(w)){
    const sx=strike.x-offset;
    const left=sx-strike.width/2, top=strike.y-strike.height/2;
    if(strike.phase==='TELEGRAPH'){
      g.lineStyle(strike.shape==='RAM'?4:2,strike.color,.62);
      g.strokeRect(left,top,strike.width,strike.height);
    } else {
      const alpha=strike.shape==='GUITAR'?.9:.82;
      g.fillStyle(strike.color,alpha);
      g.fillRect(left,top,strike.width,strike.height);
      g.lineStyle(1,0xffffff,.75);
      g.strokeRect(left,top,strike.width,strike.height);
    }
  }

  for(const p of w.pickups.filter(p=>!p.heldBy&&!p.broken)){
    g.fillStyle(p.kind==='BOTTLE'?0x55aa77:0xaaaaaa,1);
    g.fillRect(p.x-offset-5,p.y-24,10,24);
  }

  if(r.debugMode==='GEOMETRY'){
    for(const d of debugGeometryDescriptors(w)){
      const color=d.kind==='BODY'?0x55ccff:d.kind==='HURT'?0x66ff88:0xffee55;
      g.lineStyle(d.kind==='ATTACK'?3:2,color,.95);
      g.strokeRect(d.x-offset,d.y,d.width,d.height);
    }
  }

  r.text.setText(`STATE ${w.polly.state}  COMBO ${w.polly.comboIndex}  WAVE ${r.encounter.stage}\nJ / LIGHT   K / HEAVY   L / USE   SHIFT / RUN   F2 / DEBUG`);
  r.hpText.setText(`POLLY HP ${w.polly.hp.toFixed(1)} / ${w.polly.maxHp}`);
  r.moveText.setText(isMoveStage(r.encounter.stage)?'MOVE  >>>':'' );
  r.moveText.setVisible(isMoveStage(r.encounter.stage));
  if(w.sliceComplete){r.text.setText('SLICE COMPLETE\nRECTANGLES HAVE PREVAILED.');r.moveText.setVisible(false);}
}
function combatStep(scene:any,dt:number):void {
  const r=runtime(scene);
  if(isDebugTogglePressed(r.currentKeys,r.previousKeys)){ r.debugMode=toggleDebugGeometry(r.debugMode); r.presenter.setDebugGeometry(r.debugMode==='GEOMETRY'); }
  const intent=mergePlayerIntents(readKeyboardIntent(r.currentKeys,r.previousKeys),r.touchController.consumeIntent());
  if(isMoveStage(r.encounter.stage) && intent.moveX>0) intent.sprint=true;
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
    const touchController=new TouchController();
    const disposeTouch=installTouchControls(touchController);
    const presenter=new ActorPresenter(this);
    this.__pollyRuntime={
      world,encounter:createRatHoleEncounter(),clock:new FixedStepClock(),currentKeys,previousKeys:new Set<string>(),touchController,disposeTouch,presenter,debugMode:'AESTHETIC',
      graphics:this.add.graphics(),
      text:this.add.text(18,18,'',{fontFamily:'monospace',fontSize:'15px',color:'#eeeeee'}).setScrollFactor(0),
      hpText:this.add.text(18,500,'',{fontFamily:'monospace',fontSize:'16px',color:'#ffffff'}).setScrollFactor(0),
      moveText:this.add.text(720,88,'',{fontFamily:'monospace',fontSize:'34px',fontStyle:'bold',color:'#ffe276',stroke:'#111111',strokeThickness:5}).setScrollFactor(0),
    } as SceneRuntime;
    this.input.keyboard.on('keydown',(ev:KeyboardEvent)=>currentKeys.add(ev.code));
    this.input.keyboard.on('keyup',(ev:KeyboardEvent)=>currentKeys.delete(ev.code));
    this.events?.once?.('shutdown',()=>{disposeTouch();presenter.destroy();});
    render(this);
  },
  update(this:any,_time:number,delta:number){
    const r=runtime(this);
    if(!isGameplayInputBlocked()) r.clock.advance(delta,dt=>combatStep(this,dt));
    render(this);
  },
};
