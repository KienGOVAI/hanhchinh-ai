import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";

export default function DashboardHero() {
  return (
    <section className="relative overflow-hidden rounded-2xl border bg-gradient-to-r from-primary/10 via-background to-primary/5 p-8">
      <div className="absolute right-0 top-0 h-40 w-40 rounded-full bg-primary/10 blur-3xl" />

      <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 rounded-full border bg-background px-3 py-1 text-sm font-medium">
            <Sparkles className="h-4 w-4 text-primary" />
            Hành Chính AI
          </div>

          <h1 className="text-3xl font-bold tracking-tight">
            Xin chào 👋
          </h1>

          <p className="max-w-2xl text-muted-foreground">
            Chào mừng bạn quay trở lại. Từ đây bạn có thể tạo văn bản,
            quản lý hồ sơ, tra cứu pháp luật và sử dụng các tính năng AI
            dành cho cơ quan hành chính.
          </p>
        </div>

        <Button size="lg" className="gap-2 self-start lg:self-auto">
          Bắt đầu
          <ArrowRight className="h-4 w-4" />
        </Button>
      </div>
    </section>
  );
}