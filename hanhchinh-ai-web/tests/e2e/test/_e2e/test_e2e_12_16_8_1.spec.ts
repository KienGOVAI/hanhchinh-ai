/**
 * 12.16.8.1 - Final Regression Gate.
 *
 * Final regression smoke test cho Sprint 12.16.
 *
 * Mục tiêu:
 *
 *     Application
 *        ↓
 *     Dashboard
 *        ↓
 *     Knowledge
 *        ↓
 *     Assistant
 *        ↓
 *     Browser stability
 *
 * Task 12.16.8.1
 *
 * Lưu ý:
 * - Đây là FINAL GATE.
 * - Không phụ thuộc vào dữ liệu Knowledge Base cụ thể.
 * - Không mock API.
 * - Không thay thế các test chi tiết của 12.16.7.
 * - Chỉ xác nhận các luồng nền tảng vẫn hoạt động
 *   sau toàn bộ Sprint 12.16.
 */

import {
  test,
  expect,
  type Page,
} from "@playwright/test";

// ============================================================
// CONSTANTS
// ============================================================

const BASE_URL =
  process.env.E2E_BASE_URL ||
  "http://localhost:5173";

const KNOWLEDGE_PATH =
  "/knowledge";

const ASSISTANT_PATH =
  "/assistant";

// ============================================================
// HELPERS
// ============================================================

async function openApplication(
  page: Page,
): Promise<void> {
  await page.goto(
    BASE_URL,
    {
      waitUntil: "networkidle",
    },
  );
}

async function openKnowledge(
  page: Page,
): Promise<void> {
  await page.goto(
    `${BASE_URL}${KNOWLEDGE_PATH}`,
    {
      waitUntil: "networkidle",
    },
  );
}

async function openAssistant(
  page: Page,
): Promise<void> {
  await page.goto(
    `${BASE_URL}${ASSISTANT_PATH}`,
    {
      waitUntil: "networkidle",
    },
  );
}

// ============================================================
// 1. APPLICATION BOOT
// ============================================================

test(
  "12.16.8.1.1 - application boot regression",
  async ({ page }) => {
    const pageErrors: string[] = [];

    page.on(
      "pageerror",
      (error) => {
        pageErrors.push(
          error.message,
        );
      },
    );

    await openApplication(
      page,
    );

    await expect(
      page,
    ).toHaveTitle(
      /hanhchinh-ai-web/i,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Hành Chính AI/i,
    );

    expect(
      pageErrors,
    ).toEqual([]);
  },
);

// ============================================================
// 2. DASHBOARD REGRESSION
// ============================================================

test(
  "12.16.8.1.2 - dashboard regression",
  async ({ page }) => {
    await openApplication(
      page,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Hành Chính AI|Dashboard|Tổng quan/i,
    );

    await expect(
      page.getByRole(
        "link",
        {
          name: /kho tri thức|knowledge/i,
        },
      ).first(),
    ).toBeVisible();

    await expect(
      page.getByRole(
        "link",
        {
          name: /assistant|trợ lý/i,
        },
      ).first(),
    ).toBeVisible();
  },
);

// ============================================================
// 3. KNOWLEDGE ROUTE REGRESSION
// ============================================================

test(
  "12.16.8.1.3 - knowledge route regression",
  async ({ page }) => {
    const pageErrors: string[] = [];

    page.on(
      "pageerror",
      (error) => {
        pageErrors.push(
          error.message,
        );
      },
    );

    await openKnowledge(
      page,
    );

    await expect(
      page,
    ).toHaveURL(
      new RegExp(
        `${KNOWLEDGE_PATH}$`,
      ),
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Kho tri thức/i,
    );

    await expect(
      page.getByPlaceholder(
        "Nhập nội dung cần tra cứu...",
        {
          exact: true,
        },
      ),
    ).toBeVisible();

    expect(
      pageErrors,
    ).toEqual([]);
  },
);

// ============================================================
// 4. ASSISTANT ROUTE REGRESSION
// ============================================================

test(
  "12.16.8.1.4 - assistant route regression",
  async ({ page }) => {
    const pageErrors: string[] = [];

    page.on(
      "pageerror",
      (error) => {
        pageErrors.push(
          error.message,
        );
      },
    );

    await openAssistant(
      page,
    );

    await expect(
      page,
    ).toHaveURL(
      new RegExp(
        `${ASSISTANT_PATH}$`,
      ),
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Trợ lý Hành Chính AI|trợ lý|assistant/i,
    );

    await expect(
      page.getByRole(
        "textbox",
      ).last(),
    ).toBeVisible();

    expect(
      pageErrors,
    ).toEqual([]);
  },
);

// ============================================================
// 5. CROSS-ROUTE NAVIGATION REGRESSION
// ============================================================

test(
  "12.16.8.1.5 - cross route navigation regression",
  async ({ page }) => {
    const pageErrors: string[] = [];

    page.on(
      "pageerror",
      (error) => {
        pageErrors.push(
          error.message,
        );
      },
    );

    /*
     * Dashboard
     */

    await openApplication(
      page,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Hành Chính AI/i,
    );

    /*
     * Knowledge
     */

    await openKnowledge(
      page,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Kho tri thức/i,
    );

    /*
     * Assistant
     */

    await openAssistant(
      page,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Trợ lý|assistant/i,
    );

    /*
     * Quay lại Knowledge để bảo đảm
     * SPA routing không bị hỏng.
     */

    await openKnowledge(
      page,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Kho tri thức/i,
    );

    expect(
      pageErrors,
    ).toEqual([]);
  },
);

// ============================================================
// 6. FINAL BROWSER STABILITY GATE
// ============================================================

test(
  "12.16.8.1.6 - final browser stability gate",
  async ({ page }) => {
    const pageErrors: string[] = [];

    const consoleErrors: string[] = [];

    page.on(
      "pageerror",
      (error) => {
        pageErrors.push(
          error.message,
        );
      },
    );

    page.on(
      "console",
      (message) => {
        if (
          message.type() ===
          "error"
        ) {
          consoleErrors.push(
            message.text(),
          );
        }
      },
    );

    await openApplication(
      page,
    );

    await openKnowledge(
      page,
    );

    await openAssistant(
      page,
    );

    expect(
      pageErrors,
    ).toEqual([]);

    /*
     * Không bắt console warning.
     * Chỉ kiểm tra console.error.
     */

    expect(
      consoleErrors,
    ).toEqual([]);
  },
);

// ============================================================
// 7. FINAL REGRESSION GATE
// ============================================================

test(
  "12.16.8.1.7 - final regression gate",
  async ({ page }) => {
    const pageErrors: string[] = [];

    page.on(
      "pageerror",
      (error) => {
        pageErrors.push(
          error.message,
        );
      },
    );

    /*
     * 1. Application
     */

    await openApplication(
      page,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Hành Chính AI/i,
    );

    /*
     * 2. Knowledge
     */

    await openKnowledge(
      page,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Kho tri thức/i,
    );

    await expect(
      page.getByPlaceholder(
        "Nhập nội dung cần tra cứu...",
        {
          exact: true,
        },
      ),
    ).toBeVisible();

    /*
     * 3. Assistant
     */

    await openAssistant(
      page,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Trợ lý Hành Chính AI|trợ lý|assistant/i,
    );

    await expect(
      page.getByRole(
        "textbox",
      ).last(),
    ).toBeVisible();

    /*
     * 4. Browser stability
     */

    expect(
      pageErrors,
    ).toEqual([]);
  },
);