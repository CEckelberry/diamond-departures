import { chromium } from '@playwright/test';

const browser = await chromium.launch();

for (const mode of ['aesthetic', 'faithful']) {
  const context = await browser.newContext();
  const page = await context.newPage();

  // Navigate and wait for the board to be interactive
  await page.goto('http://localhost:5173', { waitUntil: 'load' });
  await page.waitForTimeout(5000);

  // Set localStorage AND directly apply the body class (mirrors what the store does)
  await page.evaluate((m) => {
    localStorage.setItem('eink-mode', m);
    document.body.classList.remove('eink-aesthetic', 'eink-faithful');
    if (m === 'aesthetic') document.body.classList.add('eink-aesthetic');
    if (m === 'faithful') document.body.classList.add('eink-faithful');
  }, mode);

  // Allow CSS to repaint
  await page.waitForTimeout(500);

  await page.screenshot({ path: `/tmp/eink-${mode}.png`, fullPage: false });
  console.log(`Captured eink-${mode}.png`);
  await context.close();
}

await browser.close();
console.log('Done.');
