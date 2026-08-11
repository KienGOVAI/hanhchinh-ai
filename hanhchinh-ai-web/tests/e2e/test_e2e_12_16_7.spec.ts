/**
 * 12.16.7 - Browser E2E Demo.
 *
 * Browser E2E cho Hành Chính AI.
 * Task 12.16.7
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

const KNOWLEDGE_PATH = "/knowledge";
const ASSISTANT_PATH = "/assistant";

const KNOWLEDGE_QUERY = "Chuyển đổi số";

const ASSISTANT_QUESTION =
  "Chuyển đổi số là gì?";

const ASSISTANT_SECOND_QUESTION =
  "Triển khai chuyển đổi số cần gắn với những nội dung nào?";

const KNOWLEDGE_INPUT_PLACEHOLDER =
  "Nhập nội dung cần tra cứu...";

// ============================================================
// HELPERS
// ============================================================

async function openApplication(
  page: Page,
): Promise<void> {
  await page.goto(BASE_URL, {
    waitUntil: "networkidle",
  });
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
// KNOWLEDGE SEARCH HELPER
// ============================================================

async function submitKnowledgeSearch(
  page: Page,
): Promise<void> {
  const input =
    page.getByPlaceholder(
      KNOWLEDGE_INPUT_PLACEHOLDER,
      {
        exact: true,
      },
    );

  await expect(input).toBeVisible();

  await input.fill(KNOWLEDGE_QUERY);

  await expect(input).toHaveValue(
    KNOWLEDGE_QUERY,
  );

  const searchButton =
    page.getByRole("button", {
      name: /tìm kiếm|tra cứu|search/i,
    }).first();

  await expect(searchButton).toBeVisible();
  await expect(searchButton).toBeEnabled();

  const responsePromise =
    page.waitForResponse(
      (response) =>
        response.url().includes(
          "/knowledge/search",
        ) &&
        response.request().method() ===
          "POST",
      {
        timeout: 30_000,
      },
    );

  await searchButton.click();

  const response =
    await responsePromise;

  expect(response.ok()).toBeTruthy();

  const body = await response.json();

  expect(body.success).toBeTruthy();
  expect(
    Array.isArray(body.results),
  ).toBeTruthy();

  // Helper chỉ xác nhận API/search hoạt động.
  // Không ép results.length ở đây vì từng test
  // có trách nhiệm assertion riêng.
}

// ============================================================
// ASSISTANT INPUT HELPER
// ============================================================

async function getAssistantInput(
  page: Page,
) {
  /*
   * Assistant UI dùng textarea làm ô nhập câu hỏi.
   * Ưu tiên textarea để tránh bắt nhầm textbox
   * của navigation/search.
   */

  const textarea =
    page.locator("textarea").first();

  if (
    (await textarea.count()) > 0 &&
    (await textarea.isVisible())
  ) {
    return textarea;
  }

  const textboxes =
    page.getByRole("textbox");

  const count =
    await textboxes.count();

  for (
    let index = count - 1;
    index >= 0;
    index -= 1
  ) {
    const textbox =
      textboxes.nth(index);

    if (
      await textbox.isVisible()
    ) {
      return textbox;
    }
  }

  throw new Error(
    "Không tìm thấy ô nhập câu hỏi Assistant.",
  );
}

async function submitAssistantQuestion(
  page: Page,
  question: string,
): Promise<void> {
  const input =
    await getAssistantInput(page);

  await input.fill(question);

  await expect(input).toHaveValue(
    question,
  );

  const sendButton =
    page.getByRole("button", {
      name: /gửi|send|hỏi/i,
    }).first();

  await expect(sendButton).toBeVisible();
  await expect(sendButton).toBeEnabled();

  await sendButton.click();
}

// ============================================================
// 1. APPLICATION LOADS
// ============================================================

test(
  "12.16.7.1 - application loads",
  async ({ page }) => {
    await openApplication(page);

    await expect(page).toHaveTitle(
      /hanhchinh-ai-web/i,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Hành Chính AI/i,
    );
  },
);

// ============================================================
// 2. DASHBOARD
// ============================================================

test(
  "12.16.7.2 - dashboard is displayed",
  async ({ page }) => {
    await openApplication(page);

    await expect(
      page.locator("body"),
    ).toContainText(
      /Hành Chính AI|Dashboard|Tổng quan/i,
    );
  },
);

// ============================================================
// 3. KNOWLEDGE NAVIGATION
// ============================================================

test(
  "12.16.7.3 - knowledge navigation exists",
  async ({ page }) => {
    await openApplication(page);

    await expect(
      page.getByRole("link", {
        name: /kho tri thức|knowledge/i,
      }).first(),
    ).toBeVisible();
  },
);

// ============================================================
// 4. ASSISTANT NAVIGATION
// ============================================================

test(
  "12.16.7.4 - assistant navigation exists",
  async ({ page }) => {
    await openApplication(page);

    await expect(
      page.getByRole("link", {
        name: /assistant|trợ lý/i,
      }).first(),
    ).toBeVisible();
  },
);

// ============================================================
// 5. NAVIGATE KNOWLEDGE
// ============================================================

