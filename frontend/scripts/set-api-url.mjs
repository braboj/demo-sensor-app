// Build-time API URL injection for hosted, cross-origin deploys.
//
// Angular bakes the API URL into the bundle at build time. When the frontend
// and backend share an origin (the nginx/docker-compose path) the committed
// `environment.prod.ts` uses the relative `/api/v1/sensors` and nginx proxies
// it. But on a static-site host like Render the SPA is served from a different
// origin with no proxy, so the bundle needs the backend's absolute URL.
//
// This script writes `environment.prod.ts` from the `API_URL` env var:
//   - API_URL set   -> overwrite the file with that absolute URL.
//   - API_URL unset -> leave the committed same-origin default untouched.
//
// It runs via the npm `prebuild` hook, so a plain `npm run build` stays correct
// in every context (Render sets API_URL; compose and local builds do not).
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const apiUrl = process.env.API_URL?.trim();

if (!apiUrl) {
  console.log(
    '[set-api-url] API_URL not set; keeping committed environment.prod.ts',
  );
  process.exit(0);
}

const here = dirname(fileURLToPath(import.meta.url));
const target = resolve(here, '../src/environments/environment.prod.ts');

const contents = `// GENERATED AT BUILD TIME by scripts/set-api-url.mjs from the API_URL
// environment variable (see docs/DEPLOY.md). The committed same-origin default
// (/api/v1/sensors) is what ships when API_URL is unset; do not hand-edit this
// for hosted deploys.
export const environment = {
  production: true,
  apiUrl: '${apiUrl}',
};
`;

writeFileSync(target, contents);
console.log(`[set-api-url] wrote environment.prod.ts with apiUrl=${apiUrl}`);
