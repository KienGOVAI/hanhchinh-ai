import DashboardQuickAction from "./DashboardQuickAction";
import { quickActions } from "../data/dashboard.mock";

export default function DashboardQuickActions() {
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold">
          Thao tác nhanh
        </h2>

        <p className="text-sm text-muted-foreground">
          Truy cập nhanh các chức năng thường sử dụng.
        </p>
      </div>

      <div className="space-y-3">
        {quickActions.map((action) => (
          <DashboardQuickAction
            key={action.title}
            title={action.title}
            description={action.description}
            icon={action.icon}
            onClick={() => {
              console.log(`Đã chọn: ${action.title}`);
            }}
          />
        ))}
      </div>
    </section>
  );
}