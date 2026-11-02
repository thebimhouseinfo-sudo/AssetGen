import { expect, test } from '@playwright/test';

test('concept tab shows a temporary page and Batch remains accessible', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Concept', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Concept preview' })).toBeVisible();
  await expect(page.getByText('Chưa kết nối trình render HTML')).toBeVisible();
  await expect(page.getByText('Tạo frame', { exact: true })).toHaveCount(0);
  await page.getByRole('button', { name: 'Batch Generate' }).click();
  await expect(page.getByLabel('Hoặc dán nội dung prompt')).toBeVisible();
});
