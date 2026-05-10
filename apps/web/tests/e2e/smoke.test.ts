import { expect, test } from '@playwright/test';

test.describe('smoke test', () => {
	test('homepage loads and shows board', async ({ page }) => {
		await page.goto('/');
		const brand = page.getByRole('link', { name: 'Diamond Departures' });
		await expect(brand).toBeVisible();

		// Check for board or skeleton
		const board = page.locator('.board-layout');
		await expect(board).toBeVisible();

		// Ensure no 500 error message is visible
		const error = page.getByText('500');
		await expect(error).not.toBeVisible();
	});
});
