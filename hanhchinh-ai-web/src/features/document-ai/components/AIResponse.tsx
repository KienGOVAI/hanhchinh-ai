import { Bot } from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface AIResponseProps {
  content: string;
  loading?: boolean;
}

export default function AIResponse({
  content,
  loading = false,
}: AIResponseProps) {
  return (
    <Card className="min-h-[350px]">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-primary" />
          Kết quả AI
        </CardTitle>
      </CardHeader>

      <CardContent>
        {loading ? (
          <div className="space-y-4 animate-pulse">

            <div className="h-5 w-40 rounded bg-muted" />

            <div className="h-4 w-full rounded bg-muted" />

            <div className="h-4 w-full rounded bg-muted" />

            <div className="h-4 w-5/6 rounded bg-muted" />

            <div className="h-4 w-full rounded bg-muted" />

            <div className="h-4 w-3/4 rounded bg-muted" />

            <div className="h-4 w-2/3 rounded bg-muted" />

          </div>
        ) : content ? (
          <div className="whitespace-pre-wrap text-sm leading-7">
            {content}
          </div>
        ) : (
          <div className="flex h-[220px] items-center justify-center rounded-lg border border-dashed">
            <div className="space-y-2 text-center">
              <Bot className="mx-auto h-10 w-10 text-muted-foreground" />

              <h3 className="font-medium">
                Chưa có nội dung
              </h3>

              <p className="max-w-md text-sm text-muted-foreground">
                Chọn loại văn bản, nhập yêu cầu rồi nhấn{" "}
                <strong>"Tạo bằng AI"</strong>.
                <br />
                Kết quả sẽ hiển thị tại đây.
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}