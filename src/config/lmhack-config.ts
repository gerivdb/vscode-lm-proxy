// /src/config/lmhack-config.ts
import fs from 'fs';
import path from 'path';

export interface LMHackConfig {
  server: { port: number; host: string };
  lmstudio: { endpoint: string; auto_detect: boolean; health_check_interval: number };
  integrations: { anyllm: { enabled: boolean; auto_configure: boolean }, browseros: { enabled: boolean; auto_configure: boolean } };
  features: { context_sharing: boolean; model_management: boolean; performance_monitoring: boolean };
}

const defaultConfig: LMHackConfig = {
  server: { port: Number(process.env.LMHACK_PORT || 4000), host: process.env.LMHACK_HOST || '0.0.0.0' },
  lmstudio: {
    endpoint: process.env.LMSTUDIO_BASE_URL || 'http://localhost:1234',
    auto_detect: true,
    health_check_interval: Number(process.env.LMHACK_HEALTH_INTERVAL || 5000),
  },
  integrations: {
    anyllm: { enabled: true, auto_configure: true },
    browseros: { enabled: true, auto_configure: true },
  },
  features: { context_sharing: true, model_management: true, performance_monitoring: true },
};

export function loadConfig(cwd: string = process.cwd()): LMHackConfig {
  try {
    const file = path.join(cwd, 'lmhack.config.yml');
    if (fs.existsSync(file)) {
      // naive YAML parse to avoid extra deps; accept simple key: value lines
      const raw = fs.readFileSync(file, 'utf-8');
      const cfg = { ...defaultConfig } as any;
      raw.split(/\r?\n/).forEach((line) => {
        const m = line.match(/^\s*([a-zA-Z_\.]+):\s*(.*)$/);
        if (m) {
          const key = m[1];
          const val = m[2].replace(/^["']|["']$/g, '');
          // support a few keys
          if (key === 'server.port') cfg.server.port = Number(val);
          if (key === 'server.host') cfg.server.host = val;
          if (key === 'lmstudio.endpoint') cfg.lmstudio.endpoint = val;
          if (key === 'lmstudio.health_check_interval') cfg.lmstudio.health_check_interval = Number(val);
        }
      });
      return cfg as LMHackConfig;
    }
  } catch (e) {
    // fallback to default
  }
  return defaultConfig;
}
