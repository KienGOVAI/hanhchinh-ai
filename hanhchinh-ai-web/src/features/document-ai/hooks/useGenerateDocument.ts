import { useState } from "react";

import { documentAIService } from "../services/document-ai.service";

import type {
  GenerateDocumentRequest,
  GenerateDocumentResponse,
} from "../types/document.types";

export function useGenerateDocument() {
  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [response, setResponse] =
    useState<GenerateDocumentResponse | null>(null);

  /**
   * Sinh văn bản
   */
  async function generate(
    request: GenerateDocumentRequest
  ) {
    try {
      setLoading(true);

      setError("");

      const result =
        await documentAIService.generate(request);

      setResponse(result);

      return result;
    } catch (err: any) {
      const message =
        err?.response?.data?.message ??
        err?.message ??
        "Không thể sinh văn bản.";

      setError(message);

      throw err;
    } finally {
      setLoading(false);
    }
  }

  /**
   * Reset trạng thái
   */
  function reset() {
    setResponse(null);

    setError("");

    setLoading(false);
  }

  return {
    generate,

    reset,

    loading,

    error,

    response,
  };
}