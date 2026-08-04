import { FileText } from "lucide-react";

import { Input } from "@/components/ui/input";

interface DocumentTitleInputProps {
  value: string;
  onChange: (value: string) => void;
}

export default function DocumentTitleInput({
  value,
  onChange,
}: DocumentTitleInputProps) {
  return (
    <div className="space-y-3">
      <div>
        <h2 className="text-lg font-semibold">
          Tiêu đề văn bản
        </h2>

        <p className="text-sm text-muted-foreground">
          Nhập tiêu đề hoặc chủ đề chính của văn bản.
        </p>
      </div>

      <div className="relative">
        <FileText className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />

        <Input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Ví dụ: Báo cáo công tác chuyển đổi số 6 tháng đầu năm 2026"
          className="h-12 pl-11"
        />
      </div>
    </div>
  );
}