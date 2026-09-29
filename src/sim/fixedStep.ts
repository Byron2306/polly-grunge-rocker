export class FixedStepClock {
  public remainderMs = 0;
  constructor(public readonly stepMs = 1000/60, public readonly maxCatchUpSteps = 5) {}
  advance(deltaMs: number, step: (dtMs: number) => void): number {
    const boundedDelta = Math.max(0, deltaMs);
    this.remainderMs += boundedDelta;
    let count = 0;
    while (this.remainderMs + 1e-9 >= this.stepMs && count < this.maxCatchUpSteps) {
      step(this.stepMs);
      this.remainderMs -= this.stepMs;
      count++;
    }
    if (count === this.maxCatchUpSteps && this.remainderMs >= this.stepMs) {
      this.remainderMs %= this.stepMs;
    }
    return count;
  }
}
