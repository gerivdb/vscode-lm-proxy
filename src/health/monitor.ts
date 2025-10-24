// /src/health/monitor.ts
import EventEmitter from 'events';
import { LMStudioDetector } from '../detectors/lmstudio';

export class HealthMonitor extends EventEmitter {
  private running = false;
  private lastUp = false;

  constructor(private endpoint: string, private intervalMs: number = 5000) {
    super();
  }

  async start() {
    this.running = true;
    const detector = new LMStudioDetector([this.endpoint]);
    const loop = async () => {
      if (!this.running) return;
      const ok = await detector.testConnection(this.endpoint);
      if (ok && !this.lastUp) this.emit('reconnected');
      if (!ok && this.lastUp) this.emit('disconnected');
      this.lastUp = ok;
      setTimeout(loop, this.intervalMs);
    };
    loop();
  }

  stop() {
    this.running = false;
  }
}
