"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createBook } from "@/lib/api/books";
import BookForm from "@/app/books/_components/BookForm";
import IsbnInputForm from "@/app/books/_components/IsbnInputForm";
import type { BookFormData } from "@/types/book";

type Mode = "isbn-input" | "full-form";

export default function NewBookPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("isbn-input");
  const [initialData, setInitialData] = useState<BookFormData>({
    title: "",
    author: "",
    description: "",
    isbn: "",
    image_url: "",
    note: "",
  });

  const handleIsbnSuccess = (bookData: BookFormData) => {
    setInitialData(bookData);
    setMode("full-form");
  };

  const handleManualEntry = (isbn?: string) => {
    setInitialData({
      title: "",
      author: "",
      description: "",
      isbn: isbn || "",
      image_url: "",
      note: "",
    });
    setMode("full-form");
  };

  const handleCancel = () => {
    router.push("/books");
  };

  const handleBackToIsbnInput = () => {
    setMode("isbn-input");
  };

  const handleSubmit = async (formData: BookFormData) => {
    await createBook({
      title: formData.title,
      author: formData.author || null,
      description: formData.description || null,
      image_url: formData.image_url || null,
      isbn: formData.isbn || null,
      note: formData.note || null,
      status: "unread",
      created_at: new Date().toISOString(),
    });
    router.push("/books");
  };

  return (
    <div className="container">
      <h2>書籍登録</h2>

      {mode === "isbn-input" && (
        <IsbnInputForm
          onSuccess={handleIsbnSuccess}
          onManualEntry={handleManualEntry}
          onCancel={handleCancel}
        />
      )}

      {mode === "full-form" && (
        <BookForm
          initialData={initialData}
          onSubmit={handleSubmit}
          submitLabel="登録"
          cancelHref="/books"
          onBackToIsbnInput={handleBackToIsbnInput}
        />
      )}
    </div>
  );
}
