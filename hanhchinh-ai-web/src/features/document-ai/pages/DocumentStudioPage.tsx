import { useEffect, useState } from "react";

import AIResponse from "../components/AIResponse";
import DocumentTitleInput from "../components/DocumentTitleInput";
import DocumentTypeSelect from "../components/DocumentTypeSelect";
import ExportActions from "../components/ExportActions";
import GenerateButton from "../components/GenerateButton";
import PromptEditor from "../components/PromptEditor";
import ProviderSelect from "../components/ProviderSelect";

import { DEFAULT_PROVIDER } from "../constants/ai-provider";
import { useGenerateDocument } from "../hooks/useGenerateDocument";
import type { AIProvider } from "../types/document.types";
import { getErrorMessage } from "../utils/error-message";

export default function DocumentStudioPage() {
  const [provider, setProvider] =
    useState<AIProvider>(DEFAULT_PROVIDER as AIProvider);

  const [documentType, setDocumentType] =
    useState("");

  const [title, setTitle] = useState("");

  const [prompt, setPrompt] = useState("");

  const [errorMessage, setErrorMessage] =
    useState("");

  const generateMutation =
    useGenerateDocument();

  const isLoading =
    generateMutation.isPending;

  useEffect(() => {
    if (!generateMutation.error) {
      setErrorMessage("");
      return;
    }

    setErrorMessage(
      getErrorMessage(
        generateMutation.error
      )
    );
  }, [generateMutation.error]);

  const handleGenerate = () => {
    setErrorMessage("");

    generateMutation.mutate({
      provider,
      type: documentType,
      title,
      prompt,
    });
  };

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      {/* Header */}

      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          AI Document Studio
        </h1>

        <p className="mt-2 text-muted-foreground">
          Soạn thảo văn bản hành chính bằng trí tuệ nhân tạo.
        </p>
      </div>

      {/* Form */}

      <fieldset
        disabled={isLoading}
        className="space-y-8 disabled:opacity-70"
      >
        <ProviderSelect
          value={provider}
          onChange={(value) =>
            setProvider(
              value as AIProvider
            )
          }
        />

        <DocumentTypeSelect
          value={documentType}
          onChange={setDocumentType}
        />

        <DocumentTitleInput
          value={title}
          onChange={setTitle}
        />

        <PromptEditor
          value={prompt}
          onChange={setPrompt}
        />

        <GenerateButton
          loading={isLoading}
          disabled={
            isLoading ||
            !provider ||
            !documentType ||
            !title ||
            !prompt
          }
          onClick={handleGenerate}
        />
      </fieldset>

      {/* Error */}

      {errorMessage && (
        <div className="rounded-lg border border-red-300 bg-red-50 p-4">
          <h3 className="font-semibold text-red-700">
            Không thể tạo văn bản
          </h3>

          <p className="mt-1 text-sm text-red-600">
            {errorMessage}
          </p>
        </div>
      )}

      {/* AI Result */}

      <AIResponse
        loading={isLoading}
        content={
          generateMutation.data?.content ??
          ""
        }
      />

      {/* Export */}

      <ExportActions
        disabled={
          !generateMutation.data?.content
        }
      />
    </div>
  );
}