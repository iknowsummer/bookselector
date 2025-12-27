"use client";

import { useState, Suspense } from "react";
import { useRouter } from "next/navigation";
import { createBook } from "@/lib/api/books";
import { formDataToBookCreate } from "@/lib/api/bookTransformers";
import BookForm from "@/app/books/_components/BookForm";
import type { BookFormData } from "@/types/book";
import { BookParamReader } from "./_components/BookParamReader";

export default function ManualEntryPage() {
  const router = useRouter();

  // URLパラメータから書籍情報を取得
  const [initialData, setInitialData] = useState<BookFormData>({
    title: "",
    author: "",
    description: "",
    isbn: "",
    image_url: "",
    note: "",
  });

  const handleParamsRead = (data: BookFormData) => {
    setInitialData(data);
  };

  const handleSubmit = async (formData: BookFormData) => {
    await createBook(formDataToBookCreate(formData));
    router.push("/books");
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
        cancelHref="/books/new"
      />
    </div>
  );
}