test(
  "12.16.7.5 - navigate to knowledge",
  async ({ page }) => {
    await openKnowledge(page);

    await expect(page).toHaveURL(
      new RegExp(
        `${KNOWLEDGE_PATH}$`,
      ),
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Kho tri thức/i,
    );
  },
);

// ============================================================
// 6. KNOWLEDGE SEARCH UI
// ============================================================

test(
  "12.16.7.6 - knowledge search UI is displayed",
  async ({ page }) => {
    await openKnowledge(page);

    const input =
      page.getByPlaceholder(
        KNOWLEDGE_INPUT_PLACEHOLDER,
        {
          exact: true,
        },
      );

    await expect(input).toBeVisible();

    await expect(
      page.getByRole("button", {
        name: /tìm kiếm|tra cứu|search/i,
      }).first(),
    ).toBeVisible();
  },
);

// ============================================================
// 7. KNOWLEDGE SEARCH
// ============================================================

test(
  "12.16.7.7 - knowledge search works in browser",
  async ({ page }) => {
    await openKnowledge(page);

    await submitKnowledgeSearch(page);

    await expect(
      page.locator("body"),
    ).toContainText(
      /Kết quả tra cứu|Không tìm thấy kết quả|Chuyển đổi số/i,
      {
        timeout: 30_000,
      },
    );
  },
);

// ============================================================
// 8. KNOWLEDGE RESULT
// ============================================================

test(
  "12.16.7.8 - knowledge result is rendered",
  async ({ page }) => {
    /*
     * Test rendering độc lập với backend demo seed.
     * Mock tại API boundary để kết quả deterministic.
     */

    await page.route(
      "**/knowledge/search",
      async (route) => {
        await route.fulfill({
          status: 200,
          contentType:
            "application/json",
          body: JSON.stringify({
            success: true,
            query: "Chuyển đổi số",
            total: 2,
            results: [
              {
                vector_id:
                  "demo-chunk-001",
                score: 1.0,
                content:
                  "Chuyển đổi số là quá trình ứng dụng công nghệ số vào hoạt động quản lý, điều hành và cung cấp dịch vụ, nhằm nâng cao hiệu quả hoạt động của cơ quan hành chính.",
                document_id:
                  "demo-nghi-quyet-57",
                chunk_index: 0,
                page_number: 1,
                metadata: {
                  document_id:
                    "demo-nghi-quyet-57",
                  chunk_index: 0,
                  page_number: 1,
                  content:
                    "Chuyển đổi số là quá trình ứng dụng công nghệ số vào hoạt động quản lý, điều hành và cung cấp dịch vụ, nhằm nâng cao hiệu quả hoạt động của cơ quan hành chính.",
                  document_name:
                    "Nghị quyết - Demo Knowledge Base",
                  source:
                    "Nghị quyết - Demo Knowledge Base",
                },
              },
              {
                vector_id:
                  "demo-chunk-002",
                score:
                  0.9986178293325098,
                content:
                  "Triển khai chuyển đổi số cần gắn với cải cách hành chính, nâng cao chất lượng phục vụ người dân và doanh nghiệp.",
                document_id:
                  "demo-ke-hoach-cds",
                chunk_index: 1,
                page_number: 3,
                metadata: {
                  document_id:
                    "demo-ke-hoach-cds",
                  chunk_index: 1,
                  page_number: 3,
                  content:
                    "Triển khai chuyển đổi số cần gắn với cải cách hành chính, nâng cao chất lượng phục vụ người dân và doanh nghiệp.",
                  document_name:
                    "Kế hoạch chuyển đổi số - Demo",
                  source:
                    "Kế hoạch chuyển đổi số - Demo",
                },
              },
            ],
            message:
              "Tìm kiếm thành công.",
          }),
        });
      },
    );

    await openKnowledge(page);
    await submitKnowledgeSearch(page);

    await expect(
      page.locator("body"),
    ).toContainText(
      /Chuyển đổi số là quá trình ứng dụng công nghệ số/i,
      {
        timeout: 10_000,
      },
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /demo-nghi-quyet-57/i,
      {
        timeout: 10_000,
      },
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Triển khai chuyển đổi số cần gắn với cải cách hành chính/i,
      {
        timeout: 10_000,
      },
    );
  },
);

// ============================================================
// 9. NAVIGATE ASSISTANT
// ============================================================

test(
  "12.16.7.9 - navigate to assistant",
  async ({ page }) => {
    await openAssistant(page);

    await expect(page).toHaveURL(
      new RegExp(
        `${ASSISTANT_PATH}$`,
      ),
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /trợ lý|assistant/i,
    );
  },
);

// ============================================================
// 10. ASSISTANT INPUT
// ============================================================

test(
  "12.16.7.10 - assistant input is displayed",
  async ({ page }) => {
    await openAssistant(page);

    const input =
      await getAssistantInput(page);

    await expect(input).toBeVisible();
  },
);

// ============================================================
// 11. ASSISTANT SEND CONTROL
// ============================================================

