import { createGameConfig } from './game/config.js';
import { installLandscapeShell } from './platform/mobileShell.js';

installLandscapeShell();
const config = createGameConfig();
if (typeof Phaser !== 'undefined') {
  new Phaser.Game({
    ...config,
    type: Phaser.AUTO,
    parent: 'game-root',
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH, width: 960, height: 540 },
  });
  (globalThis as { __pollyGameCreated?: boolean }).__pollyGameCreated = true;
}
