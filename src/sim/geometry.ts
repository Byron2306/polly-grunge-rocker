import type { Rect } from './types.js';
export function overlaps(a: Rect, b: Rect): boolean {
  return a.x <= b.x + b.width && a.x + a.width >= b.x && a.y <= b.y + b.height && a.y + a.height >= b.y;
}
export function withinLane(aY: number, bY: number, tolerance: number): boolean {
  return Math.abs(aY - bY) <= tolerance;
}
export function meleeContact(hit: Rect, hurt: Rect, attackerY: number, victimY: number, tolerance: number): boolean {
  return overlaps(hit, hurt) && withinLane(attackerY, victimY, tolerance);
}
export function worldRect(local: Rect, x: number, y: number, facing: -1|1 = 1): Rect {
  return { x: facing === 1 ? x + local.x : x - local.x - local.width, y: y + local.y, width: local.width, height: local.height };
}
