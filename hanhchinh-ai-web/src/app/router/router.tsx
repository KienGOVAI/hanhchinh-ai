import { createBrowserRouter } from "react-router-dom";

import DashboardLayout from "@/app/layouts/DashboardLayout";

import DashboardPage from "@/features/dashboard/pages/DashboardPage";

import KnowledgePage from "@/features/knowledge/pages/KnowledgePage";

import AssistantPage from "@/features/assistant/pages/AssistantPage";


export const router = createBrowserRouter([
  {
    path: "/",

    element: <DashboardLayout />,

    children: [
      {
        index: true,

        element: <DashboardPage />,
      },

      {
        path: "knowledge",

        element: <KnowledgePage />,
      },

      {
        path: "assistant",

        element: <AssistantPage />,
      },
    ],
  },
]);