"use client";

import { useEffect } from "react";
import { useSearchParams } from "next/navigation";
import type { BookFormData } from "@/types/book";

interface BookParamReaderProps {
  onParamsRead: (data: BookFormData) => void;
}

export function BookParamReader({ onParamsRead }: BookParamReaderProps) {
  const searchParams = useSearchParams();

  useEffect(() => {
    const initialData: BookFormData = {
      title: searchParams.get("title") || "",
      author: searchParams.get("author") || "",
      description: searchParams.get("description") || "",
      isbn: searchParams.get("isbn") || "",
      image_url: searchParams.get("image_url") || "",
      note: "",
    };
    onParamsRead(initialData);
  }, [searchParams, onParamsRead]);

  return null; // このコンポーネントはUIを持たない
}
