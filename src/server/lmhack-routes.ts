// /src/server/lmhack-routes.ts
import type { Express } from 'express';
import { loadConfig } from '../config/lmhack-config';
import { LMStudioDetector } from '../detectors/lmstudio';

export function registerLMHackRoutes(app: Express) {
  const cfg = loadConfig();

  app.get('/lmhack/health', async (_req, res) => {
    const det = new LMStudioDetector([cfg.lmstudio.endpoint]);
    const ok = await det.testConnection(cfg.lmstudio.endpoint);
    res.json({ lmstudio: ok ? 'up' : 'down', endpoint: cfg.lmstudio.endpoint });
  });

  app.get('/lmhack/config', (_req, res) => {
    res.json(cfg);
  });

  app.get('/lmhack/models', async (_req, res) => {
    const det = new LMStudioDetector([cfg.lmstudio.endpoint]);
    const models = await det.getAvailableModels(cfg.lmstudio.endpoint);
    res.json({ endpoint: cfg.lmstudio.endpoint, models });
  });
}
