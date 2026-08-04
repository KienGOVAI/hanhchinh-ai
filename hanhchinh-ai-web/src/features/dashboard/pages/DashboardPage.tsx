import DashboardHero from "../components/DashboardHero";
import DashboardStats from "../components/DashboardStats";
import DashboardQuickActions from "../components/DashboardQuickActions";
import DashboardRecentActivities from "../components/DashboardRecentActivities";

export default function DashboardPage() {
  return (
    <main className="space-y-8">
      <DashboardHero />

      <DashboardStats />

      <div className="grid gap-8 xl:grid-cols-5">
        <section className="xl:col-span-2">
          <DashboardQuickActions />
        </section>

        <section className="xl:col-span-3">
          <DashboardRecentActivities />
        </section>
      </div>
    </main>
  );
}