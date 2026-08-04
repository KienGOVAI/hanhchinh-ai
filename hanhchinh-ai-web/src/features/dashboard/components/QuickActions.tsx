import DashboardQuickAction from "./DashboardQuickAction";
import { quickActions } from "../data/dashboard.mock";

export default function DashboardQuickActions() {
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold tracking-tight">
          Thao tác nhanh
        </h2>

        <p className="text-sm text-muted-foreground">
          Truy cập nhanh các chức năng thường dùng.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {quickActions.map((action) => (
          <DashboardQuickAction
            key={action.title}
            title={action.title}
            description={action.description}
            icon={action.icon}
            onClick={() => {
              console.log(`${action.title} clicked`);
            }}
          />
        ))}
      </div>
    </section>
  );
}