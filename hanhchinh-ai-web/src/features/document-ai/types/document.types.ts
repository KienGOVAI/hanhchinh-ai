/**
 * Document AI Types
 * -----------------
 *
 * Type definitions cho Document AI.
 */

import type { LucideIcon } from "lucide-react";

// ============================================================
// AI PROVIDER
// ============================================================

export type AIProvider =
  | "ollama"
  | "gemini"
  | "openai";

// ============================================================
// DOCUMENT TYPE
// ============================================================

export interface DocumentType {
  /**
   * Mã loại văn bản.
   */
  id: string;

  /**
   * Tên hiển thị.
   */
  name: string;

  /**
   * Mô tả loại văn bản.
   */
  description: string;

  /**
   * Icon hiển thị trên giao diện.
   */
  icon: LucideIcon;
}

// ============================================================
// GENERATE REQUEST
// ============================================================

export interface GenerateDocumentRequest {
  /**
   * AI Provider.
   */
  provider: AIProvider;

  /**
   * Loại văn bản.
   *
   * Backend DocumentRequest sử dụng field "type".
   */
  type: string;

  /**
   * Tiêu đề văn bản.
   */
  title: string;

  /**
   * Yêu cầu gửi tới AI.
   */
  prompt: string;
}

// ============================================================
// GENERATE RESPONSE
// ============================================================

export interface GenerateDocumentResponse {
  /**
   * Trạng thái xử lý.
   */
  success: boolean;

  /**
   * Provider đã sử dụng.
   */
  provider: AIProvider;

  /**
   * Loại văn bản.
   */
  document_type?: string;

  /**
   * Tên file Word sinh ra.
   */
  file_name?: string;

  /**
   * Nội dung văn bản AI sinh ra.
   */
  content: string;

  /**
   * Thông báo từ backend.
   */
  message?: string;

  /**
   * Thời gian xử lý.
   */
  processingTime?: number;

  /**
   * Số token sử dụng.
   */
  tokens?: number;
}

// ============================================================
// EXPORT REQUEST
// ============================================================

export interface ExportDocumentRequest {
  /**
   * Nội dung cần xuất.
   */
  content: string;

  /**
   * Tên file.
   */
  filename: string;

  /**
   * Định dạng xuất.
   */
  format: "docx" | "pdf";
}