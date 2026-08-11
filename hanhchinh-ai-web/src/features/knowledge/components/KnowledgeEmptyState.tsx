import {
  BookOpen,
} from "lucide-react";

export default function KnowledgeEmptyState() {
  return (
    <div className="flex min-h-[240px] items-center justify-center rounded-xl border border-dashed">
      <div className="space-y-3 text-center">
        <BookOpen className="mx-auto h-10 w-10 text-muted-foreground" />

        <h3 className="font-medium">
          Chưa có kết quả
        </h3>

        <p className="max-w-md text-sm text-muted-foreground">
          Nhập nội dung cần tìm kiếm trong
          Knowledge Base rồi thực hiện tra cứu.
        </p>
      </div>
    </div>
  );
}