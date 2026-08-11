import {
  useMutation,
} from "@tanstack/react-query";

import {
  knowledgeService,
} from "../services/knowledge.service";

import type {
  KnowledgeSearchRequest,
} from "../types/knowledge.types";

export function useKnowledgeSearch() {
  return useMutation({
    mutationFn: (
      request: KnowledgeSearchRequest
    ) =>
      knowledgeService.search(
        request
      ),
  });
}