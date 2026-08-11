/**
 * Knowledge Types
 * ---------------
 *
 * TypeScript contracts cho Knowledge API.
 *
 * Sprint 12
 * Task 12.13 - Knowledge UI
 */

// ============================================================
// SEARCH REQUEST
// ============================================================

export interface KnowledgeSearchRequest {
  /**
   * Nội dung người dùng muốn tìm kiếm.
   */
  query: string;

  /**
   * Vector embedding của query.
   *
   * Task 12.13 hiện tại vẫn sử dụng
   * contract của Knowledge API 12.12.
   *
   * Sau này EmbeddingService sẽ được
   * backend xử lý thay cho frontend.
   */
  query_vector: number[];

  /**
   * Số lượng kết quả tối đa.
   */
  top_k?: number;

  /**
   * Ngưỡng similarity.
   */
  score_threshold?: number;
}

// ============================================================
// SEARCH RESULT
// ============================================================

export interface KnowledgeSearchItem {
  /**
   * ID của vector/chunk.
   */
  vector_id: string;

  /**
   * Điểm similarity.
   */
  score: number;

  /**
   * Nội dung chunk.
   */
  content: string;

  /**
   * ID tài liệu nguồn.
   */
  document_id?: string | null;

  /**
   * Vị trí chunk trong tài liệu.
   */
  chunk_index?: number | null;

  /**
   * Số trang trong tài liệu.
   */
  page_number?: number | null;

  /**
   * Metadata bổ sung.
   */
  metadata: Record<string, unknown>;
}

// ============================================================
// SEARCH RESPONSE
// ============================================================

export interface KnowledgeSearchResponse {
  /**
   * API xử lý thành công hay không.
   */
  success: boolean;

  /**
   * Query thực tế được tìm kiếm.
   */
  query: string;

  /**
   * Tổng số kết quả.
   */
  total: number;

  /**
   * Danh sách kết quả.
   */
  results: KnowledgeSearchItem[];

  /**
   * Thông báo từ backend.
   */
  message: string;
}

// ============================================================
// UI STATE
// ============================================================

export interface KnowledgeSearchState {
  /**
   * Nội dung ô tìm kiếm.
   */
  query: string;

  /**
   * Số lượng kết quả tối đa.
   */
  topK: number;

  /**
   * Ngưỡng similarity.
   */
  scoreThreshold: number;
}

// ============================================================
// DEFAULT VALUES
// ============================================================

export const DEFAULT_KNOWLEDGE_SEARCH_STATE: KnowledgeSearchState = {
  query: "",
  topK: 5,
  scoreThreshold: 0,
};