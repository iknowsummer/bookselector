"use client";

import { useRouter } from "next/navigation";
import { createBook } from "@/lib/api/books";
import BookForm, { BookFormData } from "@/components/BookForm";

export default function NewBookPage() {
  const router = useRouter();

  const handleSubmit = async (formData: BookFormData) => {
    await createBook({
      title: formData.title,
      author: formData.author || null,
      description: formData.description || null,
      note: formData.note || null,
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
