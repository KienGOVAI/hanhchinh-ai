import { Textarea } from "@/components/ui/textarea";

interface PromptEditorProps {
  value: string;
  onChange: (value: string) => void;
}

export default function PromptEditor({
  value,
  onChange,
}: PromptEditorProps) {
  return (
    <div className="space-y-3">
      <div>
        <h2 className="text-lg font-semibold">
          Mô tả yêu cầu
        </h2>

        <p className="text-sm text-muted-foreground">
          Nhập yêu cầu để AI tạo văn bản theo đúng nội dung mong muốn.
        </p>
      </div>

      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={`Ví dụ:

Soạn công văn gửi Phòng Nội vụ về việc báo cáo tình hình chuyển đổi số của UBND xã Yên Minh trong 6 tháng đầu năm 2026.

Yêu cầu:
- Văn phong hành chính.
- Đúng thể thức văn bản.
- Có căn cứ pháp lý.
- Có nơi nhận.
- Có phần ký tên.
`}
        className="min-h-[260px] resize-none text-sm leading-7"
      />
    </div>
  );
}