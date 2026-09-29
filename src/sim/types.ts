export type Facing = -1 | 1;
export type ActorState = 'SPAWN'|'IDLE'|'APPROACH'|'ALIGN'|'THREATEN'|'ATTACK'|'RECOVER'|'HURT'|'KNOCKBACK'|'DOWN'|'GETUP'|'KO';
export type AttackPhase = 'NONE'|'STARTUP'|'ACTIVE'|'RECOVERY';
export type EnemyKind = 'GLAM'|'PROG'|'PUNK';
export type PickupKind = 'BOTTLE'|'MIC_STAND';
export interface Vec2 { x: number; y: number; }
export interface Rect { x: number; y: number; width: number; height: number; }
export interface AttackDefinition {
  id: string;
  startupMs: number;
  activeMs: number;
  recoveryMs: number;
  damage: number;
  stagger: number;
  rangeX: number;
  laneTolerance: number;
  knockback: number;
  hitstopMs: number;
}
export interface AttackRuntime {
  definition: AttackDefinition;
  phase: AttackPhase;
  elapsedMs: number;
  hitVictimIds: Set<string>;
}
export interface Actor {
  id: string;
  kind: 'POLLY' | EnemyKind;
  state: ActorState;
  position: Vec2;
  velocity: Vec2;
  facing: Facing;
  hp: number;
  maxHp: number;
  stagger: number;
  staggerResistance: number;
  body: Rect;
  hurtbox: Rect;
  attack: AttackRuntime | null;
  hitstopMs: number;
  hitstunMs: number;
  invulnerableMs: number;
  heldPickupId: string | null;
  comboIndex: 0|1|2|3;
  comboResetMs: number;
  queuedLight: boolean;
  archetypeTimerMs: number;
  tokenOwned: boolean;
}
export interface PlayerIntent {
  moveX: number;
  moveY: number;
  sprint: boolean;
  lightPressed: boolean;
  heavyPressed: boolean;
  interactPressed: boolean;
}
