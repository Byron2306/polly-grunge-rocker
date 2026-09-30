import test from 'node:test';
import assert from 'node:assert/strict';
import type { Actor } from '../src/sim/types.js';
import { AttackTokenPool } from '../src/sim/tokens.js';
import { createRatHoleEncounter, updateEncounter } from '../src/sim/encounters.js';
import { WALK_SPEED, VERTICAL_SPEED_RATIO, SPRINT_RATIO, STANDARD_LANE_TOLERANCE, WALKABLE_Y_MIN, WALKABLE_Y_MAX } from '../src/sim/constants.js';
import { visualStateForActor } from '../src/render/visualState.js';
import { framesForVisualState } from '../src/render/spriteManifest.js';
import { presentationForActor } from '../src/render/actorPresenter.js';
import { clampActorsToWalkBand } from '../src/sim/world.js';

const polly:Actor={id:'polly',kind:'POLLY',state:'IDLE',position:{x:120,y:320},velocity:{x:0,y:0},facing:1,hp:12,maxHp:12,stagger:0,staggerResistance:4,body:{x:-14,y:-10,width:28,height:20},hurtbox:{x:-16,y:-86,width:32,height:86},attack:null,hitstopMs:0,hitstunMs:0,invulnerableMs:0,heldPickupId:null,comboIndex:0,comboResetMs:0,queuedLight:false,archetypeTimerMs:0,tokenOwned:false};
const world:any={polly,enemies:[],pickups:[],tokens:new AttackTokenPool(2),elapsedMs:0,sliceComplete:false};
const ko=()=>{for(const e of world.enemies){e.state='KO';e.hp=0;}};

test('Phase2B.1 preserves Phase1 combat truth through all Rat Hole zones',()=>{
  assert.deepEqual([WALK_SPEED,VERTICAL_SPEED_RATIO,SPRINT_RATIO,STANDARD_LANE_TOLERANCE],[180,.82,1.55,24]);
  assert.deepEqual([WALKABLE_Y_MIN,WALKABLE_Y_MAX],[360,485]);

  clampActorsToWalkBand([world.polly]);
  assert.equal(world.polly.position.y,360);

  const enc=createRatHoleEncounter();
  updateEncounter(world,enc,1000);
  assert.equal(enc.stage,'E1');
  assert.equal(world.enemies.length,1);

  for(const a of [world.polly,...world.enemies]){
    const v=visualStateForActor(a),def=framesForVisualState(v.key),before=JSON.stringify(a);
    assert.equal(def.frames.length,1,`${a.kind} has production master`);
    presentationForActor(a,0,true);
    assert.equal(JSON.stringify(a),before);
  }

  ko();updateEncounter(world,enc,16);assert.equal(enc.stage,'MOVE1');
  world.polly.position.x=900;updateEncounter(world,enc,16);assert.equal(enc.stage,'E2');
  updateEncounter(world,enc,1300);assert.equal(world.enemies.length,2);

  for(const a of world.enemies){
    const def=framesForVisualState(visualStateForActor(a).key);
    assert.equal(def.frames.length,1,`${a.kind} has production master`);
  }

  ko();updateEncounter(world,enc,16);assert.equal(enc.stage,'MOVE2');
  world.polly.position.x=1650;updateEncounter(world,enc,16);assert.equal(enc.stage,'E3');
  assert.equal(world.enemies.length,3);

  for(const a of world.enemies){
    const def=framesForVisualState(visualStateForActor(a).key);
    assert.equal(def.frames.length,1,`${a.kind} has production master`);
  }

  ko();
  const events=updateEncounter(world,enc,16);
  assert.equal(enc.stage,'COMPLETE');
  assert.equal(world.sliceComplete,true);
  assert.equal(events.filter(x=>x.type==='SLICE_COMPLETE').length,1);
  assert.ok(world.tokens.ordinaryCount<=2);
});
