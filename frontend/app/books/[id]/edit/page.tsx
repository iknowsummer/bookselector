"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { fetchBook, updateBook } from "@/lib/api/books";
import { bookToFormData, formDataToBookUpdate } from "@/lib/api/bookTransformers";
import BookForm from "@/app/books/_components/BookForm";
import DeleteButton from "@/app/books/_components/DeleteButton";
import Link from "next/link";
import type { Book, BookFormData } from "@/types/book";

export default function EditBookPage() {
  const router = useRouter();
  const params = useParams();
  const [book, setBook] = useState<Book | null>(null);
  const [initialData, setInitialData] = useState<BookFormData | undefined>();
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const getData = async () => {
      try {
        const id = Number(params.id);
        const fetchedBook = await fetchBook(id);
        setBook(fetchedBook);
        setInitialData(bookToFormData(fetchedBook));
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
    await updateBook(id, formDataToBookUpdate(formData));
    router.push(`/books/${id}`);
  };

  if (error && !initialData) {
    return (
      <div className="container">
        <div className="error">エラー: {error}</div>
        <Link href="/books">
          <button className="button">書籍一覧に戻る</button>
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
      {book && (
        <div className="delete-section">
          <DeleteButton
            bookId={book.id}
            bookTitle={book.title}
            onSuccess={() => router.push("/books")}
          />
        </div>
      )}
    </div>
  );
}
