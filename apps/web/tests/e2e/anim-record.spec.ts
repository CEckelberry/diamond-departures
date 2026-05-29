import { test } from '@playwright/test';

test('record animation', async ({ page }) => {
  await page.goto('/');
  await page.waitForTimeout(6000);
});
