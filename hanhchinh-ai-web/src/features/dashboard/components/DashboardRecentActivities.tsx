import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import DashboardActivityItem from "./DashboardActivityItem";
import { recentActivities } from "../data/dashboard.mock";

export default function DashboardRecentActivities() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Hoạt động gần đây</CardTitle>
      </CardHeader>

      <CardContent className="space-y-3">
        {recentActivities.map((activity) => (
          <DashboardActivityItem
            key={activity.id}
            title={activity.title}
            description={activity.description}
            time={activity.time}
          />
        ))}
      </CardContent>
    </Card>
  );
}