import { expect, test } from '@playwright/test';

test.describe('freeze test', () => {
	test('switching tabs multiple times does not freeze the page', async ({ page }) => {
		await page.goto('/');
		await page.waitForSelector('.board-row', { timeout: 15000 });

		const views = ['PITCHERS', 'HITTERS', 'TRADITIONAL', 'SABER', 'TRADITIONAL', 'PITCHERS'];
		
		for (const label of views) {
			console.log('Clicking ' + label + '...');
			const btn = page.locator('button').filter({ hasText: new RegExp('^' + label + '$', 'i') }).first();
			await btn.click();
			
			// Wait for data change
			await page.waitForTimeout(1000);
			
			// Check if page still responds by finding first brand link
			const brand = page.getByRole('link', { name: 'Diamond Departures' }).first();
			await expect(brand).toBeVisible();
			
			// Confirm board is present
			await expect(page.locator('.board-row').first()).toBeVisible({ timeout: 5000 });
		}
	});
});
