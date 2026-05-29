import { expect, test } from '@playwright/test';

test.describe('sorting data persistence', () => {
	test('clicking a sort header preserves player data', async ({ page }) => {
		await page.goto('/?view=hitters&style=sabermetric');
		await page.waitForSelector('.board-row', { timeout: 10000 });

		// 1. Get initial player count
		const initialCount = await page.locator('.board-row').count();
		console.log('Initial rows:', initialCount);
		expect(initialCount).toBeGreaterThan(0);

		// 2. Click a sort header (e.g., WAR)
		const warBtn = page.locator('.stat-head-btn').filter({ hasText: /^WAR$/i }).first();
		await warBtn.click();
		
		// 3. Wait for data update
		await page.waitForTimeout(3000);
		
		// 4. Verify rows still exist
		const newCount = await page.locator('.board-row').count();
		console.log('New rows after sort:', newCount);
		
		expect(newCount).toBeGreaterThan(0);
		
		// Ensure no 500 error
		const error = page.getByText('500');
		await expect(error).not.toBeVisible();
	});
});
