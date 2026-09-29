import { RatHoleScene } from './scenes/RatHoleScene.js';

export function createGameConfig(): GameConfig {
  return {
    width: 960,
    height: 540,
    pixelArt: true,
    backgroundColor: '#111111',
    scene: [RatHoleScene],
  };
}
