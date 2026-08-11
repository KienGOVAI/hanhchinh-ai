import api from "@/lib/api";

import type {
  KnowledgeSearchRequest,
  KnowledgeSearchResponse,
} from "../types/knowledge.types";

class KnowledgeService {
  /**
   * Tìm kiếm Knowledge Base.
   */
  async search(
    request: KnowledgeSearchRequest
  ): Promise<KnowledgeSearchResponse> {
    const { data } =
      await api.post<KnowledgeSearchResponse>(
        "/knowledge/search",
        request
      );

    return data;
  }
}

export const knowledgeService =
  new KnowledgeService();