import { useMutation } from "@tanstack/react-query";

import { assistantService } from "../api/assistant.api";

import type {
  AssistantRequest,
} from "../types/assistant.types";

export function useAssistant() {
  return useMutation({
    mutationFn: (
      request: AssistantRequest,
    ) => assistantService.ask(request),
  });
}