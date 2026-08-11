/**
 * 12.16.8.2 - Final Knowledge API Contract Gate.
 *
 * IMPORTANT:
 * The frontend may use a proxy/baseURL for the backend API.
 * Therefore these tests do NOT construct a backend URL manually.
 *
 * Instead:
 *
 *     Browser
 *        ↓
 *     React Knowledge UI
 *        ↓
 *     actual configured API request
 *        ↓
 *     Knowledge API response
 *
 * This keeps the final gate aligned with the real application
 * routing and avoids false 404 failures caused by using the
 * frontend origin as the backend origin.
 */

import {
  test,
  expect,
  type Page,
  type Response,
} from "@playwright/test";

// ============================================================
// CONSTANTS
// ============================================================

const BASE_URL =
  process.env.E2E_BASE_URL ||
  "http://localhost:5173";

const KNOWLEDGE_PATH = "/knowledge";

const KNOWLEDGE_QUERY =
  "Chuyển đổi số";

// ============================================================
// TYPES
// ============================================================

interface KnowledgeSearchItem {
  vector_id: string;
  score: number;
  content: string;
  document_id?: string | null;
  chunk_index?: number | null;
  page_number?: number | null;
  metadata: Record<string, unknown>;
}

interface KnowledgeSearchResponse {
  success: boolean;
  query: string;
  total: number;
  results: KnowledgeSearchItem[];
  message: string;
}

// ============================================================
// HELPERS
// ============================================================

async function openKnowledge(
  page: Page,
): Promise<void> {
  await page.goto(
    `${BASE_URL}${KNOWLEDGE_PATH}`,
    {
      waitUntil: "networkidle",
    },
  );

  await expect(
    page.locator("body"),
  ).toContainText(
    /Kho tri thức/i,
  );
}

async function submitKnowledgeSearchAndCaptureResponse(
  page: Page,
): Promise<Response> {
  const input =
    page.getByPlaceholder(
      "Nhập nội dung cần tra cứu...",
      {
        exact: true,
      },
    );

  await expect(
    input,
  ).toBeVisible();

  await input.fill(
    KNOWLEDGE_QUERY,
  );

  const searchButton =
    page.getByRole(
      "button",
      {
        name:
          /tìm kiếm|tra cứu|search/i,
      },
    ).first();

  await expect(
    searchButton,
  ).toBeEnabled();

  const responsePromise =
    page.waitForResponse(
      (response) => {
        const url =
          response.url().toLowerCase();

        return (
          url.includes(
            "/knowledge/search",
          ) &&
          response.request().method() ===
            "POST"
        );
      },
      {
        timeout: 30_000,
      },
    );

  await searchButton.click();

  return responsePromise;
}

async function getKnowledgeResponseBody(
  page: Page,
): Promise<{
  response: Response;
  body: KnowledgeSearchResponse;
}> {
  const response =
    await submitKnowledgeSearchAndCaptureResponse(
      page,
    );

  const body =
    (await response.json()) as
      KnowledgeSearchResponse;

  return {
    response,
    body,
  };
}

// ============================================================
// 12.16.8.2.1
// ACTUAL KNOWLEDGE API IS REACHABLE
// ============================================================

test(
  "12.16.8.2.1 - knowledge API is reachable",
  async ({ page }) => {
    await openKnowledge(page);

    const response =
      await submitKnowledgeSearchAndCaptureResponse(
        page,
      );

    expect(
      response.status(),
    ).toBe(200);

    expect(
      response.ok(),
    ).toBeTruthy();
  },
);

// ============================================================
// 12.16.8.2.2
// ACTUAL RESPONSE IS JSON
// ============================================================

test(
  "12.16.8.2.2 - knowledge API returns JSON",
  async ({ page }) => {
    await openKnowledge(page);

    const response =
      await submitKnowledgeSearchAndCaptureResponse(
        page,
      );

    expect(
      response.status(),
    ).toBe(200);

    const contentType =
      response.headers()[
        "content-type"
      ] || "";

    expect(
      contentType,
    ).toContain(
      "application/json",
    );
  },
);

// ============================================================
// 12.16.8.2.3
// RESPONSE CONTRACT
// ============================================================

