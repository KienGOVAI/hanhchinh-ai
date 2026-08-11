import {
  FileText,
  MapPin,
} from "lucide-react";

import type {
  AssistantCitation as AssistantCitationType,
} from "../types/assistant.types";

interface AssistantCitationProps {
  citation: AssistantCitationType;
  index: number;
}

export default function AssistantCitation({
  citation,
  index,
}: AssistantCitationProps) {
  return (
    <div className="rounded-lg border bg-muted/30 p-4">
      <div className="flex items-start gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10">
          <FileText className="h-4 w-4 text-primary" />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold">
              [{index}]
            </span>

            <span className="font-medium">
              {citation.label || citation.source}
            </span>
          </div>

          <div className="mt-2 flex flex-wrap gap-3 text-xs text-muted-foreground">
            {citation.source && (
              <span>
                Nguồn: {citation.source}
              </span>
            )}

            {citation.page_number !== null &&
              citation.page_number !== undefined && (
                <span className="flex items-center gap-1">
                  <MapPin className="h-3 w-3" />
                  Trang {citation.page_number}
                </span>
              )}

            {citation.chunk_index !== null &&
              citation.chunk_index !== undefined && (
                <span>
                  Chunk {citation.chunk_index}
                </span>
              )}

            <span>
              Similarity:{" "}
              {citation.score.toFixed(3)}
            </span>
          </div>

          {citation.content && (
            <p className="mt-3 text-sm leading-6 text-muted-foreground">
              {citation.content}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}