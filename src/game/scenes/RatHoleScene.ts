import { FixedStepClock } from '../../sim/fixedStep.js';
import { createWorld, stepWorld } from '../../sim/world.js';
import { createRatHoleEncounter, updateEncounter } from '../../sim/encounters.js';
import { createPickup } from '../../sim/pickups.js';
import { blockDescriptors, cameraOffsetX, strikeDescriptors } from '../../render/blockRenderer.js';
import { ActorPresenter } from '../../render/actorPresenter.js';
import { debugGeometryDescriptors, toggleDebugGeometry, type DebugGeometryMode } from '../../render/debugGeometry.js';
import { spriteSheetsForManifest } from '../../render/spriteManifest.js';
import { environmentDescriptors, type RatHoleDescriptor } from '../../render/ratHoleEnvironment.js';
import { isDebugTogglePressed, readKeyboardIntent } from '../../input/keyboard.js';
import { TouchController, mergePlayerIntents } from '../../input/touch.js';
import { installTouchControls } from '../../input/touchUi.js';
import { isGameplayInputBlocked } from '../../platform/mobileShell.js';

interface SceneRuntime { world:ReturnType<typeof createWorld>; encounter:ReturnType<typeof createRatHoleEncounter>; clock:FixedStepClock; currentKeys:Set<string>; previousKeys:Set<string>; touchController:TouchController; disposeTouch:()=>void; graphics:any; text:any; hpText:any; moveText:any; presenter:ActorPresenter; debugMode:DebugGeometryMode; }
function runtime(scene:any):SceneRuntime { return scene.__pollyRuntime as SceneRuntime; }
function isMoveStage(stage:string):boolean { return stage==='MOVE1'||stage==='MOVE2'; }
function drawModule(g:any,m:RatHoleDescriptor):void {
  const x=m.screenX,y=m.y;
  g.fillStyle(m.color,1); g.fillRect(x,y,m.width,m.height);
  if(m.kind==='SKYLINE'){g.fillStyle(m.accent??0x292538,1);for(let px=x+30;px<x+m.width;px+=120)g.fillRect(px,y-35-(px%80),70,35+(px%80));}
  if(m.kind==='BRICK'){g.lineStyle(1,m.accent??0x5a3940,.55);for(let yy=y+16;yy<y+m.height;yy+=18){g.lineBetween(x,yy,x+m.width,yy);for(let xx=x+((yy/18)%2?28:0);xx<x+m.width;xx+=56)g.lineBetween(xx,yy-18,xx,yy);}}
  if(m.kind==='CLUB_DOOR'){g.fillStyle(m.accent??0x711d34,1);g.fillRect(x+10,y+14,m.width-20,18);g.fillStyle(0x08080b,1);g.fillRect(x+18,y+44,m.width-36,m.height-52);}
  if(m.kind==='NEON'){g.lineStyle(5,m.color,.35);g.strokeRect(x-5,y-5,m.width+10,m.height+10);g.lineStyle(2,m.accent??0xffffff,1);g.strokeRect(x,y,m.width,m.height);}
  if(m.kind==='POSTERS'){g.fillStyle(m.accent??0x8b3142,1);g.fillRect(x+12,y+9,42,62);g.fillRect(x+70,y+18,54,50);}
  if(m.kind==='FENCE'){g.lineStyle(1,m.accent??0x646a74,.8);for(let xx=x;xx<x+m.width;xx+=20){g.lineBetween(xx,y,xx+70,y+m.height);g.lineBetween(xx+70,y,xx,y+m.height);}}
  if(m.kind==='DUMPSTER'){g.fillStyle(m.accent??0x527970,1);g.fillRect(x-5,y-12,m.width+10,18);g.lineStyle(2,0x1b2d29,1);g.strokeRect(x,y,m.width,m.height);}
  if(m.kind==='PUDDLE'){g.fillStyle(m.accent??0x668295,.38);g.fillEllipse(x+m.width/2,y+m.height/2,m.width,m.height);}
  if(m.kind==='BAGS'){g.fillStyle(m.color,1);g.fillEllipse(x+25,y+30,44,48);g.fillEllipse(x+58,y+34,38,40);}
  if(m.kind==='CRATE'){g.lineStyle(3,m.accent??0x8b6045,1);g.strokeRect(x,y,m.width,m.height);g.lineBetween(x,y,x+m.width,y+m.height);g.lineBetween(x+m.width,y,x,y+m.height);}
}
function render(scene:any):void {
  const r=runtime(scene),g=r.graphics,w=r.world,offset=cameraOffsetX(w.polly.position.x);
  g.clear();g.fillStyle(0x0c0c12,1);g.fillRect(0,0,960,540);
  const env=environmentDescriptors(offset);
  for(const layer of ['far','middle','ground'] as const) for(const m of env.filter(x=>x.layer===layer)) drawModule(g,m);
  const actors=[w.polly,...w.enemies].sort((a,b)=>a.position.y-b.position.y);r.presenter.removeMissing(actors.map(a=>a.id));const fallbackIds=new Set<string>();for(const actor of actors)if(r.presenter.syncActor(actor,offset).fallback)fallbackIds.add(actor.id);
  for(const b of blockDescriptors(w).filter(b=>fallbackIds.has(b.id)).sort((a,b)=>a.depth-b.depth)){const sx=b.x-offset,sy=b.y;g.fillStyle(0x000000,.35);g.fillEllipse(sx-20,sy-8,40,12);g.fillStyle(b.color,1);g.fillRect(sx-b.width/2,sy-b.height,b.width,b.height);g.fillStyle(0x111111,1);g.fillRect(sx-24,sy-b.height-12,48,6);g.fillStyle(0x7bd36d,1);g.fillRect(sx-24,sy-b.height-12,48*(Math.max(0,b.hp)/b.maxHp),6);}
  for(const strike of strikeDescriptors(w)){const sx=strike.x-offset,left=sx-strike.width/2,top=strike.y-strike.height/2;if(strike.phase==='TELEGRAPH'){g.lineStyle(strike.shape==='RAM'?4:2,strike.color,.62);g.strokeRect(left,top,strike.width,strike.height);}else{g.fillStyle(strike.color,strike.shape==='GUITAR'?.9:.82);g.fillRect(left,top,strike.width,strike.height);g.lineStyle(1,0xffffff,.75);g.strokeRect(left,top,strike.width,strike.height);}}
  for(const p of w.pickups.filter(p=>!p.heldBy&&!p.broken)){g.fillStyle(p.kind==='BOTTLE'?0x55aa77:0xaaaaaa,1);g.fillRect(p.x-offset-5,p.y-24,10,24);}
  for(const m of env.filter(x=>x.layer==='foreground'))drawModule(g,m);
  if(r.debugMode==='GEOMETRY')for(const d of debugGeometryDescriptors(w)){const color=d.kind==='BODY'?0x55ccff:d.kind==='HURT'?0x66ff88:0xffee55;g.lineStyle(d.kind==='ATTACK'?3:2,color,.95);g.strokeRect(d.x-offset,d.y,d.width,d.height);}
  r.text.setText(`STATE ${w.polly.state}  COMBO ${w.polly.comboIndex}  WAVE ${r.encounter.stage}\nJ / LIGHT   K / HEAVY   L / USE   SHIFT / RUN   F2 / DEBUG`);r.hpText.setText(`POLLY HP ${w.polly.hp.toFixed(1)} / ${w.polly.maxHp}`);r.moveText.setText(isMoveStage(r.encounter.stage)?'MOVE  >>>':'');r.moveText.setVisible(isMoveStage(r.encounter.stage));if(w.sliceComplete){r.text.setText('SLICE COMPLETE\nBASIC-ASS SPRITES HAVE PREVAILED.');r.moveText.setVisible(false);}
}
function combatStep(scene:any,dt:number):void {const r=runtime(scene);if(isDebugTogglePressed(r.currentKeys,r.previousKeys)){r.debugMode=toggleDebugGeometry(r.debugMode);r.presenter.setDebugGeometry(r.debugMode==='GEOMETRY');}const intent=mergePlayerIntents(readKeyboardIntent(r.currentKeys,r.previousKeys),r.touchController.consumeIntent());if(isMoveStage(r.encounter.stage)&&intent.moveX>0)intent.sprint=true;stepWorld(r.world,intent,dt);updateEncounter(r.world,r.encounter,dt);r.previousKeys=new Set(r.currentKeys);}
export const RatHoleScene={key:'RatHoleScene',preload(this:any){for(const sheet of spriteSheetsForManifest())this.load.spritesheet(sheet.assetKey,sheet.path,{frameWidth:sheet.frameWidth,frameHeight:sheet.frameHeight});},create(this:any){const world=createWorld();world.pickups=[createPickup('BOTTLE',230,340),createPickup('MIC_STAND',1320,320)];const currentKeys=new Set<string>(),touchController=new TouchController(),disposeTouch=installTouchControls(touchController),presenter=new ActorPresenter(this);this.__pollyRuntime={world,encounter:createRatHoleEncounter(),clock:new FixedStepClock(),currentKeys,previousKeys:new Set<string>(),touchController,disposeTouch,presenter,debugMode:'AESTHETIC',graphics:this.add.graphics(),text:this.add.text(18,18,'',{fontFamily:'monospace',fontSize:'15px',color:'#eeeeee'}).setScrollFactor(0),hpText:this.add.text(18,500,'',{fontFamily:'monospace',fontSize:'16px',color:'#ffffff'}).setScrollFactor(0),moveText:this.add.text(720,88,'',{fontFamily:'monospace',fontSize:'34px',fontStyle:'bold',color:'#ffe276',stroke:'#111111',strokeThickness:5}).setScrollFactor(0)} as SceneRuntime;this.input.keyboard.on('keydown',(ev:KeyboardEvent)=>currentKeys.add(ev.code));this.input.keyboard.on('keyup',(ev:KeyboardEvent)=>currentKeys.delete(ev.code));this.events?.once?.('shutdown',()=>{disposeTouch();presenter.destroy();});render(this);},update(this:any,_time:number,delta:number){const r=runtime(this);if(!isGameplayInputBlocked())r.clock.advance(delta,dt=>combatStep(this,dt));render(this);}};
