import { createBrowserRouter } from "react-router-dom";

import DashboardLayout from "@/app/layouts/DashboardLayout";
import DashboardPage from "@/features/dashboard/pages/DashboardPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <DashboardLayout />,
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
    ],
  },
]);