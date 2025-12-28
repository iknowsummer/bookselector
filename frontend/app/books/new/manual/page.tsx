"use client";

import { useState, Suspense } from "react";
import { createBook } from "@/lib/api/books";
import { formDataToBookCreate } from "@/lib/api/bookTransformers";
import BookForm from "@/app/books/_components/BookForm";
import type { BookFormData } from "@/types/book";
import { BookParamReader } from "./_components/BookParamReader";

export default function ManualEntryPage() {
  const [initialData, setInitialData] = useState<BookFormData | undefined>(undefined);

  const handleParamsRead = (data: BookFormData) => {
    setInitialData(data);
  };

  const handleSubmit = async (formData: BookFormData) => {
    await createBook(formDataToBookCreate(formData));
  };

  return (
    <div className="container">
      <Suspense fallback={null}>
        <BookParamReader onParamsRead={handleParamsRead} />
      </Suspense>
      <h2>書籍登録</h2>
      <BookForm
        initialData={initialData}
        onSubmit={handleSubmit}
        submitLabel="登録"
      />
    </div>
  );
}
