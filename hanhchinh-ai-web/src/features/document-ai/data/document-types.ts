import {
  Bell,
  BookOpen,
  ClipboardList,
  FileCheck,
  FileText,
  FileWarning,
  Mail,
  ScrollText,
} from "lucide-react";

import type { DocumentType } from "../types/document.types";

export const documentTypes: DocumentType[] = [
  {
    id: "cong-van",
    name: "Công văn",
    description: "Soạn công văn hành chính",
    icon: FileText,
  },
  {
    id: "quyet-dinh",
    name: "Quyết định",
    description: "Soạn quyết định hành chính",
    icon: FileCheck,
  },
  {
    id: "thong-bao",
    name: "Thông báo",
    description: "Soạn thông báo",
    icon: Bell,
  },
  {
    id: "ke-hoach",
    name: "Kế hoạch",
    description: "Soạn kế hoạch công tác",
    icon: ClipboardList,
  },
  {
    id: "bao-cao",
    name: "Báo cáo",
    description: "Soạn báo cáo",
    icon: BookOpen,
  },
  {
    id: "to-trinh",
    name: "Tờ trình",
    description: "Soạn tờ trình",
    icon: ScrollText,
  },
  {
    id: "giay-moi",
    name: "Giấy mời",
    description: "Soạn giấy mời",
    icon: Mail,
  },
  {
    id: "bien-ban",
    name: "Biên bản",
    description: "Soạn biên bản",
    icon: FileWarning,
  },
];