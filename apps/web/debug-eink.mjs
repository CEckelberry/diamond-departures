import { chromium } from '@playwright/test';

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();

await page.goto('http://localhost:5173', { waitUntil: 'load' });
await page.waitForTimeout(5000);

// Apply the class
await page.evaluate(() => {
  document.body.classList.add('eink-aesthetic');
});

// Check what happened
const result = await page.evaluate(() => {
  const body = document.body;
  const bodyStyle = window.getComputedStyle(body);
  const shellMain = document.querySelector('.shell-main');
  const shellStyle = shellMain ? window.getComputedStyle(shellMain) : null;
  
  // Check CSS variable
  const boardBg = getComputedStyle(document.documentElement).getPropertyValue('--board-bg');
  const boardBgBody = getComputedStyle(document.body).getPropertyValue('--board-bg');
  
  return {
    bodyClasses: body.className,
    bodyBg: bodyStyle.backgroundColor,
    shellBg: shellStyle ? shellStyle.background : 'none found',
    boardBgRoot: boardBg,
    boardBgBody: boardBgBody,
    hasEinkClass: body.classList.contains('eink-aesthetic'),
  };
});

console.log(JSON.stringify(result, null, 2));

await page.screenshot({ path: '/tmp/eink-debug.png' });
await browser.close();
