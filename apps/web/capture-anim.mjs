import { chromium } from '@playwright/test';
import { mkdir } from 'fs/promises';

await mkdir('/tmp/pw-video', { recursive: true });

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width: 1280, height: 900 },
  recordVideo: { dir: '/tmp/pw-video/', size: { width: 1280, height: 900 } }
});
const page = await context.newPage();
await page.goto('http://localhost:5173');
await page.waitForTimeout(5000);
await page.close();
await context.close();
await browser.close();
console.log('Done - check /tmp/pw-video/');
