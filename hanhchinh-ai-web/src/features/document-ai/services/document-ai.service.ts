import api from "@/lib/api";

import type {
  GenerateDocumentRequest,
  GenerateDocumentResponse,
} from "../types/document.types";

class DocumentAIService {

  async generate(
    request: GenerateDocumentRequest
  ): Promise<GenerateDocumentResponse> {

    const { data } =
      await api.post<GenerateDocumentResponse>(
        "/document/generate",
        request
      );

    return data;
  }

  async download(
    fileName: string
  ): Promise<void> {

    window.open(
      `${import.meta.env.VITE_API_URL}/document/download/${fileName}`,
      "_blank"
    );
  }

  async health() {

    const { data } =
      await api.get("/document/health");

    return data;
  }

  async providers() {

    throw new Error(
      "Provider API chưa được triển khai."
    );
  }
}

export const documentAIService =
  new DocumentAIService();