"use client";
import { useState, useEffect } from "react";
import type { Book } from "@/types/book";
import { fetchLatestBooks } from "@/lib/api/books";
import { BookList } from "@/app/books/_components/BookList";

type LatestBookListProps = {
  limit?: number;
};

export default function LatestBookList({ limit = 12 }: LatestBookListProps) {
  const [books, setBooks] = useState<Book[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const loadLatestBooks = async () => {
      setIsLoading(true);
      setError("");
      try {
        const data = await fetchLatestBooks(limit);
        setBooks(data);
      } catch (err) {
        setBooks([]);
        setError(`書籍情報の取得に失敗しました: ${err}`);
      } finally {
        setIsLoading(false);
      }
    };

    loadLatestBooks();
  }, [limit]);

  if (isLoading) {
    return <section>読み込み中...</section>;
  }

  if (error) {
    return <section>{error}</section>;
  }

  return (
    <section>
      <BookList books={books} />
    </section>
  );
}
