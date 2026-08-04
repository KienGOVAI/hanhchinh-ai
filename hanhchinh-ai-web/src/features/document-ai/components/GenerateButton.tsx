import { Loader2, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";

interface GenerateButtonProps {
  loading?: boolean;
  disabled?: boolean;
  onClick: () => void;
}

export default function GenerateButton({
  loading = false,
  disabled = false,
  onClick,
}: GenerateButtonProps) {
  return (
    <div className="flex justify-end">
      <Button
        type="button"
        size="lg"
        onClick={onClick}
        disabled={loading || disabled}
        className="min-w-[220px] gap-2"
      >
        {loading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            AI đang soạn văn bản...
          </>
        ) : (
          <>
            <Sparkles className="h-4 w-4" />
            Tạo bằng AI
          </>
        )}
      </Button>
    </div>
  );
}