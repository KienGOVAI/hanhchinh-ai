import {
  Bot,
  Clock3,
  FileText,
  Scale,
  type LucideIcon,
} from "lucide-react";

export interface DashboardStat {
  title: string;
  value: string;
  description: string;
  icon: LucideIcon;
}

export interface DashboardQuickAction {
  title: string;
  description: string;
  icon: LucideIcon;
}

export interface DashboardActivity {
  id: number;
  title: string;
  description: string;
  time: string;
}

export const dashboardStats: DashboardStat[] = [
  {
    title: "Văn bản đã tạo",
    value: "128",
    description: "+12 trong hôm nay",
    icon: FileText,
  },
  {
    title: "Lượt AI hỗ trợ",
    value: "3.482",
    description: "Tăng 18%",
    icon: Bot,
  },
  {
    title: "Tra cứu pháp luật",
    value: "257",
    description: "Trong tháng",
    icon: Scale,
  },
  {
    title: "Tiết kiệm thời gian",
    value: "146h",
    description: "Ước tính",
    icon: Clock3,
  },
];

export const quickActions: DashboardQuickAction[] = [
  {
    title: "Soạn công văn",
    description: "Tạo công văn bằng AI",
    icon: FileText,
  },
  {
    title: "Tra cứu pháp luật",
    description: "Tìm văn bản pháp luật",
    icon: Scale,
  },
  {
    title: "Hỏi AI",
    description: "Trao đổi với trợ lý AI",
    icon: Bot,
  },
];

export const recentActivities: DashboardActivity[] = [
  {
    id: 1,
    title: "Đã tạo Công văn số 15",
    description: "Hoàn thành lúc 09:15",
    time: "10 phút trước",
  },
  {
    id: 2,
    title: "AI trả lời câu hỏi",
    description: "Tra cứu Nghị định mới",
    time: "30 phút trước",
  },
  {
    id: 3,
    title: "Xuất văn bản Word",
    description: "Đã tải xuống thành công",
    time: "1 giờ trước",
  },
];