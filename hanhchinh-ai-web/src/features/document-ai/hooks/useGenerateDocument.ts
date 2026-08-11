import { useMutation } from "@tanstack/react-query";

import { documentAIService } from "../services/document-ai.service";

import type {
  GenerateDocumentRequest,
  GenerateDocumentResponse,
} from "../types/document.types";

export function useGenerateDocument() {
  return useMutation<
    GenerateDocumentResponse,
    Error,
    GenerateDocumentRequest
  >({
    mutationFn: (
      request: GenerateDocumentRequest
    ) => documentAIService.generate(request),

    onSuccess: (response) => {
      console.log(
        "Sinh văn bản thành công:",
        response.file_name
      );
    },

    onError: (error) => {
      console.error(
        "Sinh văn bản thất bại:",
        error
      );
    },
  });
}