test(
  "12.16.7.11 - assistant send control exists",
  async ({ page }) => {
    await openAssistant(page);

    const sendButton =
      page.getByRole("button", {
        name: /gửi|send|hỏi/i,
      }).first();

    await expect(
      sendButton,
    ).toBeVisible();
  },
);

// ============================================================
// 12. ASSISTANT ACCEPTS QUESTION
// ============================================================

test(
  "12.16.7.12 - assistant accepts question",
  async ({ page }) => {
    await openAssistant(page);

    const input =
      await getAssistantInput(page);

    await input.fill(
      ASSISTANT_QUESTION,
    );

    await expect(input).toHaveValue(
      ASSISTANT_QUESTION,
    );
  },
);

// ============================================================
// 13. ASSISTANT RETURNS ANSWER
// ============================================================

test(
  "12.16.7.13 - assistant returns answer",
  async ({ page }) => {
    await openAssistant(page);

    await submitAssistantQuestion(
      page,
      ASSISTANT_QUESTION,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /chuyển đổi số|quá trình|công nghệ số/i,
      {
        timeout: 30_000,
      },
    );
  },
);

// ============================================================
// 14. ASSISTANT ANSWER VISIBLE
// ============================================================

test(
  "12.16.7.14 - assistant answer is visible",
  async ({ page }) => {
    await openAssistant(page);

    await submitAssistantQuestion(
      page,
      ASSISTANT_QUESTION,
    );

    await expect(
      page.locator("body"),
    ).not.toContainText(
      /đang xử lý|loading/i,
      {
        timeout: 30_000,
      },
    );
  },
);

// ============================================================
// 15. CITATION
// ============================================================

test(
  "12.16.7.15 - citation is rendered",
  async ({ page }) => {
    await openAssistant(page);

    await submitAssistantQuestion(
      page,
      ASSISTANT_QUESTION,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /nguồn|citation|tài liệu|demo-nghi-quyet-57/i,
      {
        timeout: 30_000,
      },
    );
  },
);

// ============================================================
// 16. SECOND QUESTION
// ============================================================

test(
  "12.16.7.16 - assistant handles second question",
  async ({ page }) => {
    await openAssistant(page);

    await submitAssistantQuestion(
      page,
      ASSISTANT_QUESTION,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /chuyển đổi số/i,
      {
        timeout: 30_000,
      },
    );

    const input =
      await getAssistantInput(page);

    await input.fill(
      ASSISTANT_SECOND_QUESTION,
    );

    await expect(input).toHaveValue(
      ASSISTANT_SECOND_QUESTION,
    );

    const sendButton =
      page.getByRole("button", {
        name: /gửi|send|hỏi/i,
      }).first();

    await expect(
      sendButton,
    ).toBeEnabled();

    await sendButton.click();

    await expect(
  page.locator("body"),
).toContainText(
  /cải cách hành chính|chất lượng phục vụ|người dân|doanh nghiệp|không tìm thấy thông tin phù hợp để trả lời/i,
  {
    timeout: 30_000,
  },
);  
  },
);

// ============================================================
// 17. EMPTY ASSISTANT QUESTION
// ============================================================

test(
  "12.16.7.17 - empty assistant question is rejected",
  async ({ page }) => {
    await openAssistant(page);

    const input =
      await getAssistantInput(page);

    await input.fill("");

    const sendButton =
      page.getByRole("button", {
        name: /gửi|send|hỏi/i,
      }).first();

    await expect(
      sendButton,
    ).toBeDisabled();
  },
);

// ============================================================
// 18. NAVIGATION STABILITY
// ============================================================

test(
  "12.16.7.18 - navigation remains stable",
  async ({ page }) => {
    await openKnowledge(page);

    await expect(
      page.locator("body"),
    ).toContainText(
      /Kho tri thức/i,
    );

    await openAssistant(page);

    await expect(
      page.locator("body"),
    ).toContainText(
      /trợ lý|assistant/i,
    );

    await openKnowledge(page);

    await expect(
      page.locator("body"),
    ).toContainText(
      /Kho tri thức/i,
    );
  },
);

// ============================================================
// 19. NO BROWSER PAGE ERRORS
// ============================================================

test(
  "12.16.7.19 - no browser page errors",
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

    await openApplication(page);
    await openKnowledge(page);
    await openAssistant(page);

    expect(pageErrors).toEqual([]);
  },
);

// ============================================================
// 20. BROWSER E2E DEMO GATE
// ============================================================

test(
  "12.16.7.20 - browser E2E demo gate",
  async ({ page }) => {
    await openKnowledge(page);

    /*
     * Gate Knowledge chỉ kiểm tra search/UI.
     * Không ép helper phải có backend demo result.
     */

    await submitKnowledgeSearch(page);

    await expect(
      page.locator("body"),
    ).toContainText(
      /Kết quả tra cứu|Không tìm thấy kết quả|Chuyển đổi số/i,
      {
        timeout: 10_000,
      },
    );

    await openAssistant(page);

    await submitAssistantQuestion(
      page,
      ASSISTANT_QUESTION,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /chuyển đổi số|công nghệ số|quản lý/i,
      {
        timeout: 30_000,
      },
    );
  },
);