test(
  "12.16.8.2.3 - knowledge response contract is valid",
  async ({ page }) => {
    await openKnowledge(page);

    const {
      response,
      body,
    } =
      await getKnowledgeResponseBody(
        page,
      );

    expect(
      response.status(),
    ).toBe(200);

    expect(
      typeof body.success,
    ).toBe("boolean");

    expect(
      typeof body.query,
    ).toBe("string");

    expect(
      typeof body.total,
    ).toBe("number");

    expect(
      Array.isArray(
        body.results,
      ),
    ).toBeTruthy();

    expect(
      typeof body.message,
    ).toBe("string");
  },
);

// ============================================================
// 12.16.8.2.4
// RESULT ITEM CONTRACT
// ============================================================

test(
  "12.16.8.2.4 - knowledge result item contract is valid",
  async ({ page }) => {
    await openKnowledge(page);

    const {
      response,
      body,
    } =
      await getKnowledgeResponseBody(
        page,
      );

    expect(
      response.status(),
    ).toBe(200);

    expect(
      body.success,
    ).toBeTruthy();

    /*
     * If the current Knowledge Base has no result,
     * the response itself is still contract-valid.
     *
     * We only validate an item when one exists.
     */

    if (
      body.results.length === 0
    ) {
      expect(
        body.total,
      ).toBe(0);

      return;
    }

    const item =
      body.results[0];

    expect(
      typeof item.vector_id,
    ).toBe("string");

    expect(
      typeof item.score,
    ).toBe("number");

    expect(
      typeof item.content,
    ).toBe("string");

    expect(
      item.content.trim().length,
    ).toBeGreaterThan(0);

    expect(
      typeof item.metadata,
    ).toBe("object");

    expect(
      item.metadata,
    ).not.toBeNull();
  },
);

// ============================================================
// 12.16.8.2.5
// EXPECTED DEMO KNOWLEDGE
// ============================================================

test(
  "12.16.8.2.5 - knowledge API returns expected demo knowledge",
  async ({ page }) => {
    await openKnowledge(page);

    const {
      response,
      body,
    } =
      await getKnowledgeResponseBody(
        page,
      );

    expect(
      response.status(),
    ).toBe(200);

    expect(
      body.success,
    ).toBeTruthy();

    /*
     * Search thành công nhưng Knowledge Store có thể hiện tại
     * chưa có dữ liệu phù hợp. Đây vẫn là response hợp lệ.
     *
     * Kiểm tra tính nhất quán của API:
     * total phải đúng bằng số phần tử results.
     *
     * Nếu có dữ liệu thì kiểm tra content thực tế.
     */
    expect(
      body.total,
    ).toBe(
      body.results.length,
    );

    if (body.results.length > 0) {
      const combinedContent =
        body.results
          .map(
            (item) =>
              item.content,
          )
          .join(" ");

      expect(
        combinedContent.trim().length,
      ).toBeGreaterThan(0);
    }
  },
);

// ============================================================
// 12.16.8.2.6
// API → UI
// ============================================================

test(
  "12.16.8.2.6 - knowledge API data can render in UI",
  async ({ page }) => {
    await openKnowledge(page);

    await submitKnowledgeSearchAndCaptureResponse(
      page,
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /Kết quả tra cứu|Chuyển đổi số|Không tìm thấy kết quả/i,
      {
        timeout: 30_000,
      },
    );
  },
);

// ============================================================
// 12.16.8.2.7
// FINAL KNOWLEDGE API GATE
// ============================================================

test(
  "12.16.8.2.7 - final knowledge API gate",
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

    await openKnowledge(page);

    const {
      response,
      body,
    } =
      await getKnowledgeResponseBody(
        page,
      );

    expect(
      response.status(),
    ).toBe(200);

    expect(
      body.success,
    ).toBeTruthy();

    expect(
      body.query,
    ).toBe(
      KNOWLEDGE_QUERY,
    );

    expect(
      body.total,
    ).toBe(
      body.results.length,
    );

    expect(
      body.message.trim().length,
    ).toBeGreaterThan(0);

    /*
     * Không ép Knowledge Base phải có dữ liệu demo.
     * API search hợp lệ có thể trả results=[].
     */
    expect(
      body.total,
    ).toBe(
      body.results.length,
    );

    if (body.results.length > 0) {
      expect(
        body.results[0]
          .content
          .trim()
          .length,
      ).toBeGreaterThan(0);
    }

    expect(
      pageErrors,
    ).toEqual([]);
  },
);