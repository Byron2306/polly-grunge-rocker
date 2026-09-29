import type { Actor, ActorState, EnemyKind } from './types.js';
import type { AttackTokenPool, TokenReason } from './tokens.js';
import { PUNK_CHARGE_LANE_TOLERANCE, STANDARD_LANE_TOLERANCE } from './constants.js';

export const COMMON_ENEMY_STATES: ActorState[]=['SPAWN','IDLE','APPROACH','ALIGN','THREATEN','ATTACK','RECOVER','HURT','KNOCKBACK','DOWN','GETUP','KO'];
export interface EnemyConfig { kind:EnemyKind; hp:number; desiredRange:number; laneTolerance:number; anticipationMs:number; activeMs:number; recoveryMs:number; chargeMinMs?:number; chargeMaxMs?:number; }
const CONFIGS:Record<EnemyKind,EnemyConfig>={
  GLAM:{kind:'GLAM',hp:6,desiredRange:58,laneTolerance:STANDARD_LANE_TOLERANCE,anticipationMs:420,activeMs:100,recoveryMs:450},
  PROG:{kind:'PROG',hp:5,desiredRange:78,laneTolerance:STANDARD_LANE_TOLERANCE,anticipationMs:170,activeMs:90,recoveryMs:320},
  PUNK:{kind:'PUNK',hp:6,desiredRange:110,laneTolerance:PUNK_CHARGE_LANE_TOLERANCE,anticipationMs:180,activeMs:500,recoveryMs:500,chargeMinMs:350,chargeMaxMs:600},
};
export function enemyConfig(kind:EnemyKind):EnemyConfig { return CONFIGS[kind]; }
export function progHoldMs(seed01:number):number { return 180 + Math.round(Math.max(0,Math.min(1,seed01))*240); }
let nextEnemyId=1;
export function createEnemy(kind:EnemyKind):Actor {
  const c=CONFIGS[kind];
  return {id:`${kind.toLowerCase()}-${nextEnemyId++}`,kind,state:'SPAWN',position:{x:700,y:320},velocity:{x:0,y:0},facing:-1,hp:c.hp,maxHp:c.hp,stagger:0,staggerResistance:kind==='PUNK'?5:4,
    body:{x:-14,y:-10,width:28,height:20},hurtbox:{x:-16,y:-82,width:32,height:82},attack:null,hitstopMs:0,hitstunMs:0,invulnerableMs:0,heldPickupId:null,comboIndex:0,comboResetMs:0,queuedLight:false,archetypeTimerMs:0,tokenOwned:false};
}
export interface EnemyWorldView { polly:Actor; tokens:AttackTokenPool; seed01:number; }
function reasonFor(kind:EnemyKind):TokenReason { return kind==='PUNK'?'PUNK_CHARGE':kind==='GLAM'?'GLAM_BACKHAND':'PROG_POKE'; }
export function updateEnemy(enemy:Actor,view:EnemyWorldView,dtMs:number):void {
  if(enemy.state==='KO'){ if(enemy.tokenOwned){view.tokens.release(enemy.id); enemy.tokenOwned=false;} return; }
  if(enemy.state==='HURT'||enemy.state==='KNOCKBACK'){ if(enemy.tokenOwned){view.tokens.release(enemy.id);enemy.tokenOwned=false;} enemy.archetypeTimerMs+=dtMs; if(enemy.archetypeTimerMs>=180){enemy.archetypeTimerMs=0;enemy.state='APPROACH';} return; }
  const c=CONFIGS[enemy.kind as EnemyKind];
  if(enemy.state==='SPAWN'){enemy.state='APPROACH';}
  const dx=view.polly.position.x-enemy.position.x, dy=view.polly.position.y-enemy.position.y;
  enemy.facing=dx>=0?1:-1;
  if(enemy.state==='APPROACH'){
    if(Math.abs(dy)>c.laneTolerance){enemy.state='ALIGN'; return;}
    if(Math.abs(dx)>c.desiredRange){ enemy.position.x += Math.sign(dx)*Math.min(Math.abs(dx)-c.desiredRange, 110*dtMs/1000); return; }
    enemy.state='THREATEN'; enemy.archetypeTimerMs=0;
  }
  if(enemy.state==='ALIGN'){
    if(Math.abs(dy)<=c.laneTolerance){enemy.state='THREATEN';enemy.archetypeTimerMs=0;return;}
    enemy.position.y += Math.sign(dy)*Math.min(Math.abs(dy),90*dtMs/1000); return;
  }
  if(enemy.state==='THREATEN'){
    enemy.archetypeTimerMs+=dtMs;
    const extra=enemy.kind==='PROG'?progHoldMs(view.seed01):0;
    if(enemy.archetypeTimerMs>=c.anticipationMs+extra){
      if(view.tokens.acquire(enemy.id,reasonFor(enemy.kind as EnemyKind))){enemy.tokenOwned=true;enemy.state='ATTACK';enemy.archetypeTimerMs=0;}
    }
    return;
  }
  if(enemy.state==='ATTACK'){
    enemy.archetypeTimerMs+=dtMs;
    const attackDuration=enemy.kind==='PUNK' ? (c.chargeMinMs! + Math.round((c.chargeMaxMs!-c.chargeMinMs!)*view.seed01)) : c.activeMs;
    if(enemy.kind==='PUNK') enemy.position.x += enemy.facing*260*dtMs/1000;
    if(enemy.archetypeTimerMs>=attackDuration){enemy.state='RECOVER';enemy.archetypeTimerMs=0;}
    return;
  }
  if(enemy.state==='RECOVER'){
    enemy.archetypeTimerMs+=dtMs;
    if(enemy.archetypeTimerMs>=c.recoveryMs){ if(enemy.tokenOwned){view.tokens.release(enemy.id);enemy.tokenOwned=false;} enemy.archetypeTimerMs=0;enemy.state='APPROACH'; }
  }
}
