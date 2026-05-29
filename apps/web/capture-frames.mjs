import { chromium } from '@playwright/test';
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const page = await ctx.newPage();
await page.goto('http://localhost:5173');
await page.waitForTimeout(2500);
await page.screenshot({ path: '/tmp/layout-full.png' });
await page.screenshot({ path: '/tmp/layout-header.png', clip: { x: 0, y: 190, width: 1280, height: 320 } });
await browser.close();
