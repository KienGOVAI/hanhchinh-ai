import { NavLink } from "react-router-dom";

import {
  BookOpen,
  Bot,
  FileText,
  FolderOpen,
  LayoutDashboard,
  Settings,
  Sparkles,
} from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

const menus = [
  {
    title: "Dashboard",
    url: "/",
    icon: LayoutDashboard,
  },
  {
    title: "Soạn văn bản AI",
    url: "/documents",
    icon: FileText,
  },
  {
    title: "Kho tri thức",
    url: "/knowledge",
    icon: BookOpen,
  },
  {
    title: "Trợ lý AI",
    url: "/assistant",
    icon: Bot,
  },
  {
    title: "Mẫu văn bản",
    url: "/templates",
    icon: FolderOpen,
  },
  {
    title: "Cài đặt",
    url: "/settings",
    icon: Settings,
  },
];

export default function AppSidebar() {
  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="border-b">
        <div className="flex items-center gap-3 px-2 py-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <Sparkles className="h-5 w-5" />
          </div>

          <div className="flex flex-col">
            <span className="font-bold">
              Hành Chính AI
            </span>

            <span className="text-xs text-muted-foreground">
              Phiên bản 1.0
            </span>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>
            ĐIỀU HƯỚNG
          </SidebarGroupLabel>

          <SidebarGroupContent>
            <SidebarMenu>
              {menus.map((menu) => (
                <SidebarMenuItem
                  key={menu.title}
                >
                  <SidebarMenuButton
                    tooltip={menu.title}
                    render={
                      <NavLink
                        to={menu.url}
                        className={({ isActive }) =>
                          isActive
                            ? "font-semibold"
                            : ""
                        }
                      />
                    }
                  >
                    <menu.icon />
                    <span>{menu.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t">
        <div className="px-3 py-2">
          <p className="text-xs text-muted-foreground">
            © 2026
          </p>

          <p className="text-sm font-medium">
            Hành Chính AI
          </p>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}