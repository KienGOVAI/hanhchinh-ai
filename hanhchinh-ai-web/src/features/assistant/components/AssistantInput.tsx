import {
  Loader2,
  Send,
} from "lucide-react";

import {
  Button,
} from "@/components/ui/button";

import {
  Textarea,
} from "@/components/ui/textarea";

interface AssistantInputProps {
  value: string;
  loading: boolean;
  onChange: (value: string) => void;
  onAsk: () => void;
}

export default function AssistantInput({
  value,
  loading,
  onChange,
  onAsk,
}: AssistantInputProps) {
  const disabled =
    loading || !value.trim();

  return (
    <div className="space-y-3">
      <Textarea
        value={value}
        onChange={(event) =>
          onChange(event.target.value)
        }
        placeholder="Nhập câu hỏi cho Hành Chính AI..."
        disabled={loading}
        rows={5}
        onKeyDown={(event) => {
          if (
            event.key === "Enter" &&
            (event.ctrlKey || event.metaKey)
          ) {
            event.preventDefault();

            if (!disabled) {
              onAsk();
            }
          }
        }}
      />

      <div className="flex items-center justify-between gap-3">
        <p className="text-xs text-muted-foreground">
          Nhấn Ctrl + Enter để gửi câu hỏi.
        </p>

        <Button
          type="button"
          onClick={onAsk}
          disabled={disabled}
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Đang xử lý...
            </>
          ) : (
            <>
              <Send className="mr-2 h-4 w-4" />
              Hỏi AI
            </>
          )}
        </Button>
      </div>
    </div>
  );
}