export interface AIProvider {
  value: string;
  label: string;
  description: string;
  local: boolean;
}

export const AI_PROVIDERS: AIProvider[] = [
  {
    value: "ollama",
    label: "Ollama",
    description: "Mô hình AI chạy nội bộ trên máy chủ",
    local: true,
  },
  {
    value: "gemini",
    label: "Google Gemini",
    description: "Google Gemini API",
    local: false,
  },
  {
    value: "openai",
    label: "OpenAI GPT",
    description: "OpenAI GPT API",
    local: false,
  },
];

export const DEFAULT_PROVIDER = "ollama";

export function getProviderLabel(provider: string): string {
  const found = AI_PROVIDERS.find(
    (item) => item.value === provider
  );

  return found?.label ?? provider;
}

export function isLocalProvider(provider: string): boolean {
  return provider === "ollama";
}