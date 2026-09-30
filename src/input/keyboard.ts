import type { PlayerIntent } from '../sim/types.js';

function down(keys: ReadonlySet<string>, ...codes: string[]): boolean { return codes.some(c => keys.has(c)); }
export function isDebugTogglePressed(current:ReadonlySet<string>,previous:ReadonlySet<string>):boolean { return current.has('F2')&&!previous.has('F2'); }
export function readKeyboardIntent(current: ReadonlySet<string>, previous: ReadonlySet<string>): PlayerIntent {
  const edge = (code: string) => current.has(code) && !previous.has(code);
  return {
    moveX: (down(current,'ArrowRight','KeyD') ? 1 : 0) - (down(current,'ArrowLeft','KeyA') ? 1 : 0),
    moveY: (down(current,'ArrowDown','KeyS') ? 1 : 0) - (down(current,'ArrowUp','KeyW') ? 1 : 0),
    sprint: down(current,'ShiftLeft','ShiftRight'),
    lightPressed: edge('KeyJ'),
    heavyPressed: edge('KeyK'),
    interactPressed: edge('KeyL'),
  };
}
