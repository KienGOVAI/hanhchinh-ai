import { cn } from "@/lib/utils";

import { Card, CardContent } from "@/components/ui/card";

import { documentTypes } from "../data/document-types";

interface DocumentTypeSelectProps {
  value: string;
  onChange: (value: string) => void;
}

export default function DocumentTypeSelect({
  value,
  onChange,
}: DocumentTypeSelectProps) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">
          Loại văn bản
        </h2>

        <p className="text-sm text-muted-foreground">
          Chọn loại văn bản cần AI hỗ trợ soạn thảo.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {documentTypes.map((type) => {
          const Icon = type.icon;
          const active = value === type.id;

          return (
            <Card
              key={type.id}
              onClick={() => onChange(type.id)}
              className={cn(
                "cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md",
                active && "border-primary bg-primary/5"
              )}
            >
              <CardContent className="flex flex-col gap-4 p-5">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                  <Icon className="h-6 w-6 text-primary" />
                </div>

                <div>
                  <h3 className="font-semibold">
                    {type.name}
                  </h3>

                  <p className="mt-1 text-sm text-muted-foreground">
                    {type.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}