import type { LucideIcon } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";

interface DashboardStatCardProps {
  title: string;
  value: string | number;
  description: string;
  icon: LucideIcon;
}

export default function DashboardStatCard({
  title,
  value,
  description,
  icon: Icon,
}: DashboardStatCardProps) {
  return (
    <Card className="transition-all hover:-translate-y-1 hover:shadow-md">
      <CardContent className="flex items-start justify-between p-6">
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">
            {title}
          </p>

          <h3 className="text-3xl font-bold tracking-tight">
            {value}
          </h3>

          <p className="text-sm text-muted-foreground">
            {description}
          </p>
        </div>

        <div className="rounded-xl bg-primary/10 p-3">
          <Icon className="h-6 w-6 text-primary" />
        </div>
      </CardContent>
    </Card>
  );
}