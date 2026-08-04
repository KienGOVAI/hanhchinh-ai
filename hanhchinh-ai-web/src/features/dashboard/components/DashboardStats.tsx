import DashboardStatCard from "./DashboardStatCard";
import { dashboardStats } from "../data/dashboard.mock";

export default function DashboardStats() {
  return (
    <section className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
      {dashboardStats.map((stat) => (
        <DashboardStatCard
          key={stat.title}
          title={stat.title}
          value={stat.value}
          description={stat.description}
          icon={stat.icon}
        />
      ))}
    </section>
  );
}