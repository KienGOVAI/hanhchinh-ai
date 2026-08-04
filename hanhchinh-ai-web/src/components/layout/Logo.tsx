import { Sparkles } from "lucide-react";

export default function Logo() {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow">
        <Sparkles className="h-5 w-5" />
      </div>

      <div>
        <h1 className="font-bold leading-none">
          Hành Chính AI
        </h1>

        <p className="text-xs text-muted-foreground">
          Văn phòng UBND
        </p>
      </div>
    </div>
  );
}