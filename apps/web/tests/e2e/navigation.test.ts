import { expect, test } from '@playwright/test';

test.describe('navigation and filter test', () => {
	test('switching between categories updates headers', async ({ page }) => {
		await page.goto('/');
		await page.waitForSelector('.board-row', { timeout: 20000 });

		// 1. Check Hitters Saber (Default)
		await expect(page.locator('.stat-head-btn').filter({ hasText: /^wRC\+$/i }).first()).toBeVisible();

		// 2. Switch to Pitchers
		await page.locator('button').filter({ hasText: /^Pitchers$/i }).first().click();
		await page.waitForTimeout(2000);
		// Default sort for Pitchers Saber is FIP
		await expect(page.locator('.stat-head-btn').filter({ hasText: /^FIP$/i }).first()).toBeVisible();

		// 3. Switch to Defense
		await page.locator('button').filter({ hasText: /^Defense$/i }).first().click();
		await page.waitForTimeout(2000);
		// Default sort for Defense is OAA
		await expect(page.locator('.stat-head-btn').filter({ hasText: /^OAA$/i }).first()).toBeVisible();
	});

	test('switching style updates sort', async ({ page }) => {
		await page.goto('/');
		await page.waitForSelector('.board-row', { timeout: 20000 });

		// Saber -> Traditional
		await page.locator('button').filter({ hasText: /^Traditional$/i }).first().click();
		await page.waitForTimeout(2000);
		
		// Header should be AVG
		await expect(page.locator('.stat-head-btn').filter({ hasText: /^AVG$/i }).first()).toBeVisible();
		// Active sort should be gold
		await expect(page.locator('.stat-head-btn.active').filter({ hasText: /^AVG$/i }).first()).toBeVisible();
	});
});
