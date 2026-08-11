import { useState } from "react";
import {
  AlertCircle,
  BookOpen,
  Loader2,
  Search,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import KnowledgeEmptyState from "../components/KnowledgeEmptyState";
import KnowledgeResultCard from "../components/KnowledgeResultCard";
import KnowledgeSearch from "../components/KnowledgeSearch";
import { useKnowledgeSearch } from "../hooks/useKnowledgeSearch";

import type {
  KnowledgeSearchResponse,
} from "../types/knowledge.types";

export default function KnowledgePage() {
  const [query, setQuery] = useState("");

  const [result, setResult] =
    useState<KnowledgeSearchResponse | null>(null);

  const searchMutation = useKnowledgeSearch();

  const handleSearch = () => {
    const value = query.trim();

    if (!value) {
      return;
    }

    // Xóa kết quả cũ trước khi thực hiện tìm kiếm mới.
    setResult(null);

    /*
     * =====================================================
     * TEMPORARY QUERY VECTOR
     * =====================================================
     *
     * Knowledge API 12.12 hiện đang yêu cầu
     * query_vector từ client.
     *
     * Đây là vector kiểm thử Integration.
     *
     * Không phải embedding production.
     *
     * Task 12.14 sẽ chuyển quá trình embedding
     * sang Backend / AI Assistant.
     */
    searchMutation.mutate(
      {
        query: value,
        query_vector: [
          1.0,
          0.0,
          0.0,
        ],
        top_k: 5,
        score_threshold: 0,
      },
      {
        onSuccess: (data) => {
          setResult(data);
        },
      }
    );
  };

  const isLoading = searchMutation.isPending;

  const error = searchMutation.error;

  const hasResults =
    Boolean(result) &&
    result !== null &&
    result.results.length > 0;

  const hasSearched =
    Boolean(result) || Boolean(error);

  return (
    <div className="space-y-6">
      {/* ================================================= */}
      {/* HEADER */}
      {/* ================================================= */}

      <div>
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10">
            <BookOpen className="h-6 w-6 text-primary" />
          </div>

          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              Kho tri thức
            </h1>

            <p className="mt-1 text-muted-foreground">
              Tra cứu thông tin từ Knowledge Base
              của Hành Chính AI.
            </p>
          </div>
        </div>
      </div>

      {/* ================================================= */}
      {/* SEARCH */}
      {/* ================================================= */}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5 text-primary" />

            Tra cứu Knowledge Base
          </CardTitle>
        </CardHeader>

        <CardContent>
          <KnowledgeSearch
            value={query}
            loading={isLoading}
            onChange={setQuery}
            onSearch={handleSearch}
          />

          <p className="mt-3 text-xs text-muted-foreground">
            Nhập từ khóa hoặc nội dung cần tra cứu
            trong kho tri thức.
          </p>
        </CardContent>
      </Card>

      {/* ================================================= */}
      {/* ERROR */}
      {/* ================================================= */}

      {error && (
        <div className="flex gap-3 rounded-lg border border-red-300 bg-red-50 p-4">
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />

          <div>
            <h3 className="font-semibold text-red-700">
              Không thể tra cứu Knowledge Base
            </h3>

            <p className="mt-1 text-sm text-red-600">
              {error instanceof Error
                ? error.message
                : "Đã xảy ra lỗi khi tìm kiếm."}
            </p>
          </div>
        </div>
      )}

      {/* ================================================= */}
      {/* LOADING */}
      {/* ================================================= */}

      {isLoading && (
        <div className="flex min-h-[220px] items-center justify-center rounded-xl border border-dashed">
          <div className="space-y-3 text-center">
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />

            <p className="text-sm text-muted-foreground">
              Đang tìm kiếm trong Knowledge Base...
            </p>
          </div>
        </div>
      )}

      {/* ================================================= */}
      {/* RESULT */}
      {/* ================================================= */}

      {!isLoading && hasResults && result && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">
                Kết quả tra cứu
              </h2>

              <p className="mt-1 text-sm text-muted-foreground">
                Tìm thấy{" "}
                <strong className="text-foreground">
                  {result.total}
                </strong>{" "}
                kết quả cho từ khóa{" "}
                <strong className="text-foreground">
                  “{result.query}”
                </strong>
                .
              </p>
            </div>
          </div>

          <div className="space-y-4">
            {result.results.map((item, index) => (
              <KnowledgeResultCard
                key={item.vector_id}
                result={item}
                index={index + 1}
              />
            ))}
          </div>
        </div>
      )}

      {/* ================================================= */}
      {/* NO RESULT */}
      {/* ================================================= */}

      {!isLoading &&
        !error &&
        hasSearched &&
        result &&
        result.results.length === 0 && (
          <div className="flex min-h-[220px] items-center justify-center rounded-xl border border-dashed">
            <div className="space-y-3 text-center">
              <BookOpen className="mx-auto h-10 w-10 text-muted-foreground" />

              <div>
                <h3 className="font-semibold">
                  Không tìm thấy kết quả
                </h3>

                <p className="mt-1 text-sm text-muted-foreground">
                  Không có tài liệu phù hợp với nội dung
                  “{result.query}”.
                </p>
              </div>
            </div>
          </div>
        )}

      {/* ================================================= */}
      {/* INITIAL EMPTY STATE */}
      {/* ================================================= */}

      {!isLoading &&
        !error &&
        !hasSearched && (
          <KnowledgeEmptyState />
        )}
    </div>
  );
}