/**
 * 12.16.8.5 - Assistant RAG End-to-End Integration Gate.
 *
 * Purpose:
 *   Verify the complete production-facing Assistant pipeline after
 *   Knowledge API, Assistant API and Citation Flow have been validated.
 *
 * Pipeline:
 *
 *   Question
 *      ↓
 *   Assistant UI
 *      ↓
 *   POST /assistant/ask
 *      ↓
 *   Retrieval / RAG
 *      ↓
 *   Answer
 *      ↓
 *   Citations
 *      ↓
 *   Assistant UI
 *
 * This file observes the real request made by the application.
 * It does not construct a backend origin manually.
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

const ASSISTANT_PATH = "/assistant";

const QUESTION =
  "Chuyển đổi số là gì?";

const SECOND_QUESTION =
  "Triển khai chuyển đổi số cần gắn với những nội dung nào?";

// ============================================================
// TYPES
// ============================================================

interface Citation {
  citation_id?: string;
  source?: string;
  document_id?: string | null;
  page_number?: number | null;
  chunk_index?: number | null;
  content?: string;
  label?: string;
  score?: number | null;
  metadata?: Record<string, unknown>;
  [key: string]: unknown;
}

interface AssistantResponse {
  success?: boolean;
  answer?: string;
  question?: string;
  query?: string;
  citations?: Citation[];
  metadata?: Record<string, unknown>;
  message?: string;
  [key: string]: unknown;
}

// ============================================================
// HELPERS
// ============================================================

async function openAssistant(
  page: Page,
): Promise<void> {
  await page.goto(
    `${BASE_URL}${ASSISTANT_PATH}`,
    {
      waitUntil: "networkidle",
    },
  );

  await expect(
    page.locator("body"),
  ).toContainText(
    /Trợ lý Hành Chính AI|Trợ lý AI|Assistant/i,
  );
}

async function getAssistantInput(
  page: Page,
) {
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

async function submitQuestion(
  page: Page,
  question: string,
): Promise<Response> {
  const input =
    await getAssistantInput(page);

  await input.fill(question);

  await expect(
    input,
  ).toHaveValue(question);

  const sendButton =
    page.getByRole(
      "button",
      {
        name: /gửi|send|hỏi/i,
      },
    ).first();

  await expect(
    sendButton,
  ).toBeVisible();

  await expect(
    sendButton,
  ).toBeEnabled();

  const responsePromise =
    page.waitForResponse(
      (response) => {
        const url =
          response.url().toLowerCase();

        return (
          url.includes("/assistant/ask") &&
          response.request().method() === "POST"
        );
      },
      {
        timeout: 30_000,
      },
    );

  await sendButton.click();

  return responsePromise;
}

async function getResponse(
  page: Page,
  question: string = QUESTION,
): Promise<{
  response: Response;
  body: AssistantResponse;
}> {
  const response =
    await submitQuestion(
      page,
      question,
    );

  const body =
    (await response.json()) as AssistantResponse;

  return {
    response,
    body,
  };
}

function citationsOf(
  body: AssistantResponse,
): Citation[] {
  expect(
    Array.isArray(body.citations),
  ).toBeTruthy();

  return body.citations ?? [];
}

function returnedQuestion(
  body: AssistantResponse,
): string {
  return String(
    body.question ??
      body.query ??
      "",
  );
}

// ============================================================
// 12.16.8.5.1
// FULL RAG PIPELINE IS REACHABLE
// ============================================================

test(
  "12.16.8.5.1 - full assistant RAG pipeline is reachable",
  async ({ page }) => {
    await openAssistant(page);

    const response =
      await submitQuestion(
        page,
        QUESTION,
      );

    expect(
      response.status(),
    ).toBe(200);

    expect(
      response.ok(),
    ).toBeTruthy();

    expect(
      response.headers()["content-type"] || "",
    ).toContain(
      "application/json",
    );
  },
);

// ============================================================
// 12.16.8.5.2
// ANSWER IS GROUNDED IN KNOWLEDGE
// ============================================================

test(
  "12.16.8.5.2 - assistant returns grounded knowledge answer",
  async ({ page }) => {
    await openAssistant(page);

    const {
      response,
      body,
    } =
      await getResponse(
        page,
        QUESTION,
      );

    expect(
      response.status(),
    ).toBe(200);

    expect(
      body.success,
    ).not.toBe(false);

    expect(
      typeof body.answer,
    ).toBe("string");

    expect(
      body.answer?.trim().length,
    ).toBeGreaterThan(0);

    /*
     * Demo Knowledge Base đã được xác định ở các task
     * trước bằng nội dung về chuyển đổi số, công nghệ số,
     * quản lý và cung cấp dịch vụ.
     */
    expect(
      body.answer,
    ).toMatch(
      /chuyển đổi số|công nghệ số|quản lý|dịch vụ/i,
    );
  },
);

// ============================================================
// 12.16.8.5.3
// ANSWER + CITATION COHERENCE
// ============================================================

