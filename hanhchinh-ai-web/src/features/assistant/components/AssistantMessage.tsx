import {
  Bot,
  BookOpen,
} from "lucide-react";

import {
  Card,
  CardContent,
} from "@/components/ui/card";

import AssistantCitation from "./AssistantCitation";

import type {
  AssistantResponse,
} from "../types/assistant.types";

interface AssistantMessageProps {
  response: AssistantResponse;
}

export default function AssistantMessage({
  response,
}: AssistantMessageProps) {
  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary/10">
              <Bot className="h-5 w-5 text-primary" />
            </div>

            <div className="min-w-0 flex-1">
              <h2 className="font-semibold">
                Trợ lý Hành Chính AI
              </h2>

              <div className="mt-3 whitespace-pre-wrap text-sm leading-7">
                {response.answer}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {response.citations.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-primary" />

            <h3 className="font-semibold">
              Nguồn tham khảo
            </h3>
          </div>

          <div className="space-y-3">
            {response.citations.map(
              (citation, index) => (
                <AssistantCitation
                  key={citation.citation_id}
                  citation={citation}
                  index={index + 1}
                />
              ),
            )}
          </div>
        </div>
      )}
    </div>
  );
}