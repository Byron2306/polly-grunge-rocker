import { TouchController } from './touch.js';

export function installTouchControls(controller: TouchController, doc: Document = document): () => void {
  const pad = doc.getElementById('move-pad');
  const stick = doc.getElementById('move-stick');
  const light = doc.getElementById('touch-light');
  const heavy = doc.getElementById('touch-heavy');
  const interact = doc.getElementById('touch-use');
  const sprint = doc.getElementById('touch-sprint');
  if (!pad || !stick || !light || !heavy || !interact || !sprint) return () => {};

  const abort = new AbortController();
  const options = { signal: abort.signal };
  let movePointerId: number | null = null;

  const updateMove = (event: PointerEvent): void => {
    const rect = pad.getBoundingClientRect();
    const radius = Math.max(1, Math.min(rect.width, rect.height) / 2);
    const dx = event.clientX - (rect.left + rect.width / 2);
    const dy = event.clientY - (rect.top + rect.height / 2);
    const distance = Math.hypot(dx, dy);
    const scale = distance > radius ? radius / distance : 1;
    const nx = (dx * scale) / radius;
    const ny = (dy * scale) / radius;
    controller.setMove(nx, ny);
    const visualRadius = radius * 0.46;
    stick.style.transform = `translate(${nx * visualRadius}px, ${ny * visualRadius}px)`;
  };

  const releaseMove = (event: PointerEvent): void => {
    if (movePointerId !== event.pointerId) return;
    movePointerId = null;
    controller.resetMove();
    stick.style.transform = 'translate(0px, 0px)';
  };

  pad.addEventListener('pointerdown', (event) => {
    event.preventDefault();
    movePointerId = event.pointerId;
    pad.setPointerCapture?.(event.pointerId);
    updateMove(event);
  }, options);
  pad.addEventListener('pointermove', (event) => {
    if (movePointerId === event.pointerId) updateMove(event);
  }, options);
  pad.addEventListener('pointerup', releaseMove, options);
  pad.addEventListener('pointercancel', releaseMove, options);
  pad.addEventListener('lostpointercapture', releaseMove, options);

  const bindEdge = (element: HTMLElement, action: () => void): void => {
    element.addEventListener('pointerdown', (event) => {
      event.preventDefault();
      element.setPointerCapture?.(event.pointerId);
      action();
    }, options);
  };
  bindEdge(light, () => controller.pressLight());
  bindEdge(heavy, () => controller.pressHeavy());
  bindEdge(interact, () => controller.pressInteract());

  const stopSprint = (event: PointerEvent): void => {
    event.preventDefault();
    controller.setSprint(false);
  };
  sprint.addEventListener('pointerdown', (event) => {
    event.preventDefault();
    sprint.setPointerCapture?.(event.pointerId);
    controller.setSprint(true);
  }, options);
  sprint.addEventListener('pointerup', stopSprint, options);
  sprint.addEventListener('pointercancel', stopSprint, options);
  sprint.addEventListener('lostpointercapture', stopSprint, options);

  return () => {
    controller.resetMove();
    controller.setSprint(false);
    abort.abort();
  };
}
