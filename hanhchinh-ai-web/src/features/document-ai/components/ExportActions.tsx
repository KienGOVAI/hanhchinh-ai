import {
  Copy,
  Download,
  FileText,
} from "lucide-react";

import { Button } from "@/components/ui/button";

interface ExportActionsProps {
  disabled?: boolean;
  onCopy?: () => void;
  onExportWord?: () => void;
  onExportPdf?: () => void;
}

export default function ExportActions({
  disabled = true,
  onCopy,
  onExportWord,
  onExportPdf,
}: ExportActionsProps) {
  return (
    <div className="flex flex-wrap justify-end gap-3">
      <Button
        variant="outline"
        disabled={disabled}
        onClick={onCopy}
      >
        <Copy className="mr-2 h-4 w-4" />
        Sao chép
      </Button>

      <Button
        variant="outline"
        disabled={disabled}
        onClick={onExportWord}
      >
        <FileText className="mr-2 h-4 w-4" />
        Xuất Word
      </Button>

      <Button
        disabled={disabled}
        onClick={onExportPdf}
      >
        <Download className="mr-2 h-4 w-4" />
        Xuất PDF
      </Button>
    </div>
  );
}