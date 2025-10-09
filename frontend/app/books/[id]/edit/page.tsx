"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { fetchBook, updateBook } from "@/lib/api/books";
import BookForm, { BookFormData } from "@/components/BookForm";
import Link from "next/link";

export default function EditBookPage() {
  const router = useRouter();
  const params = useParams();
  const [initialData, setInitialData] = useState<BookFormData | undefined>();
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const getData = async () => {
      try {
        const id = Number(params.id);
        const book = await fetchBook(id);
        setInitialData({
          title: book.title,
          author: book.author || "",
          description: book.description || "",
          note: book.note || "",
        });
      } catch (err) {
        setError(`書籍の取得に失敗しました: ${err}`);
      } finally {
        setIsLoading(false);
      }
    };
    getData();
  }, [params.id]);

  const handleSubmit = async (formData: BookFormData) => {
    const id = Number(params.id);
    await updateBook(id, {
      title: formData.title,
      author: formData.author || null,
      description: formData.description || null,
      note: formData.note || null,
    });
    router.push(`/books/${id}`);
  };

  if (error && !initialData) {
    return (
      <div className="container">
        <div className="error">エラー: {error}</div>
        <Link href="/books">
          <button>書籍一覧に戻る</button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container">
      <h2>書籍編集</h2>
      <BookForm
        initialData={initialData}
        onSubmit={handleSubmit}
        submitLabel="更新"
        cancelHref={`/books/${params.id}`}
        isLoading={isLoading}
      />
    </div>
  );
}
