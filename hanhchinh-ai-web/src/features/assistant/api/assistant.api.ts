import type {
  AssistantRequest,
  AssistantResponse,
} from "../types/assistant.types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

async function ask(
  request: AssistantRequest,
): Promise<AssistantResponse> {
  const response = await fetch(
    `${API_BASE_URL}/assistant/ask`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    },
  );

  if (!response.ok) {
    let message =
      "Không thể kết nối tới AI Assistant.";

    try {
      const data = await response.json();

      if (typeof data?.detail === "string") {
        message = data.detail;
      } else if (
        typeof data?.message === "string"
      ) {
        message = data.message;
      }
    } catch {
      // Giữ message mặc định.
    }

    throw new Error(message);
  }

  return response.json() as Promise<AssistantResponse>;
}

export const assistantService = {
  ask,
};