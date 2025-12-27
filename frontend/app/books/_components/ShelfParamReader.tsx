"use client";

import { useEffect } from "react";
import { useSearchParams } from "next/navigation";

interface ShelfParamReaderProps {
  onShelfIdRead: (shelfId: number | null | "unassigned") => void;
}

export function ShelfParamReader({ onShelfIdRead }: ShelfParamReaderProps) {
  const searchParams = useSearchParams();

  useEffect(() => {
    const shelfParam = searchParams.get("shelf");
    if (shelfParam === "unassigned") {
      onShelfIdRead("unassigned");
    } else if (shelfParam) {
      const shelfId = parseInt(shelfParam, 10);
      if (!isNaN(shelfId)) {
        onShelfIdRead(shelfId);
      }
    }
  }, [searchParams, onShelfIdRead]);

  return null; // このコンポーネントはUIを持たない
}
