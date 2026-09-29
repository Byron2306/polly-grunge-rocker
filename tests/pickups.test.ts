import test from 'node:test';
import assert from 'node:assert/strict';
import { createWorld, stepWorld } from '../src/sim/world.js';
import { createPickup, usePickup } from '../src/sim/pickups.js';
const idle={moveX:0,moveY:0,sprint:false,lightPressed:false,heavyPressed:false,interactPressed:false};

test('interaction only collects nearby pickup and L drops held pickup', () => {
  const w=createWorld();
  const near=createPickup('BOTTLE',w.polly.position.x+10,w.polly.position.y);
  const far=createPickup('MIC_STAND',w.polly.position.x+400,w.polly.position.y);
  w.pickups=[near,far];
  stepWorld(w,{...idle,interactPressed:true},16);
  assert.equal(w.polly.heldPickupId,near.id); assert.equal(near.heldBy,'polly');
  stepWorld(w,{...idle,interactPressed:true},16);
  assert.equal(w.polly.heldPickupId,null); assert.equal(near.heldBy,null);
});

test('bottle lasts three hits and mic stand six with longer range', () => {
  const bottle=createPickup('BOTTLE',0,0), mic=createPickup('MIC_STAND',0,0);
  assert.equal(bottle.durability,3); assert.equal(mic.durability,6); assert.ok(mic.rangeX>48);
  usePickup(bottle); usePickup(bottle); assert.equal(bottle.broken,false); usePickup(bottle); assert.equal(bottle.broken,true);
  for(let i=0;i<5;i++) usePickup(mic); assert.equal(mic.broken,false); usePickup(mic); assert.equal(mic.broken,true);
});

test('held mic stand extends a real world light hit and consumes durability on contact', () => {
  const w=createWorld();
  const mic=createPickup('MIC_STAND',w.polly.position.x,w.polly.position.y); mic.heldBy='polly'; w.polly.heldPickupId=mic.id; w.pickups=[mic];
  const enemy = { ...w.polly, id:'target', kind:'GLAM' as const, hp:6, maxHp:6, position:{x:w.polly.position.x+80,y:w.polly.position.y}, attack:null, heldPickupId:null };
  w.enemies=[enemy];
  stepWorld(w,{...idle,lightPressed:true},1);
  stepWorld(w,idle,100);
  assert.ok(enemy.hp<6);
  assert.equal(mic.durability,5);
});
