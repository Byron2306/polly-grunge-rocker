import { createGameConfig } from './game/config.js';

const config = createGameConfig();
if (typeof Phaser !== 'undefined') {
  new Phaser.Game({ ...config, type: Phaser.AUTO });
  (globalThis as { __pollyGameCreated?: boolean }).__pollyGameCreated = true;
}
