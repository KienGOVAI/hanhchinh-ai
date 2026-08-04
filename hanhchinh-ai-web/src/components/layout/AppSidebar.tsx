import { NavLink } from "react-router-dom";

import {
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
  SidebarRail,
} from "@/components/ui/sidebar";

interface MenuItem {
  title: string;
  url: string;
  icon: React.ElementType;
}

const menus: MenuItem[] = [
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
    <Sidebar
      variant="sidebar"
      collapsible="icon"
    >
      <SidebarHeader className="border-b">
        <div className="flex items-center gap-3 p-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <Sparkles className="h-5 w-5" />
          </div>

          <div className="overflow-hidden">
            <p className="truncate font-bold">
              Hành Chính AI
            </p>

            <p className="truncate text-xs text-muted-foreground">
              Văn phòng UBND
            </p>
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

              {menus.map((item) => (

                <SidebarMenuItem key={item.title}>

                  <SidebarMenuButton
                    tooltip={item.title}
                    render={
                      <NavLink
                        to={item.url}
                      />
                    }
                  >

                    <item.icon />

                    <span>
                      {item.title}
                    </span>

                  </SidebarMenuButton>

                </SidebarMenuItem>

              ))}

            </SidebarMenu>

          </SidebarGroupContent>

        </SidebarGroup>

      </SidebarContent>

      <SidebarFooter className="border-t">

        <div className="px-2 py-3">

          <div className="text-sm font-semibold">
            Hành Chính AI
          </div>

          <div className="text-xs text-muted-foreground">
            Phiên bản 1.0.0
          </div>

        </div>

      </SidebarFooter>

      <SidebarRail />

    </Sidebar>
  );
}