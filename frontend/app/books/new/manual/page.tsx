"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { createBook } from "@/lib/api/books";
import { formDataToBookCreate } from "@/lib/api/bookTransformers";
import BookForm from "@/app/books/_components/BookForm";
import type { BookFormData } from "@/types/book";

export default function ManualEntryPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // URLパラメータから書籍情報を取得
  const initialData: BookFormData = {
    title: searchParams.get("title") || "",
    author: searchParams.get("author") || "",
    description: searchParams.get("description") || "",
    isbn: searchParams.get("isbn") || "",
    image_url: searchParams.get("image_url") || "",
    note: "",
  };

  const handleSubmit = async (formData: BookFormData) => {
    await createBook(formDataToBookCreate(formData));
    router.push("/books");
  };

  return (
    <div className="container">
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
