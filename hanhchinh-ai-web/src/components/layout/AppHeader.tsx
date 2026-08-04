import {
  Bell,
  Search,
  UserCircle2,
} from "lucide-react";

import { SidebarTrigger } from "@/components/ui/sidebar";

export default function AppHeader() {
  return (
    <header className="flex h-16 items-center justify-between border-b bg-background px-6">

      <div className="flex items-center gap-4">

        <SidebarTrigger />

        <div className="relative hidden md:block">

          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            size={18}
          />

          <input
            type="text"
            placeholder="Tìm kiếm..."
            className="h-10 w-80 rounded-lg border bg-muted/40 pl-10 pr-4 outline-none transition focus:border-primary"
          />

        </div>

      </div>

      <div className="flex items-center gap-5">

        <button className="rounded-lg p-2 hover:bg-muted transition">

          <Bell size={20} />

        </button>

        <div className="flex items-center gap-3">

          <UserCircle2
            size={36}
            className="text-primary"
          />

          <div className="hidden md:block">

            <p className="text-sm font-semibold">
              Nguyễn Trung Kiên
            </p>

            <p className="text-xs text-muted-foreground">
              Chuyên viên CNTT
            </p>

          </div>

        </div>

      </div>

    </header>
  );
}