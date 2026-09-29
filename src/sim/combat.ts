import type { Actor, AttackDefinition } from './types.js';
import { KNOCKDOWN_INVULN_MS } from './constants.js';

export interface HitResult { hit: boolean; damage: number; knockback: number; ko: boolean; }

export function resolveAttackHit(attacker: Actor, victim: Actor, attack: AttackDefinition): HitResult {
  const runtime = attacker.attack;
  if (!runtime || runtime.phase !== 'ACTIVE' || runtime.definition.id !== attack.id) return {hit:false,damage:0,knockback:0,ko:false};
  if (runtime.hitVictimIds.has(victim.id) || victim.invulnerableMs > 0 || victim.state === 'KO') return {hit:false,damage:0,knockback:0,ko:victim.state==='KO'};
  const dx = (victim.position.x - attacker.position.x) * attacker.facing;
  const lane = Math.abs(victim.position.y - attacker.position.y);
  if (dx < -8 || dx > attack.rangeX || lane > attack.laneTolerance) return {hit:false,damage:0,knockback:0,ko:false};

  runtime.hitVictimIds.add(victim.id);
  victim.hp = Math.max(0, victim.hp - attack.damage);
  victim.stagger += attack.stagger;
  attacker.hitstopMs = Math.max(attacker.hitstopMs, attack.hitstopMs);
  victim.hitstopMs = Math.max(victim.hitstopMs, attack.hitstopMs);
  victim.hitstunMs = Math.max(victim.hitstunMs, attack.id === 'HEAVY' ? 260 : attack.id === 'L3' ? 190 : 130);
  victim.velocity.x = attacker.facing * attack.knockback;
  const ko = victim.hp <= 0;
  if (ko) {
    victim.state = 'KO';
    victim.invulnerableMs = Math.max(victim.invulnerableMs, KNOCKDOWN_INVULN_MS);
  } else if (victim.stagger >= victim.staggerResistance || attack.id === 'HEAVY') {
    victim.state = 'KNOCKBACK';
  } else {
    victim.state = 'HURT';
  }
  return {hit:true, damage:attack.damage, knockback:attack.knockback, ko};
}

export function tickReaction(actor: Actor, dtMs: number): void {
  if (actor.hitstopMs > 0) { actor.hitstopMs = Math.max(0, actor.hitstopMs - dtMs); return; }
  actor.hitstunMs = Math.max(0, actor.hitstunMs - dtMs);
  actor.invulnerableMs = Math.max(0, actor.invulnerableMs - dtMs);
  actor.stagger = Math.max(0, actor.stagger - dtMs * 0.0025);
}
