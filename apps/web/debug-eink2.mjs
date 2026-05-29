import { chromium } from '@playwright/test';

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();

await page.goto('http://localhost:5173', { waitUntil: 'load' });
await page.waitForTimeout(5000);

// Check before adding class
const before = await page.evaluate(() => {
  return getComputedStyle(document.body).getPropertyValue('--board-bg');
});
console.log('Before:', before);

// Add class
await page.evaluate(() => {
  document.body.classList.add('eink-aesthetic');
});

// Force a layout/paint
await page.evaluate(() => document.body.offsetHeight);
await page.waitForTimeout(200);

// Check after adding class  
const after = await page.evaluate(() => {
  const bodyBg = getComputedStyle(document.body).getPropertyValue('--board-bg');
  // Also try manually setting the variable
  const el = document.querySelector('.board-bg, [class*="board"]');
  return {
    bodyVar: bodyBg,
    bodyClass: document.body.className,
    // Check if CSS rules for eink-aesthetic exist at all
    styleSheets: Array.from(document.styleSheets).map(ss => {
      try {
        const rules = Array.from(ss.cssRules || []);
        const einkRules = rules.filter(r => r.selectorText && r.selectorText.includes('eink'));
        return einkRules.map(r => r.selectorText);
      } catch(e) {
        return [`error: ${e.message}`];
      }
    }).flat()
  };
});
console.log('After:', JSON.stringify(after, null, 2));

await browser.close();
