#!/usr/bin/env node
// Create preview WebP files from one local VRM, without publishing or rewriting it.
import { createReadStream } from 'node:fs';
import { createHash } from 'node:crypto';
import { access, mkdir, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer } from 'vite';
import { chromium } from 'playwright';
import sharp from 'sharp';

const here = path.dirname(fileURLToPath(import.meta.url));

function parseArgs(args) {
  const result = {};
  for (let i = 0; i < args.length; i += 2) {
    if (!args[i]?.startsWith('--') || !args[i + 1]) throw new Error('Expected --key value arguments');
    result[args[i].slice(2)] = args[i + 1];
  }
  if (!result.vrm || !result.id || !result['out-dir']) {
    throw new Error('Usage: node generate.mjs --vrm file.vrm --id catalog-id --out-dir /tmp/previews [--browser /usr/bin/chromium]');
  }
  if (!/^[a-z0-9][a-z0-9-]*$/.test(result.id)) throw new Error('Unsafe catalog ID');
  if (path.extname(result.vrm).toLowerCase() !== '.vrm') throw new Error('Expected .vrm input');
  return result;
}

async function sha256File(file) {
  const hash = createHash('sha256');
  for await (const chunk of createReadStream(file)) hash.update(chunk);
  return hash.digest('hex');
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const modelPath = path.resolve(args.vrm);
  await access(modelPath);
  const fileStat = await stat(modelPath);
  if (!fileStat.isFile() || fileStat.size === 0) throw new Error('No local VRM file');
  const output = path.resolve(args['out-dir']);
  await mkdir(output, { recursive: true });
  const modelHash = await sha256File(modelPath);
  const server = await createServer({
    root: here, configFile: false,
    server: { host: '127.0.0.1', port: 5186, strictPort: false },
    plugins: [{
      name: 'local-vrm-only',
      configureServer(viteServer) {
        viteServer.middlewares.use('/model.vrm', (req, res) => {
          res.setHeader('Content-Type', 'model/gltf-binary');
          res.setHeader('Content-Length', fileStat.size);
          createReadStream(modelPath).on('error', (error) => {
            if (!res.headersSent) res.writeHead(500);
            res.end(String(error));
          }).pipe(res);
        });
      },
    }],
  });
  let browser;
  try {
    await server.listen();
    const base = server.resolvedUrls.local[0].replace('localhost', '127.0.0.1');
    browser = await chromium.launch({
      headless: true,
      ...(args.browser || process.env.CHROMIUM_PATH
        ? { executablePath: args.browser || process.env.CHROMIUM_PATH } : {}),
      args: ['--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader'],
    });
    const page = await browser.newPage({ viewport: { width: 768, height: 1024 }, deviceScaleFactor: 1 });
    // No external services may receive the user's VRM data.
    await page.route('**/*', async (route) => {
      const url = new URL(route.request().url());
      if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
        await route.continue();
      } else {
        await route.abort();
      }
    });
    const result = [];
    for (const view of ['tpose', 'face']) {
      await page.goto(base + '?view=' + view, { waitUntil: 'domcontentloaded' });
      await page.waitForFunction(() => ['ready', 'error'].includes(window.previewStatus?.state), null, { timeout: 60000 });
      const status = await page.evaluate(() => window.previewStatus);
      if (status.state !== 'ready') throw new Error(view + ' rendering failed: ' + status.message);
      const canvas = page.locator('canvas');
      const png = await canvas.screenshot({ type: 'png' });
      const target = path.join(output, args.id + '-' + view + '.webp');
      await sharp(png).webp({ quality: 88, effort: 5 }).toFile(target);
      const metadata = await sharp(target).metadata();
      if (metadata.width !== status.width || metadata.height !== status.height) {
        throw new Error('Preview dimensions mismatch');
      }
      result.push({ view, path: target, width: metadata.width, height: metadata.height, sha256: await sha256File(target) });
    }
    await page.close();
    const manifest = { catalog_id: args.id, vrm_sha256: modelHash,
      previews: result.map(({ view, width, height, sha256 }) => ({
        view, width, height, sha256, filename: args.id + '-' + view + '.webp',
      })) };
    await writeFile(path.join(output, args.id + '-previews.json'),
      JSON.stringify(manifest, null, 2) + '\n', 'utf8');
    process.stdout.write(JSON.stringify(manifest) + '\n');
  } finally {
    if (browser) await browser.close();
    await server.close();
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