test(
  "12.16.8.5.3 - answer and citation flow are coherent",
  async ({ page }) => {
    await openAssistant(page);

    const {
      response,
      body,
    } =
      await getResponse(
        page,
        QUESTION,
      );

    expect(
      response.status(),
    ).toBe(200);

    expect(
      body.answer,
    ).toBeTruthy();

    const citations =
      citationsOf(body);

    expect(
      citations.length,
    ).toBeGreaterThanOrEqual(1);

    const usableCitation =
      citations.find(
        (citation) =>
          Boolean(
            citation.content,
          ) ||
          Boolean(
            citation.source,
          ) ||
          Boolean(
            citation.document_id,
          ),
      );

    expect(
      usableCitation,
    ).toBeTruthy();

    const metadata =
      body.metadata;

    expect(
      typeof metadata,
    ).toBe("object");

    expect(
      metadata,
    ).not.toBeNull();

    const citationCount =
      metadata?.citation_count;

    if (
      citationCount !== undefined &&
      citationCount !== null
    ) {
      expect(
        Number(citationCount),
      ).toBeGreaterThanOrEqual(1);
    }
  },
);

// ============================================================
// 12.16.8.5.4
// SECOND QUESTION / RAG CONSISTENCY
// ============================================================

test(
  "12.16.8.5.4 - second question preserves RAG consistency",
  async ({ page }) => {
    await openAssistant(page);

    const {
      response,
      body,
    } =
      await getResponse(
        page,
        SECOND_QUESTION,
      );

    expect(
      response.status(),
    ).toBe(200);

    expect(
      returnedQuestion(body),
    ).toBe(
      SECOND_QUESTION,
    );

    expect(
      typeof body.answer,
    ).toBe("string");

    expect(
      body.answer?.trim().length,
    ).toBeGreaterThan(0);

    /*
     * Demo Knowledge Base:
     * "Triển khai chuyển đổi số cần gắn với cải cách
     * hành chính, nâng cao chất lượng phục vụ người dân
     * và doanh nghiệp."
     */
    expect(
      body.answer,
    ).toMatch(
      /cải cách hành chính|chất lượng phục vụ|người dân|doanh nghiệp|chuyển đổi số/i,
    );

    const citations =
      citationsOf(body);

    expect(
      citations.length,
    ).toBeGreaterThanOrEqual(1);
  },
);

// ============================================================
// 12.16.8.5.5
// RAG RESULT IS RENDERED IN UI
// ============================================================

test(
  "12.16.8.5.5 - RAG answer and citation are rendered in UI",
  async ({ page }) => {
    await openAssistant(page);

    const response =
      await submitQuestion(
        page,
        QUESTION,
      );

    expect(
      response.status(),
    ).toBe(200);

    await expect(
      page.locator("body"),
    ).not.toContainText(
      /đang xử lý|loading/i,
      {
        timeout: 30_000,
      },
    );

    await expect(
      page.locator("body"),
    ).toContainText(
      /chuyển đổi số|công nghệ số|quản lý|dịch vụ/i,
      {
        timeout: 30_000,
      },
    );

    /*
     * Citation/source UI có thể dùng nhiều cách đặt nhãn.
     * Kiểm tra theo text nghiệp vụ thay vì class CSS.
     */
    await expect(
      page.locator("body"),
    ).toContainText(
      /nguồn|trích dẫn|citation|tài liệu|tham khảo/i,
      {
        timeout: 30_000,
      },
    );
  },
);

// ============================================================
// 12.16.8.5.6
// NO BROWSER RUNTIME ERROR
// ============================================================

test(
  "12.16.8.5.6 - assistant RAG flow has no browser errors",
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

    await openAssistant(page);

    const {
      response,
      body,
    } =
      await getResponse(
        page,
        QUESTION,
      );

    expect(
      response.status(),
    ).toBe(200);

    expect(
      body.answer,
    ).toBeTruthy();

    expect(
      pageErrors,
    ).toEqual([]);
  },
);

// ============================================================
// 12.16.8.5.7
// FINAL ASSISTANT RAG GATE
// ============================================================

test(
  "12.16.8.5.7 - final assistant RAG integration gate",
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

    await openAssistant(page);

    const {
      response,
      body,
    } =
      await getResponse(
        page,
        SECOND_QUESTION,
      );

    expect(
      response.status(),
    ).toBe(200);

    expect(
      response.ok(),
    ).toBeTruthy();

    expect(
      body.success,
    ).not.toBe(false);

    expect(
      typeof body.answer,
    ).toBe("string");

    expect(
      body.answer?.trim().length,
    ).toBeGreaterThan(0);

    expect(
      returnedQuestion(body),
    ).toBe(
      SECOND_QUESTION,
    );

    const citations =
      citationsOf(body);

    expect(
      citations.length,
    ).toBeGreaterThanOrEqual(1);

    for (
      const citation of citations
    ) {
      expect(
        typeof citation,
      ).toBe("object");

      expect(
        citation,
      ).not.toBeNull();

      expect(
        citation.citation_id ||
          citation.label,
      ).toBeTruthy();

      expect(
        citation.source ||
          citation.document_id,
      ).toBeTruthy();
    }

    const metadata =
      body.metadata;

    expect(
      typeof metadata,
    ).toBe("object");

    expect(
      metadata,
    ).not.toBeNull();

    const citationCount =
      metadata?.citation_count;

    if (
      citationCount !== undefined &&
      citationCount !== null
    ) {
      expect(
        Number(citationCount),
      ).toBeGreaterThanOrEqual(1);
    }

    expect(
      pageErrors,
    ).toEqual([]);
  },
);