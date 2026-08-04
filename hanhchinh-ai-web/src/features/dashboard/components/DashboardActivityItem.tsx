import { Clock3 } from "lucide-react";

interface DashboardActivityItemProps {
  title: string;
  description: string;
  time: string;
}

export default function DashboardActivityItem({
  title,
  description,
  time,
}: DashboardActivityItemProps) {
  return (
    <div className="flex items-start justify-between rounded-xl border p-4 transition-colors hover:bg-muted/40">
      <div className="space-y-1">
        <h3 className="font-medium">
          {title}
        </h3>

        <p className="text-sm text-muted-foreground">
          {description}
        </p>
      </div>

      <div className="flex items-center gap-1 whitespace-nowrap text-sm text-muted-foreground">
        <Clock3 className="h-4 w-4" />
        <span>{time}</span>
      </div>
    </div>
  );
}