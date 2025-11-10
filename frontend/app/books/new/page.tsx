"use client";

import { useRouter } from "next/navigation";
import { createBook } from "@/lib/api/books";
import BookForm from "@/app/books/_components/BookForm";
import type { BookFormData } from "@/types/book";

export default function NewBookPage() {
  const router = useRouter();

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
      <BookForm
        onSubmit={handleSubmit}
        submitLabel="登録"
        cancelHref="/books"
      />
    </div>
  );
}
