import {
  FileText,
  Hash,
  Layers,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import type {
  KnowledgeSearchItem,
} from "../types/knowledge.types";

interface KnowledgeResultCardProps {
  result: KnowledgeSearchItem;
  index: number;
}

export default function KnowledgeResultCard({
  result,
  index,
}: KnowledgeResultCardProps) {
  const scorePercent =
    Math.round(result.score * 100);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-start gap-3 text-base">
          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
            {index}
          </span>

          <span className="line-clamp-2">
            {result.metadata.source
              ? String(
                  result.metadata.source
                )
              : result.document_id ||
                "Tài liệu Knowledge Base"}
          </span>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        <p className="whitespace-pre-wrap text-sm leading-7 text-foreground">
          {result.content}
        </p>

        <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
          {result.document_id && (
            <span className="inline-flex items-center gap-1">
              <FileText className="h-3.5 w-3.5" />
              {result.document_id}
            </span>
          )}

          {result.page_number != null && (
            <span className="inline-flex items-center gap-1">
              <Layers className="h-3.5 w-3.5" />
              Trang {result.page_number}
            </span>
          )}

          {result.chunk_index != null && (
            <span className="inline-flex items-center gap-1">
              <Hash className="h-3.5 w-3.5" />
              Chunk {result.chunk_index}
            </span>
          )}

          <span>
            Độ tương đồng:{" "}
            <strong className="text-foreground">
              {scorePercent}%
            </strong>
          </span>
        </div>
      </CardContent>
    </Card>
  );
}