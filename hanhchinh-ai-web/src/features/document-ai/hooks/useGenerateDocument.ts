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
    mutationFn: (request) =>
      documentAIService.generate(request),
  });
}