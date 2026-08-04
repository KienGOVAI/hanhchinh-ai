interface ProviderSelectProps {
  value: string;
  onChange: (value: string) => void;
}

const providers = [
  {
    value: "ollama",
    label: "Ollama (Local)",
  },
  {
    value: "gemini",
    label: "Google Gemini",
  },
  {
    value: "openai",
    label: "OpenAI GPT",
  },
];

export default function ProviderSelect({
  value,
  onChange,
}: ProviderSelectProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">
        AI Provider
      </label>

      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="
          flex
          h-10
          w-full
          rounded-md
          border
          border-input
          bg-background
          px-3
          py-2
          text-sm
          ring-offset-background
          focus:outline-none
          focus:ring-2
          focus:ring-ring
        "
      >
        {providers.map((provider) => (
          <option
            key={provider.value}
            value={provider.value}
          >
            {provider.label}
          </option>
        ))}
      </select>
    </div>
  );
}