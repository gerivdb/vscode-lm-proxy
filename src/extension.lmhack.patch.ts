// Wire LMHack routes into existing server
// /src/extension.lmhack.patch.ts
import * as vscode from 'vscode';
import express from 'express';
import { registerLMHackRoutes } from './server/lmhack-routes';
import { loadConfig } from './config/lmhack-config';
import { HealthMonitor } from './health/monitor';

export function activateLMHack(context: vscode.ExtensionContext, app: express.Express) {
  const cfg = loadConfig();
  // Routes
  registerLMHackRoutes(app);
  // Health monitoring
  const mon = new HealthMonitor(cfg.lmstudio.endpoint, cfg.lmstudio.health_check_interval);
  mon.on('disconnected', () => console.log('[LMHack] LM Studio disconnected'));
  mon.on('reconnected', () => console.log('[LMHack] LM Studio reconnected'));
  mon.start();
  context.subscriptions.push({ dispose: () => mon.stop() });
}
