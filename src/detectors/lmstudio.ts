// /src/detectors/lmstudio.ts
import http from 'http';
import { URL } from 'url';

export interface LMStudioInstance {
  endpoint: string;
  models?: string[];
}

function httpGetJson(endpoint: string, path: string): Promise<any> {
  const url = new URL(path, endpoint);
  return new Promise((resolve, reject) => {
    const req = http.request(url, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          resolve(null);
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

export class LMStudioDetector {
  constructor(private endpoints: string[] = [process.env.LMSTUDIO_BASE_URL || 'http://localhost:1234']) {}

  async detect(): Promise<LMStudioInstance[]> {
    const results: LMStudioInstance[] = [];
    for (const ep of this.endpoints) {
      const ok = await this.testConnection(ep);
      if (ok) {
        const models = await this.getAvailableModels(ep);
        results.push({ endpoint: ep, models });
      }
    }
    return results;
  }

  async testConnection(endpoint: string): Promise<boolean> {
    try {
      const res = await httpGetJson(endpoint, '/v1/models');
      return Boolean(res);
    } catch {
      return false;
    }
  }

  async getAvailableModels(endpoint: string): Promise<string[]> {
    try {
      const res = await httpGetJson(endpoint, '/v1/models');
      if (res && Array.isArray(res.data)) {
        return res.data.map((m: any) => m.id || m.name).filter(Boolean);
      }
    } catch {}
    return [];
  }
}
