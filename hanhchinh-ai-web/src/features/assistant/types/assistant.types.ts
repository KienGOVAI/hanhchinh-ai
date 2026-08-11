/**
 * Assistant Types
 *
 * TypeScript contracts cho Assistant API.
 *
 * Sprint 12
 * Task 12.14.9 - Frontend Assistant
 */

// ============================================================
// REQUEST
// ============================================================

export interface AssistantRequest {
  /**
   * Câu hỏi của người dùng.
   */
  question: string;
}

// ============================================================
// CITATION
// ============================================================

export interface AssistantCitation {
  /**
   * ID citation.
   */
  citation_id: string;

  /**
   * Nguồn tài liệu.
   */
  source: string;

  /**
   * Điểm similarity.
   */
  score: number;

  /**
   * ID tài liệu.
   */
  document_id?: string | null;

  /**
   * Số trang.
   */
  page_number?: number | null;

  /**
   * Vị trí chunk.
   */
  chunk_index?: number | null;

  /**
   * Nội dung nguồn.
   */
  content: string;

  /**
   * Metadata bổ sung.
   */
  metadata: Record<string, unknown>;

  /**
   * Nhãn hiển thị.
   */
  label: string;
}

// ============================================================
// RESPONSE
// ============================================================

export interface AssistantResponse {
  /**
   * API xử lý thành công hay không.
   */
  success: boolean;

  /**
   * Câu hỏi thực tế được xử lý.
   */
  question: string;

  /**
   * Câu trả lời của Assistant.
   */
  answer: string;

  /**
   * Danh sách nguồn trích dẫn.
   */
  citations: AssistantCitation[];

  /**
   * Metadata pipeline.
   */
  metadata: Record<string, unknown>;

  /**
   * Thông báo từ backend.
   */
  message: string;
}

// ============================================================
// UI STATE
// ============================================================

export interface AssistantState {
  /**
   * Nội dung câu hỏi.
   */
  question: string;
}

export const DEFAULT_ASSISTANT_STATE: AssistantState = {
  question: "",
};