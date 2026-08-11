import { useState } from "react";

import {
  AlertCircle,
  Bot,
  Loader2,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import AssistantInput from "../components/AssistantInput";
import AssistantMessage from "../components/AssistantMessage";
import { useAssistant } from "../hooks/useAssistant";

import type {
  AssistantResponse,
} from "../types/assistant.types";

export default function AssistantPage() {
  const [question, setQuestion] =
    useState("");

  const [result, setResult] =
    useState<AssistantResponse | null>(
      null,
    );

  const assistantMutation =
    useAssistant();

  const handleAsk = () => {
    const value = question.trim();

    if (!value) {
      return;
    }

    setResult(null);

    assistantMutation.mutate(
      {
        question: value,
      },
      {
        onSuccess: (data) => {
          setResult(data);
        },
      },
    );
  };

  const isLoading =
    assistantMutation.isPending;

  const error =
    assistantMutation.error;

  return (
    <div className="space-y-6">
      {/* ================================================= */}
      {/* HEADER */}
      {/* ================================================= */}

      <div>
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10">
            <Bot className="h-6 w-6 text-primary" />
          </div>

          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              Trợ lý Hành Chính AI
            </h1>

            <p className="mt-1 text-muted-foreground">
              Hỏi đáp và tra cứu thông tin
              dựa trên Knowledge Base.
            </p>
          </div>
        </div>
      </div>

      {/* ================================================= */}
      {/* INPUT */}
      {/* ================================================= */}

      <Card>
        <CardHeader>
          <CardTitle>
            Đặt câu hỏi
          </CardTitle>
        </CardHeader>

        <CardContent>
          <AssistantInput
            value={question}
            loading={isLoading}
            onChange={setQuestion}
            onAsk={handleAsk}
          />

          <p className="mt-3 text-xs text-muted-foreground">
            Assistant sẽ sử dụng Knowledge Base
            và các nguồn trích dẫn liên quan
            để xây dựng câu trả lời.
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
              Không thể xử lý câu hỏi
            </h3>

            <p className="mt-1 text-sm text-red-600">
              {error instanceof Error
                ? error.message
                : "Đã xảy ra lỗi khi gọi AI Assistant."}
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
              Hành Chính AI đang phân tích
              câu hỏi và tra cứu Knowledge Base...
            </p>
          </div>
        </div>
      )}

      {/* ================================================= */}
      {/* RESULT */}
      {/* ================================================= */}

      {!isLoading &&
        result && (
          <AssistantMessage
            response={result}
          />
        )}

      {/* ================================================= */}
      {/* INITIAL STATE */}
      {/* ================================================= */}

      {!isLoading &&
        !result &&
        !error && (
          <div className="flex min-h-[220px] items-center justify-center rounded-xl border border-dashed">
            <div className="space-y-3 text-center">
              <Bot className="mx-auto h-10 w-10 text-muted-foreground" />

              <div>
                <h3 className="font-semibold">
                  Sẵn sàng hỗ trợ
                </h3>

                <p className="mt-1 text-sm text-muted-foreground">
                  Nhập câu hỏi để bắt đầu
                  tra cứu với Hành Chính AI.
                </p>
              </div>
            </div>
          </div>
        )}
    </div>
  );
}