export type AIProvider =
  | "ollama"
  | "gemini"
  | "openai";

/**
 * Request gửi tới Backend
 */
export interface GenerateDocumentRequest {
  provider: AIProvider;

  /**
   * Backend FastAPI sử dụng field "type"
   */
  type: string;

  title: string;

  prompt: string;
}

/**
 * Response trả về từ Backend
 */
export interface GenerateDocumentResponse {
  success: boolean;

  provider: AIProvider;

  /**
   * Loại văn bản
   */
  document_type: string;

  /**
   * Tên file Word đã sinh
   */
  file_name: string;

  /**
   * Nội dung AI sinh
   */
  content: string;

  /**
   * Thông báo từ Backend
   */
  message: string;
}

/**
 * Request xuất file
 * (Chuẩn bị cho Sprint 12)
 */
export interface ExportDocumentRequest {
  fileName: string;

  format: "docx" | "pdf";
}