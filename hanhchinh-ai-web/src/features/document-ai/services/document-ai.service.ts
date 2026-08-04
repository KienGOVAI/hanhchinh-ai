import api from "@/lib/api";

import type {
  GenerateDocumentRequest,
  GenerateDocumentResponse,
} from "../types/document.types";

class DocumentAIService {
  /**
   * Gửi yêu cầu tạo văn bản bằng AI
   */
  async generate(
    request: GenerateDocumentRequest
  ): Promise<GenerateDocumentResponse> {
    const { data } =
      await api.post<GenerateDocumentResponse>(
        "/api/documents/generate",
        request
      );

    return data;
  }

  /**
   * Kiểm tra trạng thái AI Provider
   * (Chuẩn bị cho Sprint 11)
   */
  async health() {
    const { data } = await api.get("/api/health");

    return data;
  }

  /**
   * Lấy danh sách AI Provider
   * (Chuẩn bị cho Sprint 11)
   */
  async providers() {
    const { data } = await api.get(
      "/api/providers"
    );

    return data;
  }
}

export const documentAIService =
  new DocumentAIService();