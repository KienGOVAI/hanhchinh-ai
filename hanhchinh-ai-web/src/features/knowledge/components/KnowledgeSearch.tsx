import {
  Search,
} from "lucide-react";

import {
  Button,
} from "@/components/ui/button";

import {
  Input,
} from "@/components/ui/input";

interface KnowledgeSearchProps {
  value: string;
  loading?: boolean;
  disabled?: boolean;
  onChange: (
    value: string
  ) => void;
  onSearch: () => void;
}

export default function KnowledgeSearch({
  value,
  loading = false,
  disabled = false,
  onChange,
  onSearch,
}: KnowledgeSearchProps) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row">
      <Input
        value={value}
        onChange={(event) =>
          onChange(
            event.target.value
          )
        }
        onKeyDown={(event) => {
          if (
            event.key === "Enter" &&
            !loading &&
            !disabled
          ) {
            onSearch();
          }
        }}
        placeholder="Nhập nội dung cần tra cứu..."
        disabled={loading || disabled}
        className="h-11"
      />

      <Button
        type="button"
        onClick={onSearch}
        disabled={
          loading ||
          disabled ||
          !value.trim()
        }
        className="h-11 min-w-[130px]"
      >
        <Search className="mr-2 h-4 w-4" />

        {loading
          ? "Đang tìm..."
          : "Tra cứu"}
      </Button>
    </div>
  );
}