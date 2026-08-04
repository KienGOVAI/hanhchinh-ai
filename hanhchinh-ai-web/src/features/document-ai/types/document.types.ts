export type AIProvider =
  | "ollama"
  | "gemini"
  | "openai";

export interface GenerateDocumentRequest {
  provider: AIProvider;

  documentType: string;

  title: string;

  prompt: string;
}

export interface GenerateDocumentResponse {
  success: boolean;

  provider: AIProvider;

  content: string;

  processingTime?: number;

  tokens?: number;
}

export interface ExportDocumentRequest {
  content: string;

  filename: string;

  format: "docx" | "pdf";
}