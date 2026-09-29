export type LandscapeEntryResult = 'locked' | 'unlocked' | 'failed';
export interface LandscapeActions {
  requestFullscreen?: () => Promise<void>;
  lockLandscape?: () => Promise<void>;
}

let gameplayInputBlocked = false;

export function isPortraitViewport(width: number, height: number): boolean {
  return height > width;
}

export function isGameplayInputBlocked(): boolean {
  return gameplayInputBlocked;
}

export async function enterLandscapeMode(actions: LandscapeActions): Promise<LandscapeEntryResult> {
  try {
    if (actions.requestFullscreen) await actions.requestFullscreen();
    if (actions.lockLandscape) {
      await actions.lockLandscape();
      return 'locked';
    }
    return 'unlocked';
  } catch {
    return 'failed';
  }
}

export function installLandscapeShell(win: Window = window, doc: Document = document): () => void {
  const gate = doc.getElementById('rotate-gate');
  const button = doc.getElementById('enter-landscape');
  const message = doc.getElementById('rotate-message');
  if (!gate || !button || !message) return () => {};

  const coarsePointer = typeof win.matchMedia === 'function' && win.matchMedia('(pointer: coarse)').matches;
  const touchCapable = coarsePointer || (win.navigator?.maxTouchPoints ?? 0) > 0;

  const sync = (): void => {
    const portrait = isPortraitViewport(win.innerWidth, win.innerHeight);
    gameplayInputBlocked = touchCapable && portrait;
    gate.hidden = !gameplayInputBlocked;
    doc.body.classList.toggle('touch-capable', touchCapable);
    doc.body.classList.toggle('portrait-device', gameplayInputBlocked);
  };

  const orientation = win.screen?.orientation as (ScreenOrientation & { lock?: (orientation: 'landscape') => Promise<void> }) | undefined;
  const root = doc.documentElement as HTMLElement & { requestFullscreen?: () => Promise<void> };
  const onEnter = async (): Promise<void> => {
    message.textContent = 'ENTERING LANDSCAPE…';
    const result = await enterLandscapeMode({
      requestFullscreen: root.requestFullscreen ? () => root.requestFullscreen!() : undefined,
      lockLandscape: orientation?.lock ? () => orientation.lock!('landscape') : undefined,
    });
    message.textContent = result === 'failed' ? 'ROTATE PHONE TO LANDSCAPE' : 'ROTATE PHONE TO LANDSCAPE';
    sync();
  };

  button.addEventListener('click', onEnter);
  win.addEventListener('resize', sync);
  win.addEventListener('orientationchange', sync);
  sync();

  return () => {
    gameplayInputBlocked = false;
    button.removeEventListener('click', onEnter);
    win.removeEventListener('resize', sync);
    win.removeEventListener('orientationchange', sync);
  };
}
