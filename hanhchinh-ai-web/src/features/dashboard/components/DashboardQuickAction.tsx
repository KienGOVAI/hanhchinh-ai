import type { LucideIcon } from "lucide-react";

import { ChevronRight } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";

interface DashboardQuickActionProps {
  title: string;
  description: string;
  icon: LucideIcon;
  onClick?: () => void;
}

export default function DashboardQuickAction({
  title,
  description,
  icon: Icon,
  onClick,
}: DashboardQuickActionProps) {
  return (
    <Card
      onClick={onClick}
      className="cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md"
    >
      <CardContent className="flex items-center justify-between p-5">
        <div className="flex items-center gap-4">
          <div className="rounded-xl bg-primary/10 p-3">
            <Icon className="h-6 w-6 text-primary" />
          </div>

          <div className="space-y-1">
            <h3 className="font-semibold leading-none">
              {title}
            </h3>

            <p className="text-sm text-muted-foreground">
              {description}
            </p>
          </div>
        </div>

        <ChevronRight className="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
      </CardContent>
    </Card>
  );
}