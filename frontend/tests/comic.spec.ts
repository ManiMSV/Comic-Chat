import { expect, test } from "@playwright/test"

const DEMO_BUTTONS = [
  "A Surprising Find",
  "The Great Argument",
  "A Quiet Tension",
]

test.describe("Comic page", () => {
  test.use({ expect: { timeout: 15000 } })

  test("opens and shows demo picker", async ({ page }) => {
    await page.goto("/comic")

    await expect(page).toHaveURL(/\/comic/)
    await expect(
      page.getByText("Turn a conversation into a comic strip"),
    ).toBeVisible()

    for (const name of DEMO_BUTTONS) {
      await expect(page.getByRole("button", { name })).toBeVisible()
    }
  })

  test("picks a demo dialogue and renders an SVG comic with at least one panel", async ({
    page,
  }) => {
    await page.goto("/comic")

    await page.getByRole("button", { name: "A Surprising Find" }).click()

    const comic = page.getByRole("img", { name: "Comic strip" })
    await expect(comic).toBeVisible()

    await expect(comic.locator('g[aria-label^="Panel"]').first()).toBeVisible()

    await expect(
      page.getByRole("button", { name: "A Surprising Find" }),
    ).toBeVisible()
  })

  test("renders balloon text as real SVG text elements", async ({ page }) => {
    await page.goto("/comic")

    await page.getByRole("button", { name: "The Great Argument" }).click()

    const comic = page.getByRole("img", { name: "Comic strip" })
    await expect(comic).toBeVisible()

    await expect(comic.locator("text").first()).toBeVisible()
  })
})
