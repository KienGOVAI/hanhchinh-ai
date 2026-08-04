import { Outlet } from "react-router-dom";

import AppHeader from "@/components/layout/AppHeader";
import AppSidebar from "@/components/layout/AppSidebar";

import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar";

export default function DashboardLayout() {
  return (
    <SidebarProvider defaultOpen>
      <AppSidebar />

      <SidebarInset>
        <AppHeader />

        <main className="flex-1 bg-muted/30 p-6">
          <Outlet />
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}